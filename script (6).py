# Create expert consultation API
expert_api = """<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

// Verify session for protected endpoints
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
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'my_queries':
                    $farmer_id = verifyFarmerSession();
                    getMyQueries($farmer_id);
                    break;
                case 'faq':
                    getFAQ();
                    break;
                case 'query_details':
                    if (isset($_GET['query_id'])) {
                        getQueryDetails($_GET['query_id']);
                    } else {
                        sendJsonResponse(['error' => 'Query ID required'], 400);
                    }
                    break;
                default:
                    getFAQ();
            }
        } else {
            getFAQ();
        }
        break;
    case 'POST':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['action']) && $_GET['action'] === 'ask') {
            askExpert($farmer_id);
        } else {
            sendJsonResponse(['error' => 'Invalid action'], 400);
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function askExpert($farmer_id) {
    global $db;
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['query_text']) || empty(trim($input['query_text']))) {
        sendJsonResponse(['error' => 'Query text is required'], 400);
    }
    
    $query_text = sanitizeInput($input['query_text']);
    $crop_id = isset($input['crop_id']) ? intval($input['crop_id']) : null;
    $priority = isset($input['priority']) ? sanitizeInput($input['priority']) : 'medium';
    
    try {
        $query = "INSERT INTO expert_queries (farmer_id, crop_id, query_text, priority) VALUES (:farmer_id, :crop_id, :query_text, :priority)";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':farmer_id', $farmer_id);
        $stmt->bindParam(':crop_id', $crop_id);
        $stmt->bindParam(':query_text', $query_text);
        $stmt->bindParam(':priority', $priority);
        
        $stmt->execute();
        $query_id = $db->lastInsertId();
        
        sendJsonResponse([
            'success' => true,
            'message' => 'आपका प्रश्न सफलतापूर्वक भेजा गया है। विशेषज्ञ जल्द ही उत्तर देंगे।',
            'query_id' => $query_id
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to submit query: ' . $exception->getMessage()], 500);
    }
}

function getMyQueries($farmer_id) {
    global $db;
    
    try {
        $query = "SELECT eq.*, cm.crop_name_hindi, cm.crop_name_english 
                  FROM expert_queries eq 
                  LEFT JOIN crop_master cm ON eq.crop_id = cm.crop_id 
                  WHERE eq.farmer_id = :farmer_id 
                  ORDER BY eq.created_at DESC";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':farmer_id', $farmer_id);
        $stmt->execute();
        
        $queries = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        sendJsonResponse([
            'success' => true,
            'queries' => $queries
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch queries: ' . $exception->getMessage()], 500);
    }
}

function getFAQ() {
    $faqs = [
        [
            'question' => 'धान में पत्तियों पर भूरे धब्बे आ रहे हैं, क्या करूं?',
            'answer' => 'यह ब्लास्ट रोग हो सकता है। कॉपर ऑक्सीक्लोराइड का छिड़काव करें। बीज उपचार और संतुलित उर्वरक का प्रयोग करें।',
            'category' => 'रोग नियंत्रण',
            'crop' => 'धान'
        ],
        [
            'question' => 'मिट्टी की जांच कब और कैसे कराएं?',
            'answer' => 'हर 2-3 साल में मिट्टी की जांच कराएं। नजदीकी कृषि विज्ञान केंद्र या मिट्टी जांच प्रयोगशाला में संपर्क करें। pH, नाइट्रोजन, फास्फोरस और पोटाश की जांच कराना जरूरी है।',
            'category' => 'मिट्टी स्वास्थ्य',
            'crop' => 'सामान्य'
        ],
        [
            'question' => 'जैविक खाद कैसे बनाएं?',
            'answer' => 'गोबर, हरी पत्तियों, रसोई का कचरा मिलाकर कंपोस्ट बना सकते हैं। इसे 3-4 महीने में तैयार हो जाता है। नियमित पानी और हवा दें।',
            'category' => 'उर्वरक प्रबंधन',
            'crop' => 'सामान्य'
        ],
        [
            'question' => 'फसल में कीड़े लग गए हैं, प्राकृतिक उपाय क्या हैं?',
            'answer' => 'नीम का तेल, लहसुन-प्याज का रस, गोमूत्र का छिड़काव करें। रासायनिक दवाओं से बचें। पीले चिपचिपे जाल लगाएं।',
            'category' => 'कीट नियंत्रण',
            'crop' => 'सामान्य'
        ],
        [
            'question' => 'सिंचाई कब और कितना पानी दें?',
            'answer' => 'मिट्टी में नमी देखकर सिंचाई करें। सुबह या शाम का समय बेहतर है। ड्रिप सिंचाई से पानी की बचत होती है। अधिक पानी से जड़ सड़ सकती है।',
            'category' => 'जल प्रबंधन',
            'crop' => 'सामान्य'
        ]
    ];
    
    sendJsonResponse([
        'success' => true,
        'faqs' => $faqs
    ]);
}

function getQueryDetails($query_id) {
    global $db;
    
    try {
        $query = "SELECT eq.*, cm.crop_name_hindi, cm.crop_name_english, f.name as farmer_name 
                  FROM expert_queries eq 
                  LEFT JOIN crop_master cm ON eq.crop_id = cm.crop_id 
                  JOIN farmers f ON eq.farmer_id = f.farmer_id 
                  WHERE eq.id = :query_id";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':query_id', $query_id);
        $stmt->execute();
        
        if ($stmt->rowCount() === 0) {
            sendJsonResponse(['error' => 'Query not found'], 404);
        }
        
        $query_details = $stmt->fetch(PDO::FETCH_ASSOC);
        
        sendJsonResponse([
            'success' => true,
            'query' => $query_details
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch query details: ' . $exception->getMessage()], 500);
    }
}
?>
"""

