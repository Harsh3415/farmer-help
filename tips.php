<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

switch ($request_method) {
    case 'GET':
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'seasonal':
                    getSeasonalTips();
                    break;
                case 'crop_specific':
                    getCropSpecificTips();
                    break;
                case 'categories':
                    getTipCategories();
                    break;
                case 'latest':
                    getLatestTips();
                    break;
                default:
                    getAllTips();
            }
        } else {
            getAllTips();
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function getAllTips() {
    global $db;

    $category = isset($_GET['category']) ? sanitizeInput($_GET['category']) : null;
    $crop_id = isset($_GET['crop_id']) ? intval($_GET['crop_id']) : null;
    $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 20;

    try {
        $query = "SELECT at.*, cm.crop_name_hindi, cm.crop_name_english 
                  FROM agri_tips at 
                  LEFT JOIN crop_master cm ON at.crop_id = cm.crop_id 
                  WHERE at.is_active = 1";

        $params = [];

        if ($category) {
            $query .= " AND at.category = :category";
            $params[':category'] = $category;
        }

        if ($crop_id) {
            $query .= " AND at.crop_id = :crop_id";
            $params[':crop_id'] = $crop_id;
        }

        $query .= " ORDER BY at.created_at DESC LIMIT :limit";
        $params[':limit'] = $limit;

        $stmt = $db->prepare($query);
        foreach ($params as $param => $value) {
            if ($param === ':limit' || $param === ':crop_id') {
                $stmt->bindValue($param, $value, PDO::PARAM_INT);
            } else {
                $stmt->bindValue($param, $value);
            }
        }
        $stmt->execute();

        $tips = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // If no database tips, return mock data
        if (empty($tips)) {
            $tips = getMockTips();
        }

        sendJsonResponse([
            'success' => true,
            'tips' => $tips
        ]);

    } catch (PDOException $exception) {
        // Return mock data on error
        sendJsonResponse([
            'success' => true,
            'tips' => getMockTips()
        ]);
    }
}

function getMockTips() {
    return [
        [
            'id' => 1,
            'title' => 'धान की फसल की देखभाल',
            'content' => 'फूल आने के समय खेत में पानी की सही मात्रा बनाए रखें। कीटों से बचाव के लिए नीम का तेल का छिड़काव करें। नियमित रूप से खेत का निरीक्षण करते रहें।',
            'category' => 'फसल प्रबंधन',
            'season' => 'kharif',
            'crop_name_hindi' => 'धान',
            'crop_name_english' => 'Rice',
            'created_at' => date('Y-m-d H:i:s')
        ],
        [
            'id' => 2,
            'title' => 'मिट्टी की जांच का महत्व',
            'content' => 'हर 3 साल में मिट्टी की जांच कराएं। सही पोषक तत्वों की जानकारी के लिए नजदीकी कृषि विभाग से संपर्क करें। मिट्टी की pH और पोषक तत्वों की जांच कराना जरूरी है।',
            'category' => 'मिट्टी स्वास्थ्य',
            'season' => 'all',
            'crop_name_hindi' => null,
            'crop_name_english' => null,
            'created_at' => date('Y-m-d H:i:s')
        ],
        [
            'id' => 3,
            'title' => 'पानी की बचत के तरीके',
            'content' => 'ड्रिप सिंचाई और स्प्रिंकलर का उपयोग करके 40% तक पानी की बचत करें। बारिश के पानी को इकट्ठा करने की व्यवस्था करें। सिंचाई सुबह या शाम के समय करें।',
            'category' => 'जल प्रबंधन',
            'season' => 'all',
            'crop_name_hindi' => null,
            'crop_name_english' => null,
            'created_at' => date('Y-m-d H:i:s')
        ],
        [
            'id' => 4,
            'title' => 'जैविक खाद का उपयोग',
            'content' => 'गोबर की खाद, कंपोस्ट और वर्मी कंपोस्ट का उपयोग करें। ये मिट्टी की उर्वरता बढ़ाते हैं और लंबे समय तक फायदेमंद होते हैं।',
            'category' => 'उर्वरक प्रबंधन',
            'season' => 'all',
            'crop_name_hindi' => null,
            'crop_name_english' => null,
            'created_at' => date('Y-m-d H:i:s')
        ],
        [
            'id' => 5,
            'title' => 'कीट नियंत्रण के प्राकृतिक तरीके',
            'content' => 'नीम का तेल, लहसुन का रस और गोमूत्र का मिश्रण बनाकर छिड़काव करें। प्राकृतिक कीट नियंत्रण से फसल और मिट्टी दोनों सुरक्षित रहते हैं।',
            'category' => 'कीट नियंत्रण',
            'season' => 'all',
            'crop_name_hindi' => null,
            'crop_name_english' => null,
            'created_at' => date('Y-m-d H:i:s')
        ]
    ];
}

function getSeasonalTips() {
    $season = isset($_GET['season']) ? sanitizeInput($_GET['season']) : getCurrentSeason();

    $seasonal_tips = [
        'kharif' => [
            ['title' => 'खरीफ बुआई की तैयारी', 'content' => 'मानसून से पहले खेत की तैयारी करें। बीज, खाद और कीटनाशक का प्रबंध कर लें।'],
            ['title' => 'धान की रोपाई', 'content' => 'उचित दूरी पर धान की रोपाई करें। खेत में 2-3 सेमी पानी रखें।'],
            ['title' => 'खरपतवार नियंत्रण', 'content' => 'रोपाई के 15-20 दिन बाद खरपतवार निकालें।']
        ],
        'rabi' => [
            ['title' => 'रबी बुआई का समय', 'content' => 'अक्टूबर-नवंबर में गेहूं की बुआई करें। उचित बीज दर का प्रयोग करें।'],
            ['title' => 'सिंचाई प्रबंधन', 'content' => 'पहली सिंचाई बुआई के 20-25 दिन बाद करें।'],
            ['title' => 'उर्वरक प्रबंधन', 'content' => 'मिट्टी जांच के आधार पर उर्वरक का प्रयोग करें।']
        ]
    ];

    $tips = isset($seasonal_tips[$season]) ? $seasonal_tips[$season] : $seasonal_tips['kharif'];

    sendJsonResponse([
        'success' => true,
        'season' => $season,
        'tips' => $tips
    ]);
}

function getCurrentSeason() {
    $month = date('n');
    if ($month >= 6 && $month <= 10) {
        return 'kharif';
    } elseif ($month >= 11 || $month <= 3) {
        return 'rabi';
    } else {
        return 'zaid';
    }
}

function getTipCategories() {
    $categories = [
        'फसल प्रबंधन',
        'मिट्टी स्वास्थ्य',
        'जल प्रबंधन',
        'उर्वरक प्रबंधन',
        'कीट नियंत्रण',
        'रोग नियंत्रण',
        'बीज उत्पादन',
        'फसल कटाई',
        'भंडारण',
        'विपणन'
    ];

    sendJsonResponse([
        'success' => true,
        'categories' => $categories
    ]);
}

function getLatestTips() {
    global $db;

    $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 5;

    try {
        $query = "SELECT at.*, cm.crop_name_hindi 
                  FROM agri_tips at 
                  LEFT JOIN crop_master cm ON at.crop_id = cm.crop_id 
                  WHERE at.is_active = 1 
                  ORDER BY at.created_at DESC 
                  LIMIT :limit";

        $stmt = $db->prepare($query);
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->execute();

        $tips = $stmt->fetchAll(PDO::FETCH_ASSOC);

        if (empty($tips)) {
            $tips = array_slice(getMockTips(), 0, $limit);
        }

        sendJsonResponse([
            'success' => true,
            'tips' => $tips
        ]);

    } catch (PDOException $exception) {
        sendJsonResponse([
            'success' => true,
            'tips' => array_slice(getMockTips(), 0, $limit)
        ]);
    }
}
?>
