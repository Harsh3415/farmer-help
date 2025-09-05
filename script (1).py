# Create comprehensive project files for Rural Farmer Helper Project

# First, let's create the database schema
database_schema = """
-- Krishi Sahayak (Rural Farmer Helper) Database Schema
-- Created for farmers in rural areas of India

-- Create database
CREATE DATABASE IF NOT EXISTS krishi_sahayak;
USE krishi_sahayak;

-- Farmers table to store farmer information
CREATE TABLE farmers (
    farmer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100),
    address TEXT,
    village VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(6),
    land_size DECIMAL(10,2), -- in acres
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Crops master table
CREATE TABLE crop_master (
    crop_id INT PRIMARY KEY AUTO_INCREMENT,
    crop_name_hindi VARCHAR(100) NOT NULL,
    crop_name_english VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- cereal, vegetable, fruit, cash_crop
    season VARCHAR(20), -- kharif, rabi, zaid
    duration_days INT, -- crop duration in days
    water_requirement VARCHAR(50),
    soil_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Farmer crops - crops being grown by farmers
CREATE TABLE farmer_crops (
    id INT PRIMARY KEY AUTO_INCREMENT,
    farmer_id INT,
    crop_id INT,
    field_name VARCHAR(100),
    field_size DECIMAL(8,2), -- in acres
    planting_date DATE,
    expected_harvest_date DATE,
    current_stage VARCHAR(100),
    progress_percentage INT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crop_master(crop_id)
);

-- Weather data table
CREATE TABLE weather_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    district VARCHAR(100),
    state VARCHAR(100),
    date DATE,
    temperature_max DECIMAL(5,2),
    temperature_min DECIMAL(5,2),
    humidity INT,
    rainfall DECIMAL(6,2),
    wind_speed DECIMAL(5,2),
    weather_condition VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market prices table
CREATE TABLE market_prices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    crop_id INT,
    market_name VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    price_per_quintal DECIMAL(10,2),
    price_date DATE,
    price_trend VARCHAR(10), -- up, down, stable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crop_id) REFERENCES crop_master(crop_id)
);

-- Agricultural tips and advisories
CREATE TABLE agri_tips (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200),
    content TEXT,
    category VARCHAR(100), -- disease, fertilizer, irrigation, etc.
    crop_id INT,
    season VARCHAR(20),
    language VARCHAR(10) DEFAULT 'hindi',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (crop_id) REFERENCES crop_master(crop_id)
);

-- Expert queries and responses
CREATE TABLE expert_queries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    farmer_id INT,
    crop_id INT,
    query_text TEXT,
    query_image_path VARCHAR(255),
    response_text TEXT,
    response_by VARCHAR(100),
    response_date TIMESTAMP,
    status ENUM('pending', 'answered', 'closed') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crop_master(crop_id)
);

-- Farm records - income, expense, yield tracking
CREATE TABLE farm_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    farmer_id INT,
    crop_id INT,
    record_type ENUM('income', 'expense', 'yield') NOT NULL,
    amount DECIMAL(12,2),
    quantity DECIMAL(10,2), -- for yield records
    unit VARCHAR(20), -- quintal, kg, etc.
    description TEXT,
    record_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crop_master(crop_id)
);

-- Government schemes information
CREATE TABLE government_schemes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scheme_name VARCHAR(200),
    description TEXT,
    eligibility_criteria TEXT,
    benefits TEXT,
    application_process TEXT,
    contact_info TEXT,
    scheme_type VARCHAR(100), -- subsidy, insurance, loan, etc.
    target_farmers VARCHAR(100), -- all, small, marginal, women, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Disease and pest information
CREATE TABLE crop_diseases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    crop_id INT,
    disease_name_hindi VARCHAR(150),
    disease_name_english VARCHAR(150),
    symptoms TEXT,
    treatment TEXT,
    prevention TEXT,
    affected_season VARCHAR(50),
    severity_level ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crop_id) REFERENCES crop_master(crop_id)
);

-- User sessions for login management
CREATE TABLE user_sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    farmer_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE
);

-- Insert sample data for testing

-- Insert crop master data
INSERT INTO crop_master (crop_name_hindi, crop_name_english, category, season, duration_days, water_requirement, soil_type) VALUES
('धान', 'Rice', 'cereal', 'kharif', 120, 'high', 'Clay, Loam'),
('गेहूं', 'Wheat', 'cereal', 'rabi', 150, 'medium', 'Loam, Sandy loam'),
('मक्का', 'Maize', 'cereal', 'kharif', 90, 'medium', 'Well-drained loam'),
('आलू', 'Potato', 'vegetable', 'rabi', 90, 'medium', 'Sandy loam'),
('प्याज', 'Onion', 'vegetable', 'rabi', 120, 'low', 'Well-drained loam'),
('टमाटर', 'Tomato', 'vegetable', 'all', 75, 'medium', 'Well-drained soil'),
('सरसों', 'Mustard', 'oilseed', 'rabi', 120, 'low', 'Loam'),
('कपास', 'Cotton', 'cash_crop', 'kharif', 180, 'medium', 'Black cotton soil'),
('गन्ना', 'Sugarcane', 'cash_crop', 'all', 365, 'high', 'Heavy loam'),
('दालें', 'Pulses', 'pulse', 'rabi', 100, 'low', 'Well-drained loam');

-- Insert sample government schemes
INSERT INTO government_schemes (scheme_name, description, benefits, scheme_type, target_farmers) VALUES
('प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)', 'सभी भूमिधारक किसानों को आर्थिक सहायता', 'रु. 6,000 प्रति वर्ष तीन किस्तों में', 'subsidy', 'all'),
('प्रधानमंत्री फसल बीमा योजना', 'फसल के नुकसान की स्थिति में बीमा सुरक्षा', 'प्राकृतिक आपदा से हुए नुकसान का मुआवजा', 'insurance', 'all'),
('मृदा स्वास्थ्य कार्ड योजना', 'मिट्टी की गुणवत्ता की जांच', 'मुफ्त मिट्टी जांच और सलाह', 'advisory', 'all'),
('किसान क्रेडिट कार्ड', 'कृषि के लिए आसान ऋण', 'कम ब्याज दर पर ऋण सुविधा', 'loan', 'all');

-- Insert sample agricultural tips
INSERT INTO agri_tips (title, content, category, season, crop_id) VALUES
('धान की रोपाई के लिए सही समय', 'मानसून की पहली बारिश के बाद धान की रोपाई करें। खेत में 2-3 सेमी पानी होना चाहिए।', 'plantation', 'kharif', 1),
('गेहूं में सिंचाई का सही समय', 'गेहूं में पहली सिंचाई बुआई के 20-25 दिन बाद करें। फिर 15-20 दिन के अंतराल पर सिंचाई करते रहें।', 'irrigation', 'rabi', 2),
('टमाटर में कीट नियंत्रण', 'टमाटर में सफेद मक्खी के नियंत्रण के लिए नीम का तेल का छिड़काव करें।', 'pest_control', 'all', 6);

-- Insert sample disease data  
INSERT INTO crop_diseases (crop_id, disease_name_hindi, disease_name_english, symptoms, treatment, prevention) VALUES
(1, 'ब्लास्ट', 'Rice Blast', 'पत्तियों पर भूरे रंग के धब्बे', 'कॉपर ऑक्सीक्लोराइड का छिड़काव', 'बीज उपचार और संतुलित उर्वरक का प्रयोग'),
(2, 'गेहूं का रस्ट', 'Wheat Rust', 'पत्तियों पर नारंगी रंग के पाउडर जैसे धब्बे', 'प्रोपिकोनाजोल का छिड़काव', 'प्रतिरोधी किस्म का चयन');

"""