with open('api/expert.php', 'w', encoding='utf-8') as f:
    f.write(expert_api)

# Create records API (for farm records and financial tracking)
records_api = """<?php
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
"""

with open('api/records.php', 'w', encoding='utf-8') as f:
    f.write(records_api)

# Create government schemes API
schemes_api = """<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

switch ($request_method) {
    case 'GET':
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'active':
                    getActiveSchemes();
                    break;
                case 'by_type':
                    getSchemesByType();
                    break;
                case 'details':
                    if (isset($_GET['scheme_id'])) {
                        getSchemeDetails($_GET['scheme_id']);
                    } else {
                        sendJsonResponse(['error' => 'Scheme ID required'], 400);
                    }
                    break;
                default:
                    getAllSchemes();
            }
        } else {
            getAllSchemes();
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function getAllSchemes() {
    global $db;
    
    try {
        $query = "SELECT * FROM government_schemes WHERE is_active = 1 ORDER BY scheme_name";
        $stmt = $db->prepare($query);
        $stmt->execute();
        
        $schemes = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // If no database schemes, return mock data
        if (empty($schemes)) {
            $schemes = getMockSchemes();
        }
        
        sendJsonResponse([
            'success' => true,
            'schemes' => $schemes
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse([
            'success' => true,
            'schemes' => getMockSchemes()
        ]);
    }
}

function getMockSchemes() {
    return [
        [
            'id' => 1,
            'scheme_name' => 'प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)',
            'description' => 'सभी भूमिधारक किसानों को आर्थिक सहायता प्रदान करने वाली योजना',
            'eligibility_criteria' => 'सभी भूमिधारक किसान परिवार जिनके पास खेती योग्य भूमि है',
            'benefits' => 'रु. 6,000 प्रति वर्ष तीन किस्तों में (रु. 2,000 प्रत्येक)',
            'application_process' => 'नजदीकी CSC केंद्र या ऑनलाइन pmkisan.gov.in पर आवेदन करें',
            'contact_info' => 'टोल फ्री: 155261 या 1800115526',
            'scheme_type' => 'subsidy',
            'target_farmers' => 'all'
        ],
        [
            'id' => 2,
            'scheme_name' => 'प्रधानमंत्री फसल बीमा योजना (PMFBY)',
            'description' => 'फसल के नुकसान की स्थिति में किसानों को बीमा सुरक्षा',
            'eligibility_criteria' => 'सभी किसान (भूमिधारक और किरायेदार)',
            'benefits' => 'प्राकृतिक आपदाओं से होने वाले नुकसान का मुआवजा',
            'application_process' => 'नजदीकी बैंक, CSC या ऑनलाइ apply करें',
            'contact_info' => 'टोल फ्री: 14447',
            'scheme_type' => 'insurance',
            'target_farmers' => 'all'
        ],
        [
            'id' => 3,
            'scheme_name' => 'मृदा स्वास्थ्य कार्ड योजना',
            'description' => 'किसानों को मिट्टी की गुणवत्ता की जानकारी प्रदान करना',
            'eligibility_criteria' => 'सभी किसान',
            'benefits' => 'मुफ्त मिट्टी जांच और उर्वरक की सलाह',
            'application_process' => 'नजदीकी कृषि विभाग या मिट्टी जांच प्रयोगशाला में संपर्क करें',
            'contact_info' => 'स्थानीय कृषि विभाग',
            'scheme_type' => 'advisory',
            'target_farmers' => 'all'
        ],
        [
            'id' => 4,
            'scheme_name' => 'किसान क्रेडिट कार्ड (KCC)',
            'description' => 'कृषि और संबद्ध गतिविधियों के लिए आसान ऋण',
            'eligibility_criteria' => 'भूमिधारक किसान, किरायेदार किसान, और शेयर क्रॉपर',
            'benefits' => 'कम ब्याज दर पर ऋण, 3 लाख तक बिना गारंटी',
            'application_process' => 'नजदीकी बैंक शाखा में आवेदन करें',
            'contact_info' => 'स्थानीय बैंक शाखा',
            'scheme_type' => 'loan',
            'target_farmers' => 'all'
        ],
        [
            'id' => 5,
            'scheme_name' => 'प्रधानमंत्री कृषि सिंचाई योजना (PMKSY)',
            'description' => 'सिंचाई सुविधाओं का विकास और जल का कुशल उपयोग',
            'eligibility_criteria' => 'सभी किसान',
            'benefits' => 'ड्रिप और स्प्रिंकलर सिंचाई पर 80% तक सब्सिडी',
            'application_process' => 'कृषि विभाग या जल संरक्षण विभाग में आवेदन',
            'contact_info' => 'स्थानीय कृषि विभाग',
            'scheme_type' => 'subsidy',
            'target_farmers' => 'all'
        ]
    ];
}

function getActiveSchemes() {
    global $db;
    
    try {
        $query = "SELECT * FROM government_schemes WHERE is_active = 1 ORDER BY created_at DESC LIMIT 10";
        $stmt = $db->prepare($query);
        $stmt->execute();
        
        $schemes = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        if (empty($schemes)) {
            $schemes = getMockSchemes();
        }
        
        sendJsonResponse([
            'success' => true,
            'schemes' => $schemes
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse([
            'success' => true,
            'schemes' => getMockSchemes()
        ]);
    }
}

function getSchemesByType() {
    $type = isset($_GET['type']) ? sanitizeInput($_GET['type']) : 'all';
    
    $schemes = getMockSchemes();
    
    if ($type !== 'all') {
        $schemes = array_filter($schemes, function($scheme) use ($type) {
            return $scheme['scheme_type'] === $type;
        });
        $schemes = array_values($schemes); // Re-index array
    }
    
    sendJsonResponse([
        'success' => true,
        'schemes' => $schemes,
        'type' => $type
    ]);
}

function getSchemeDetails($scheme_id) {
    global $db;
    
    try {
        $query = "SELECT * FROM government_schemes WHERE id = :scheme_id AND is_active = 1";
        $stmt = $db->prepare($query);
        $stmt->bindParam(':scheme_id', $scheme_id);
        $stmt->execute();
        
        if ($stmt->rowCount() === 0) {
            // Try from mock data
            $schemes = getMockSchemes();
            $scheme = null;
            foreach ($schemes as $s) {
                if ($s['id'] == $scheme_id) {
                    $scheme = $s;
                    break;
                }
            }
            
            if (!$scheme) {
                sendJsonResponse(['error' => 'Scheme not found'], 404);
                return;
            }
        } else {
            $scheme = $stmt->fetch(PDO::FETCH_ASSOC);
        }
        
        sendJsonResponse([
            'success' => true,
            'scheme' => $scheme
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch scheme details: ' . $exception->getMessage()], 500);
    }
}
?>
"""

