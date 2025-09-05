# Create main API files for the Rural Farmer Helper project

# Create the main API router
api_index = """<?php
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

require_once 'config.php';

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

print("API files created: api/index.php, api/auth.php")