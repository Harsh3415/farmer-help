<?php
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
