# Create main API files for the Rural Farmer Helper project

# Create the main API router
api_index = """<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

require_once '../config.php';

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    http_response_code(200);
    exit();
}

$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($request_uri, PHP_URL_PATH);
$path_parts = explode('/', trim($path, '/'));

// Remove 'api' from path if present
if (isset($path_parts[0]) && $path_parts[0] === 'api') {
    array_shift($path_parts);
}

$endpoint = isset($path_parts[0]) ? $path_parts[0] : '';

switch ($endpoint) {
    case 'auth':
        require_once 'auth.php';
        break;
    case 'farmers':
        require_once 'farmers.php';
        break;
    case 'crops':
        require_once 'crops.php';
        break;
    case 'weather':
        require_once 'weather.php';
        break;
    case 'market':
        require_once 'market.php';
        break;
    case 'tips':
        require_once 'tips.php';
        break;
    case 'expert':
        require_once 'expert.php';
        break;
    case 'records':
        require_once 'records.php';
        break;
    case 'schemes':
        require_once 'schemes.php';
        break;
    default:
        sendJsonResponse(['error' => 'Endpoint not found'], 404);
}
?>
"""

with open('api/index.php', 'w', encoding='utf-8') as f:
    f.write(api_index)

# Create authentication API
auth_api = """<?php
require_once '../config.php';

$database = new Database();
$db = $database->getConnection();
$request_method = $_SERVER['REQUEST_METHOD'];

switch ($request_method) {
    case 'POST':
        if (isset($_GET['action'])) {
            switch ($_GET['action']) {
                case 'register':
                    registerFarmer();
                    break;
                case 'login':
                    loginFarmer();
                    break;
                case 'logout':
                    logoutFarmer();
                    break;
                default:
                    sendJsonResponse(['error' => 'Invalid action'], 400);
            }
        } else {
            loginFarmer(); // Default action
        }
        break;
    case 'GET':
        if (isset($_GET['action']) && $_GET['action'] === 'verify') {
            verifySession();
        } else {
            sendJsonResponse(['error' => 'Invalid request'], 400);
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function registerFarmer() {
    global $db;
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['name']) || !isset($input['phone'])) {
        sendJsonResponse(['error' => 'Name and phone are required'], 400);
    }
    
    $name = sanitizeInput($input['name']);
    $phone = sanitizeInput($input['phone']);
    $email = isset($input['email']) ? sanitizeInput($input['email']) : null;
    $address = isset($input['address']) ? sanitizeInput($input['address']) : null;
    $village = isset($input['village']) ? sanitizeInput($input['village']) : null;
    $district = isset($input['district']) ? sanitizeInput($input['district']) : null;
    $state = isset($input['state']) ? sanitizeInput($input['state']) : null;
    $pincode = isset($input['pincode']) ? sanitizeInput($input['pincode']) : null;
    $land_size = isset($input['land_size']) ? floatval($input['land_size']) : null;
    
    try {
        // Check if phone already exists
        $check_query = "SELECT farmer_id FROM farmers WHERE phone = :phone";
        $check_stmt = $db->prepare($check_query);
        $check_stmt->bindParam(':phone', $phone);
        $check_stmt->execute();
        
        if ($check_stmt->rowCount() > 0) {
            sendJsonResponse(['error' => 'Phone number already registered'], 400);
        }
        
        // Insert new farmer
        $query = "INSERT INTO farmers (name, phone, email, address, village, district, state, pincode, land_size) 
                  VALUES (:name, :phone, :email, :address, :village, :district, :state, :pincode, :land_size)";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':name', $name);
        $stmt->bindParam(':phone', $phone);
        $stmt->bindParam(':email', $email);
        $stmt->bindParam(':address', $address);
        $stmt->bindParam(':village', $village);
        $stmt->bindParam(':district', $district);
        $stmt->bindParam(':state', $state);
        $stmt->bindParam(':pincode', $pincode);
        $stmt->bindParam(':land_size', $land_size);
        
        $stmt->execute();
        $farmer_id = $db->lastInsertId();
        
        // Create session
        $session_id = generateSessionId();
        $expires_at = date('Y-m-d H:i:s', strtotime('+24 hours'));
        
        $session_query = "INSERT INTO user_sessions (session_id, farmer_id, expires_at) VALUES (:session_id, :farmer_id, :expires_at)";
        $session_stmt = $db->prepare($session_query);
        $session_stmt->bindParam(':session_id', $session_id);
        $session_stmt->bindParam(':farmer_id', $farmer_id);
        $session_stmt->bindParam(':expires_at', $expires_at);
        $session_stmt->execute();
        
        sendJsonResponse([
            'success' => true,
            'message' => 'Registration successful',
            'session_id' => $session_id,
            'farmer_id' => $farmer_id,
            'farmer' => [
                'name' => $name,
                'phone' => $phone,
                'email' => $email,
                'village' => $village,
                'district' => $district,
                'state' => $state
            ]
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Registration failed: ' . $exception->getMessage()], 500);
    }
}

function loginFarmer() {
    global $db;
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['phone'])) {
        sendJsonResponse(['error' => 'Phone number is required'], 400);
    }
    
    $phone = sanitizeInput($input['phone']);
    
    try {
        $query = "SELECT farmer_id, name, phone, email, village, district, state, land_size 
                  FROM farmers WHERE phone = :phone AND is_active = 1";
        $stmt = $db->prepare($query);
        $stmt->bindParam(':phone', $phone);
        $stmt->execute();
        
        if ($stmt->rowCount() === 0) {
            sendJsonResponse(['error' => 'Farmer not found'], 404);
        }
        
        $farmer = $stmt->fetch(PDO::FETCH_ASSOC);
        
        // Update last login
        $update_query = "UPDATE farmers SET last_login = CURRENT_TIMESTAMP WHERE farmer_id = :farmer_id";
        $update_stmt = $db->prepare($update_query);
        $update_stmt->bindParam(':farmer_id', $farmer['farmer_id']);
        $update_stmt->execute();
        
        // Create session
        $session_id = generateSessionId();
        $expires_at = date('Y-m-d H:i:s', strtotime('+24 hours'));
        
        // Clean old sessions
        $clean_query = "DELETE FROM user_sessions WHERE farmer_id = :farmer_id OR expires_at < NOW()";
        $clean_stmt = $db->prepare($clean_query);
        $clean_stmt->bindParam(':farmer_id', $farmer['farmer_id']);
        $clean_stmt->execute();
        
        $session_query = "INSERT INTO user_sessions (session_id, farmer_id, expires_at) VALUES (:session_id, :farmer_id, :expires_at)";
        $session_stmt = $db->prepare($session_query);
        $session_stmt->bindParam(':session_id', $session_id);
        $session_stmt->bindParam(':farmer_id', $farmer['farmer_id']);
        $session_stmt->bindParam(':expires_at', $expires_at);
        $session_stmt->execute();
        
        sendJsonResponse([
            'success' => true,
            'message' => 'Login successful',
            'session_id' => $session_id,
            'farmer' => $farmer
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Login failed: ' . $exception->getMessage()], 500);
    }
}

function verifySession() {
    global $db;
    
    $headers = getallheaders();
    $session_id = isset($headers['Authorization']) ? str_replace('Bearer ', '', $headers['Authorization']) : null;
    
    if (!$session_id) {
        sendJsonResponse(['error' => 'Session ID required'], 401);
    }
    
    try {
        $query = "SELECT s.farmer_id, f.name, f.phone, f.email, f.village, f.district, f.state, f.land_size 
                  FROM user_sessions s 
                  JOIN farmers f ON s.farmer_id = f.farmer_id 
                  WHERE s.session_id = :session_id AND s.expires_at > NOW() AND s.is_active = 1";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':session_id', $session_id);
        $stmt->execute();
        
        if ($stmt->rowCount() === 0) {
            sendJsonResponse(['error' => 'Invalid or expired session'], 401);
        }
        
        $farmer = $stmt->fetch(PDO::FETCH_ASSOC);
        
        sendJsonResponse([
            'success' => true,
            'farmer' => $farmer
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Session verification failed'], 500);
    }
}

function logoutFarmer() {
    global $db;
    
    $headers = getallheaders();
    $session_id = isset($headers['Authorization']) ? str_replace('Bearer ', '', $headers['Authorization']) : null;
    
    if ($session_id) {
        try {
            $query = "UPDATE user_sessions SET is_active = 0 WHERE session_id = :session_id";
            $stmt = $db->prepare($query);
            $stmt->bindParam(':session_id', $session_id);
            $stmt->execute();
        } catch (PDOException $exception) {
            // Silent fail for logout
        }
    }
    
    sendJsonResponse(['success' => true, 'message' => 'Logged out successfully']);
}
?>
"""