# Save the database schema
with open('database_schema.sql', 'w', encoding='utf-8') as f:
    f.write(database_schema)

print("Database schema created: database_schema.sql")

# Create PHP configuration file
php_config = """<?php
// Database configuration for Krishi Sahayak
define('DB_HOST', 'localhost');
define('DB_USERNAME', 'root');
define('DB_PASSWORD', '');
define('DB_NAME', 'krishi_sahayak');

// Application configuration
define('APP_NAME', 'Krishi Sahayak');
define('APP_VERSION', '1.0.0');
define('UPLOAD_PATH', 'uploads/');
define('MAX_FILE_SIZE', 5242880); // 5MB

// Session configuration
ini_set('session.gc_maxlifetime', 86400); // 24 hours
session_set_cookie_params(86400); // 24 hours

// Database connection
class Database {
    private $host = DB_HOST;
    private $username = DB_USERNAME;
    private $password = DB_PASSWORD;
    private $database = DB_NAME;
    public $connection;
    
    public function __construct() {
        $this->connection = null;
        try {
            $this->connection = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->database,
                $this->username,
                $this->password
            );
            $this->connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->connection->exec("set names utf8");
        } catch(PDOException $exception) {
            echo "Connection error: " . $exception->getMessage();
        }
    }
    
    public function getConnection() {
        return $this->connection;
    }
}

// Common functions
function sanitizeInput($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

function generateSessionId() {
    return bin2hex(random_bytes(32));
}

function formatDate($date) {
    return date('d/m/Y', strtotime($date));
}

function formatDateTime($datetime) {
    return date('d/m/Y H:i', strtotime($datetime));
}

function uploadImage($file, $target_dir = 'uploads/') {
    $target_file = $target_dir . basename($file["name"]);
    $uploadOk = 1;
    $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));
    
    // Check if image file is actual image
    if(isset($_POST["submit"])) {
        $check = getimagesize($file["tmp_name"]);
        if($check !== false) {
            $uploadOk = 1;
        } else {
            $uploadOk = 0;
        }
    }
    
    // Check file size
    if ($file["size"] > MAX_FILE_SIZE) {
        $uploadOk = 0;
    }
    
    // Allow certain file formats
    if($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg") {
        $uploadOk = 0;
    }
    
    if ($uploadOk == 0) {
        return false;
    } else {
        if (move_uploaded_file($file["tmp_name"], $target_file)) {
            return $target_file;
        } else {
            return false;
        }
    }
}

// Response helper
function sendJsonResponse($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}
?>
"""

with open('config.php', 'w', encoding='utf-8') as f:
    f.write(php_config)

print("PHP configuration created: config.php")