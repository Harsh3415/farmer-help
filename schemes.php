<?php
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
