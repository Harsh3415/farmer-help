# Create weather API
weather_api = """<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

switch ($request_method) {
    case 'GET':
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'current':
                    getCurrentWeather();
                    break;
                case 'forecast':
                    getWeatherForecast();
                    break;
                case 'alerts':
                    getWeatherAlerts();
                    break;
                default:
                    getCurrentWeather();
            }
        } else {
            getCurrentWeather();
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function getCurrentWeather() {
    $district = isset($_GET['district']) ? sanitizeInput($_GET['district']) : 'गाजीपुर';
    $state = isset($_GET['state']) ? sanitizeInput($_GET['state']) : 'उत्तर प्रदेश';
    
    // Mock current weather data - in real implementation, integrate with weather API
    $current_weather = [
        'district' => $district,
        'state' => $state,
        'date' => date('Y-m-d'),
        'temperature' => '28°C',
        'temperature_max' => '32°C',
        'temperature_min' => '24°C',
        'humidity' => '65%',
        'rainfall' => '0 मिमी',
        'wind_speed' => '12 किमी/घंटा',
        'weather_condition' => 'आंशिक बादल',
        'uv_index' => 'मध्यम',
        'visibility' => '10 किमी',
        'pressure' => '1013 hPa',
        'sunrise' => '06:15',
        'sunset' => '17:45'
    ];
    
    sendJsonResponse([
        'success' => true,
        'current_weather' => $current_weather
    ]);
}

function getWeatherForecast() {
    $days = isset($_GET['days']) ? intval($_GET['days']) : 5;
    $district = isset($_GET['district']) ? sanitizeInput($_GET['district']) : 'गाजीपुर';
    
    // Mock forecast data - in real implementation, integrate with weather API
    $forecast = [
        ['day' => 'आज', 'date' => date('Y-m-d'), 'high' => '30°C', 'low' => '22°C', 'condition' => 'धूप', 'rain_chance' => '0%', 'humidity' => '60%'],
        ['day' => 'कल', 'date' => date('Y-m-d', strtotime('+1 day')), 'high' => '32°C', 'low' => '24°C', 'condition' => 'धूप', 'rain_chance' => '10%', 'humidity' => '65%'],
        ['day' => 'परसों', 'date' => date('Y-m-d', strtotime('+2 days')), 'high' => '29°C', 'low' => '21°C', 'condition' => 'बारिश', 'rain_chance' => '80%', 'humidity' => '85%'],
        ['day' => 'बुधवार', 'date' => date('Y-m-d', strtotime('+3 days')), 'high' => '26°C', 'low' => '20°C', 'condition' => 'बादल', 'rain_chance' => '60%', 'humidity' => '75%'],
        ['day' => 'बृहस्पतिवार', 'date' => date('Y-m-d', strtotime('+4 days')), 'high' => '28°C', 'low' => '22°C', 'condition' => 'धूप', 'rain_chance' => '20%', 'humidity' => '65%']
    ];
    
    sendJsonResponse([
        'success' => true,
        'forecast' => array_slice($forecast, 0, $days),
        'district' => $district
    ]);
}

function getWeatherAlerts() {
    // Mock weather alerts
    $alerts = [
        [
            'type' => 'बारिश चेतावनी',
            'severity' => 'मध्यम',
            'message' => 'कल भारी बारिश की संभावना है। फसल की सुरक्षा के उपाय करें।',
            'valid_from' => date('Y-m-d H:i:s', strtotime('+1 day')),
            'valid_until' => date('Y-m-d H:i:s', strtotime('+2 days')),
            'recommendations' => [
                'खेतों में जल निकासी की व्यवस्था करें',
                'फसल को ढकने का प्रबंध करें',
                'कीटनाशक छिड़काव टाल दें'
            ]
        ],
        [
            'type' => 'तेज हवा चेतावनी',
            'severity' => 'कम',
            'message' => 'आने वाले दिनों में तेज हवा चल सकती है।',
            'valid_from' => date('Y-m-d H:i:s', strtotime('+3 days')),
            'valid_until' => date('Y-m-d H:i:s', strtotime('+4 days')),
            'recommendations' => [
                'पौधों को सहारा दें',
                'हल्की फसलों को बांधें'
            ]
        ]
    ];
    
    sendJsonResponse([
        'success' => true,
        'alerts' => $alerts
    ]);
}
?>
"""

with open('api/weather.php', 'w', encoding='utf-8') as f:
    f.write(weather_api)

# Create market prices API
market_api = """<?php
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
"""

with open('api/market.php', 'w', encoding='utf-8') as f:
    f.write(market_api)

# Create agricultural tips API
tips_api = """<?php
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
"""

with open('api/tips.php', 'w', encoding='utf-8') as f:
    f.write(tips_api)

print("Created: api/weather.php, api/market.php, api/tips.php")