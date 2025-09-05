<?php
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
