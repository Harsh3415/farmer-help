<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

function verifyFarmerSession() {
    global $db;

    $headers = getallheaders();
    $session_id = isset($headers['Authorization']) ? str_replace('Bearer ', '', $headers['Authorization']) : null;

    if (!$session_id) {
        sendJsonResponse(['error' => 'Authentication required'], 401);
    }

    try {
        $query = "SELECT farmer_id FROM user_sessions WHERE session_id = :session_id AND expires_at > NOW() AND is_active = 1";
        $stmt = $db->prepare($query);
        $stmt->bindParam(':session_id', $session_id);
        $stmt->execute();

        if ($stmt->rowCount() === 0) {
            sendJsonResponse(['error' => 'Invalid or expired session'], 401);
        }

        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        return $result['farmer_id'];

    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Authentication failed'], 500);
    }
}

switch ($request_method) {
    case 'GET':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'income':
                    getIncomeRecords($farmer_id);
                    break;
                case 'expense':
                    getExpenseRecords($farmer_id);
                    break;
                case 'yield':
                    getYieldRecords($farmer_id);
                    break;
                case 'summary':
                    getFinancialSummary($farmer_id);
                    break;
                default:
                    getAllRecords($farmer_id);
            }
        } else {
            getAllRecords($farmer_id);
        }
        break;
    case 'POST':
        $farmer_id = verifyFarmerSession();
        addRecord($farmer_id);
        break;
    case 'PUT':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['record_id'])) {
            updateRecord($farmer_id, $_GET['record_id']);
        } else {
            sendJsonResponse(['error' => 'Record ID required'], 400);
        }
        break;
    case 'DELETE':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['record_id'])) {
            deleteRecord($farmer_id, $_GET['record_id']);
        } else {
            sendJsonResponse(['error' => 'Record ID required'], 400);
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function addRecord($farmer_id) {
    global $db;

    $input = json_decode(file_get_contents('php://input'), true);

    if (!isset($input['record_type']) || !isset($input['amount']) || !isset($input['description'])) {
        sendJsonResponse(['error' => 'Required fields: record_type, amount, description'], 400);
    }

    $record_type = sanitizeInput($input['record_type']);
    $amount = floatval($input['amount']);
    $description = sanitizeInput($input['description']);
    $crop_id = isset($input['crop_id']) ? intval($input['crop_id']) : null;
    $quantity = isset($input['quantity']) ? floatval($input['quantity']) : null;
    $unit = isset($input['unit']) ? sanitizeInput($input['unit']) : null;
    $record_date = isset($input['record_date']) ? sanitizeInput($input['record_date']) : date('Y-m-d');

    try {
        $query = "INSERT INTO farm_records (farmer_id, crop_id, record_type, amount, quantity, unit, description, record_date) 
                  VALUES (:farmer_id, :crop_id, :record_type, :amount, :quantity, :unit, :description, :record_date)";

        $stmt = $db->prepare($query);
        $stmt->bindParam(':farmer_id', $farmer_id);
        $stmt->bindParam(':crop_id', $crop_id);
        $stmt->bindParam(':record_type', $record_type);
        $stmt->bindParam(':amount', $amount);
        $stmt->bindParam(':quantity', $quantity);
        $stmt->bindParam(':unit', $unit);
        $stmt->bindParam(':description', $description);
        $stmt->bindParam(':record_date', $record_date);

        $stmt->execute();

        sendJsonResponse([
            'success' => true,
            'message' => 'Record added successfully',
            'record_id' => $db->lastInsertId()
        ]);

    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to add record: ' . $exception->getMessage()], 500);
    }
}

function getAllRecords($farmer_id) {
    global $db;

    $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 50;
    $offset = isset($_GET['offset']) ? intval($_GET['offset']) : 0;

    try {
        $query = "SELECT fr.*, cm.crop_name_hindi, cm.crop_name_english 
                  FROM farm_records fr 
                  LEFT JOIN crop_master cm ON fr.crop_id = cm.crop_id 
                  WHERE fr.farmer_id = :farmer_id 
                  ORDER BY fr.record_date DESC, fr.created_at DESC 
                  LIMIT :limit OFFSET :offset";

        $stmt = $db->prepare($query);
        $stmt->bindParam(':farmer_id', $farmer_id);
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
        $stmt->execute();

        $records = $stmt->fetchAll(PDO::FETCH_ASSOC);

        sendJsonResponse([
            'success' => true,
            'records' => $records
        ]);

    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch records: ' . $exception->getMessage()], 500);
    }
}

function getFinancialSummary($farmer_id) {
    global $db;

    $year = isset($_GET['year']) ? intval($_GET['year']) : date('Y');
    $month = isset($_GET['month']) ? intval($_GET['month']) : null;

    try {
        $date_condition = "YEAR(record_date) = :year";
        $params = [':farmer_id' => $farmer_id, ':year' => $year];

        if ($month) {
            $date_condition .= " AND MONTH(record_date) = :month";
            $params[':month'] = $month;
        }

        // Get income summary
        $income_query = "SELECT SUM(amount) as total_income, COUNT(*) as income_count 
                        FROM farm_records 
                        WHERE farmer_id = :farmer_id AND record_type = 'income' AND $date_condition";

        $income_stmt = $db->prepare($income_query);
        foreach ($params as $param => $value) {
            $income_stmt->bindValue($param, $value);
        }
        $income_stmt->execute();
        $income_data = $income_stmt->fetch(PDO::FETCH_ASSOC);

        // Get expense summary
        $expense_query = "SELECT SUM(amount) as total_expense, COUNT(*) as expense_count 
                         FROM farm_records 
                         WHERE farmer_id = :farmer_id AND record_type = 'expense' AND $date_condition";

        $expense_stmt = $db->prepare($expense_query);
        foreach ($params as $param => $value) {
            $expense_stmt->bindValue($param, $value);
        }
        $expense_stmt->execute();
        $expense_data = $expense_stmt->fetch(PDO::FETCH_ASSOC);

        // Get yield summary
        $yield_query = "SELECT SUM(quantity) as total_yield, COUNT(*) as yield_count 
                       FROM farm_records 
                       WHERE farmer_id = :farmer_id AND record_type = 'yield' AND $date_condition";

        $yield_stmt = $db->prepare($yield_query);
        foreach ($params as $param => $value) {
            $yield_stmt->bindValue($param, $value);
        }
        $yield_stmt->execute();
        $yield_data = $yield_stmt->fetch(PDO::FETCH_ASSOC);

        $total_income = floatval($income_data['total_income'] ?? 0);
        $total_expense = floatval($expense_data['total_expense'] ?? 0);
        $profit_loss = $total_income - $total_expense;

        sendJsonResponse([
            'success' => true,
            'summary' => [
                'total_income' => $total_income,
                'total_expense' => $total_expense,
                'profit_loss' => $profit_loss,
                'total_yield' => floatval($yield_data['total_yield'] ?? 0),
                'income_count' => intval($income_data['income_count'] ?? 0),
                'expense_count' => intval($expense_data['expense_count'] ?? 0),
                'yield_count' => intval($yield_data['yield_count'] ?? 0),
                'year' => $year,
                'month' => $month
            ]
        ]);

    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch financial summary: ' . $exception->getMessage()], 500);
    }
}
?>
