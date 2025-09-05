<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

switch ($request_method) {
    case 'GET':
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'prices':
                    getMarketPrices();
                    break;
                case 'trends':
                    getPriceTrends();
                    break;
                case 'markets':
                    getNearbyMarkets();
                    break;
                default:
                    getMarketPrices();
            }
        } else {
            getMarketPrices();
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function getMarketPrices() {
    global $db;

    $district = isset($_GET['district']) ? sanitizeInput($_GET['district']) : null;
    $crop = isset($_GET['crop']) ? sanitizeInput($_GET['crop']) : null;

    try {
        $query = "SELECT mp.*, cm.crop_name_hindi, cm.crop_name_english 
                  FROM market_prices mp 
                  JOIN crop_master cm ON mp.crop_id = cm.crop_id 
                  WHERE mp.price_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)";

        $params = [];

        if ($district) {
            $query .= " AND mp.district LIKE :district";
            $params[':district'] = "%$district%";
        }

        if ($crop) {
            $query .= " AND (cm.crop_name_hindi LIKE :crop OR cm.crop_name_english LIKE :crop)";
            $params[':crop'] = "%$crop%";
        }

        $query .= " ORDER BY mp.price_date DESC, mp.price_per_quintal DESC";

        $stmt = $db->prepare($query);
        foreach ($params as $param => $value) {
            $stmt->bindValue($param, $value);
        }
        $stmt->execute();

        $prices = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // If no database prices, return mock data
        if (empty($prices)) {
            $prices = getMockMarketPrices();
        }

        sendJsonResponse([
            'success' => true,
            'prices' => $prices
        ]);

    } catch (PDOException $exception) {
        // Return mock data on error
        sendJsonResponse([
            'success' => true,
            'prices' => getMockMarketPrices()
        ]);
    }
}

function getMockMarketPrices() {
    return [
        ['crop_name_hindi' => 'धान', 'crop_name_english' => 'Rice', 'price_per_quintal' => 2150, 'market_name' => 'गाजीपुर मंडी', 'district' => 'गाजीपुर', 'state' => 'उत्तर प्रदेश', 'price_trend' => 'up', 'price_date' => date('Y-m-d')],
        ['crop_name_hindi' => 'गेहूं', 'crop_name_english' => 'Wheat', 'price_per_quintal' => 2250, 'market_name' => 'वाराणसी मंडी', 'district' => 'वाराणसी', 'state' => 'उत्तर प्रदेश', 'price_trend' => 'up', 'price_date' => date('Y-m-d')],
        ['crop_name_hindi' => 'आलू', 'crop_name_english' => 'Potato', 'price_per_quintal' => 1200, 'market_name' => 'आगरा मंडी', 'district' => 'आगरा', 'state' => 'उत्तर प्रदेश', 'price_trend' => 'down', 'price_date' => date('Y-m-d')],
        ['crop_name_hindi' => 'प्याज', 'crop_name_english' => 'Onion', 'price_per_quintal' => 3500, 'market_name' => 'नासिक मंडी', 'district' => 'नासिक', 'state' => 'महाराष्ट्र', 'price_trend' => 'up', 'price_date' => date('Y-m-d')],
        ['crop_name_hindi' => 'टमाटर', 'crop_name_english' => 'Tomato', 'price_per_quintal' => 2800, 'market_name' => 'दिल्ली मंडी', 'district' => 'दिल्ली', 'state' => 'दिल्ली', 'price_trend' => 'up', 'price_date' => date('Y-m-d')]
    ];
}

function getPriceTrends() {
    $crop_id = isset($_GET['crop_id']) ? intval($_GET['crop_id']) : 1;
    $days = isset($_GET['days']) ? intval($_GET['days']) : 30;

    // Mock trend data
    $trends = [];
    for ($i = $days; $i >= 0; $i--) {
        $date = date('Y-m-d', strtotime("-$i days"));
        $price = 2000 + rand(-200, 300); // Mock price variation
        $trends[] = [
            'date' => $date,
            'price' => $price,
            'market' => 'गाजीपुर मंडी'
        ];
    }

    sendJsonResponse([
        'success' => true,
        'trends' => $trends
    ]);
}

function getNearbyMarkets() {
    $district = isset($_GET['district']) ? sanitizeInput($_GET['district']) : 'गाजीपुर';

    // Mock nearby markets data
    $markets = [
        ['name' => 'गाजीपुर मंडी', 'district' => 'गाजीपुर', 'distance' => '5 किमी', 'contact' => '+91-9876543210'],
        ['name' => 'वाराणसी मंडी', 'district' => 'वाराणसी', 'distance' => '45 किमी', 'contact' => '+91-9876543211'],
        ['name' => 'इलाहाबाद मंडी', 'district' => 'प्रयागराज', 'distance' => '85 किमी', 'contact' => '+91-9876543212'],
        ['name' => 'जौनपुर मंडी', 'district' => 'जौनपुर', 'distance' => '35 किमी', 'contact' => '+91-9876543213']
    ];

    sendJsonResponse([
        'success' => true,
        'markets' => $markets
    ]);
}
?>