with open('api/schemes.php', 'w', encoding='utf-8') as f:
    f.write(schemes_api)

print("Created: api/expert.php, api/records.php, api/schemes.php")

# Now create installation instructions and documentation
installation_guide = """# Krishi Sahayak (Rural Farmer Helper) - Installation Guide

## Overview
Krishi Sahayak is a comprehensive digital platform designed specifically for rural farmers in India. It provides crop management, weather information, market prices, expert consultation, and agricultural tips in Hindi language.

## System Requirements

### Server Requirements
- PHP 7.4 or higher
- MySQL 5.7 or higher
- Apache/Nginx web server
- Minimum 1GB RAM
- 500MB free disk space

### Local Development
- XAMPP, WAMP, or MAMP
- Modern web browser (Chrome, Firefox, Safari)
- Internet connection for initial setup

## Installation Steps

### Step 1: Download and Extract Files
1. Download the project files
2. Extract to your web server directory:
   - XAMPP: `htdocs/krishi-sahayak/`
   - WAMP: `www/krishi-sahayak/`
   - LAMP: `/var/www/html/krishi-sahayak/`

### Step 2: Database Setup
1. Open phpMyAdmin (http://localhost/phpmyadmin)
2. Create a new database: `krishi_sahayak`
3. Import the database schema:
   - Click on the `krishi_sahayak` database
   - Go to "Import" tab
   - Choose file: `database_schema.sql`
   - Click "Go" to import

### Step 3: Configuration
1. Open `config.php` file
2. Update database credentials if necessary:
   ```php
   define('DB_HOST', 'localhost');
   define('DB_USERNAME', 'root');
   define('DB_PASSWORD', '');
   define('DB_NAME', 'krishi_sahayak');
   ```

### Step 4: File Permissions
Set proper permissions for upload directory:
```bash
chmod 755 uploads/
```

### Step 5: Access the Application
1. Open web browser
2. Navigate to: `http://localhost/krishi-sahayak/`
3. The web application should load with the farmer dashboard

## Project Structure

```
krishi-sahayak/
├── index.html              # Main web application
├── style.css              # Application styles  
├── app.js                 # Frontend JavaScript
├── config.php             # Database configuration
├── database_schema.sql    # Database schema
├── api/                   # Backend API endpoints
│   ├── index.php         # API router
│   ├── auth.php          # Authentication API
│   ├── crops.php         # Crop management API
│   ├── weather.php       # Weather information API
│   ├── market.php        # Market prices API
│   ├── tips.php          # Agricultural tips API
│   ├── expert.php        # Expert consultation API
│   ├── records.php       # Farm records API
│   └── schemes.php       # Government schemes API
└── uploads/              # File upload directory
```

## API Endpoints

### Authentication
- `POST /api/auth?action=register` - Register new farmer
- `POST /api/auth?action=login` - Login farmer
- `GET /api/auth?action=verify` - Verify session
- `POST /api/auth?action=logout` - Logout farmer

### Crops Management
- `GET /api/crops?action=master` - Get crop master data
- `GET /api/crops?action=farmer_crops` - Get farmer's crops
- `POST /api/crops?action=add` - Add new crop
- `GET /api/crops?action=diseases` - Get crop diseases

### Weather
- `GET /api/weather?action=current` - Current weather
- `GET /api/weather?action=forecast` - Weather forecast
- `GET /api/weather?action=alerts` - Weather alerts

### Market Prices
- `GET /api/market?action=prices` - Market prices
- `GET /api/market?action=trends` - Price trends
- `GET /api/market?action=markets` - Nearby markets

### Agricultural Tips
- `GET /api/tips` - All tips
- `GET /api/tips?action=seasonal` - Seasonal tips
- `GET /api/tips?action=categories` - Tip categories

### Expert Consultation
- `POST /api/expert?action=ask` - Ask expert question
- `GET /api/expert?action=my_queries` - Get farmer's queries
- `GET /api/expert?action=faq` - FAQ

### Farm Records
- `GET /api/records` - All records
- `POST /api/records` - Add new record
- `GET /api/records?action=summary` - Financial summary

### Government Schemes
- `GET /api/schemes` - All schemes
- `GET /api/schemes?action=active` - Active schemes
- `GET /api/schemes?action=details&scheme_id=1` - Scheme details

## Features

### For Farmers
1. **Dashboard**: Overview of crops, weather, and important updates
2. **Crop Management**: Track crops from planting to harvest
3. **Weather Information**: Current weather and forecasts
4. **Market Prices**: Real-time commodity prices
5. **Expert Advice**: Ask questions and get expert responses
6. **Agricultural Tips**: Seasonal and crop-specific advice
7. **Farm Records**: Track income, expenses, and yields
8. **Government Schemes**: Information about available schemes

### Technical Features
1. **Responsive Design**: Works on mobile devices
2. **Hindi Language Support**: Full Hindi interface
3. **Offline Capability**: Basic functionality without internet
4. **RESTful API**: Clean API structure
5. **Database Driven**: MySQL backend
6. **Session Management**: Secure user sessions
7. **File Upload**: Image upload for queries

## Usage Instructions

### For Farmers

#### First Time Setup
1. Open the application in web browser
2. Register with name and phone number
3. Complete profile with address and land details
4. Start adding crops and managing farm data

#### Daily Usage
1. Check dashboard for weather and updates
2. View market prices for selling decisions
3. Update crop stages and activities
4. Ask experts for farming problems
5. Record farm income and expenses

#### Key Features Usage
- **Add Crop**: Go to Crop Management > Add New Crop
- **Check Weather**: Weather section shows current and forecast
- **View Prices**: Market Prices section for commodity rates
- **Ask Expert**: Expert Advice > Ask Question
- **Track Money**: Farm Records > Add Income/Expense

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database credentials in config.php
   - Ensure MySQL service is running
   - Verify database exists

2. **File Permission Issues**
   - Set proper permissions: `chmod 755 uploads/`
   - Check web server user has write access

3. **API Not Working**
   - Verify .htaccess file exists
   - Check Apache mod_rewrite is enabled
   - Ensure all API files are present

4. **PHP Errors**
   - Enable error reporting in PHP
   - Check PHP version compatibility
   - Verify all required extensions installed

### Error Messages
- "Connection error": Database connectivity issue
- "Authentication required": Session expired, login again
- "Invalid request": Check API endpoint and parameters
- "File upload failed": Check file permissions and size limits

## Support and Maintenance

### Regular Maintenance
1. **Database Backup**: Regularly backup MySQL database
2. **File Backup**: Backup uploaded files and code
3. **Updates**: Keep PHP and MySQL updated
4. **Monitoring**: Monitor disk space and performance

### Adding New Features
1. Create new API endpoint in `/api/` directory
2. Add database tables if needed
3. Update frontend interface
4. Test thoroughly before deployment

## Security Considerations

1. **Input Validation**: All user inputs are sanitized
2. **SQL Injection**: PDO prepared statements used
3. **Session Security**: Secure session management
4. **File Upload**: File type and size validation
5. **HTTPS**: Use SSL in production environment

## Production Deployment

### Web Server Configuration
1. Use Apache/Nginx with proper configuration
2. Enable SSL/HTTPS
3. Set up proper file permissions
4. Configure regular backups

### Performance Optimization
1. Enable PHP opcode caching
2. Use database connection pooling
3. Implement caching for frequently accessed data
4. Optimize images and static assets

### Monitoring
1. Set up server monitoring
2. Monitor database performance
3. Track application usage
4. Regular security updates

## Contributing

To contribute to this project:
1. Fork the repository
2. Create feature branch
3. Make changes and test thoroughly
4. Submit pull request with description

## License

This project is open source and available for educational and non-commercial use.

## Contact

For technical support or questions about the project, please contact the development team.
"""

with open('INSTALLATION_GUIDE.md', 'w', encoding='utf-8') as f:
    f.write(installation_guide)

print("Created: INSTALLATION_GUIDE.md")
print("✅ Rural Farmer Helper project created successfully!")