with open('api/auth.php', 'w', encoding='utf-8') as f:
    f.write(auth_api)

print("Created: api/index.php, api/auth.php")

# Create crops API
crops_api = """<?php
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
                case 'master':
                    getCropMaster();
                    break;
                case 'farmer_crops':
                    $farmer_id = verifyFarmerSession();
                    getFarmerCrops($farmer_id);
                    break;
                case 'crop_details':
                    if (isset($_GET['crop_id'])) {
                        getCropDetails($_GET['crop_id']);
                    } else {
                        sendJsonResponse(['error' => 'Crop ID required'], 400);
                    }
                    break;
                case 'diseases':
                    if (isset($_GET['crop_id'])) {
                        getCropDiseases($_GET['crop_id']);
                    } else {
                        getAllDiseases();
                    }
                    break;
                default:
                    sendJsonResponse(['error' => 'Invalid action'], 400);
            }
        } else {
            getCropMaster();
        }
        break;
    case 'POST':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['action']) && $_GET['action'] === 'add') {
            addFarmerCrop($farmer_id);
        } else {
            sendJsonResponse(['error' => 'Invalid action'], 400);
        }
        break;
    case 'PUT':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['crop_id'])) {
            updateFarmerCrop($farmer_id, $_GET['crop_id']);
        } else {
            sendJsonResponse(['error' => 'Crop ID required'], 400);
        }
        break;
    case 'DELETE':
        $farmer_id = verifyFarmerSession();
        if (isset($_GET['crop_id'])) {
            deleteFarmerCrop($farmer_id, $_GET['crop_id']);
        } else {
            sendJsonResponse(['error' => 'Crop ID required'], 400);
        }
        break;
    default:
        sendJsonResponse(['error' => 'Method not allowed'], 405);
}

function getCropMaster() {
    global $db;
    
    try {
        $query = "SELECT crop_id, crop_name_hindi, crop_name_english, category, season, duration_days, water_requirement, soil_type FROM crop_master ORDER BY crop_name_hindi";
        $stmt = $db->prepare($query);
        $stmt->execute();
        
        $crops = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        sendJsonResponse([
            'success' => true,
            'crops' => $crops
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch crops: ' . $exception->getMessage()], 500);
    }
}

function getFarmerCrops($farmer_id) {
    global $db;
    
    try {
        $query = "SELECT fc.*, cm.crop_name_hindi, cm.crop_name_english, cm.category, cm.season, cm.duration_days
                  FROM farmer_crops fc 
                  JOIN crop_master cm ON fc.crop_id = cm.crop_id 
                  WHERE fc.farmer_id = :farmer_id 
                  ORDER BY fc.planting_date DESC";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':farmer_id', $farmer_id);
        $stmt->execute();
        
        $crops = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        // Calculate progress and days to harvest for each crop
        foreach ($crops as &$crop) {
            $plant_date = new DateTime($crop['planting_date']);
            $harvest_date = new DateTime($crop['expected_harvest_date']);
            $current_date = new DateTime();
            
            $total_days = $plant_date->diff($harvest_date)->days;
            $elapsed_days = $plant_date->diff($current_date)->days;
            
            if ($current_date <= $harvest_date) {
                $crop['progress_percentage'] = min(100, round(($elapsed_days / $total_days) * 100));
                $crop['days_to_harvest'] = $current_date->diff($harvest_date)->days;
            } else {
                $crop['progress_percentage'] = 100;
                $crop['days_to_harvest'] = 0;
                $crop['status'] = 'हार्वेस्ट का समय हो गया';
            }
        }
        
        sendJsonResponse([
            'success' => true,
            'crops' => $crops
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch farmer crops: ' . $exception->getMessage()], 500);
    }
}

function addFarmerCrop($farmer_id) {
    global $db;
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['crop_id']) || !isset($input['field_name']) || !isset($input['field_size']) || !isset($input['planting_date'])) {
        sendJsonResponse(['error' => 'Required fields: crop_id, field_name, field_size, planting_date'], 400);
    }
    
    $crop_id = intval($input['crop_id']);
    $field_name = sanitizeInput($input['field_name']);
    $field_size = floatval($input['field_size']);
    $planting_date = sanitizeInput($input['planting_date']);
    $expected_harvest_date = isset($input['expected_harvest_date']) ? sanitizeInput($input['expected_harvest_date']) : null;
    $current_stage = isset($input['current_stage']) ? sanitizeInput($input['current_stage']) : 'बुआई';
    $notes = isset($input['notes']) ? sanitizeInput($input['notes']) : null;
    
    try {
        // If harvest date not provided, calculate based on crop duration
        if (!$expected_harvest_date) {
            $duration_query = "SELECT duration_days FROM crop_master WHERE crop_id = :crop_id";
            $duration_stmt = $db->prepare($duration_query);
            $duration_stmt->bindParam(':crop_id', $crop_id);
            $duration_stmt->execute();
            $duration_result = $duration_stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($duration_result) {
                $expected_harvest_date = date('Y-m-d', strtotime($planting_date . ' + ' . $duration_result['duration_days'] . ' days'));
            }
        }
        
        $query = "INSERT INTO farmer_crops (farmer_id, crop_id, field_name, field_size, planting_date, expected_harvest_date, current_stage, notes) 
                  VALUES (:farmer_id, :crop_id, :field_name, :field_size, :planting_date, :expected_harvest_date, :current_stage, :notes)";
        
        $stmt = $db->prepare($query);
        $stmt->bindParam(':farmer_id', $farmer_id);
        $stmt->bindParam(':crop_id', $crop_id);
        $stmt->bindParam(':field_name', $field_name);
        $stmt->bindParam(':field_size', $field_size);
        $stmt->bindParam(':planting_date', $planting_date);
        $stmt->bindParam(':expected_harvest_date', $expected_harvest_date);
        $stmt->bindParam(':current_stage', $current_stage);
        $stmt->bindParam(':notes', $notes);
        
        $stmt->execute();
        
        sendJsonResponse([
            'success' => true,
            'message' => 'Crop added successfully',
            'crop_id' => $db->lastInsertId()
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to add crop: ' . $exception->getMessage()], 500);
    }
}

function getCropDiseases($crop_id) {
    global $db;
    
    try {
        $query = "SELECT * FROM crop_diseases WHERE crop_id = :crop_id ORDER BY severity_level DESC";
        $stmt = $db->prepare($query);
        $stmt->bindParam(':crop_id', $crop_id);
        $stmt->execute();
        
        $diseases = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        sendJsonResponse([
            'success' => true,
            'diseases' => $diseases
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch diseases: ' . $exception->getMessage()], 500);
    }
}

function getAllDiseases() {
    global $db;
    
    try {
        $query = "SELECT cd.*, cm.crop_name_hindi, cm.crop_name_english 
                  FROM crop_diseases cd 
                  JOIN crop_master cm ON cd.crop_id = cm.crop_id 
                  ORDER BY cm.crop_name_hindi, cd.severity_level DESC";
        
        $stmt = $db->prepare($query);
        $stmt->execute();
        
        $diseases = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        sendJsonResponse([
            'success' => true,
            'diseases' => $diseases
        ]);
        
    } catch (PDOException $exception) {
        sendJsonResponse(['error' => 'Failed to fetch diseases: ' . $exception->getMessage()], 500);
    }
}
?>
"""

with open('api/crops.php', 'w', encoding='utf-8') as f:
    f.write(crops_api)

print("Created: api/crops.php")