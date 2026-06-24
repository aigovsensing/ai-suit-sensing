
CREATE DATABASE IF NOT EXISTS ai_lawsuits;
USE ai_lawsuits;

CREATE TABLE IF NOT EXISTS lawsuits (
id INT AUTO_INCREMENT PRIMARY KEY,
case_name TEXT,
company VARCHAR(255),
court VARCHAR(255),
state VARCHAR(10),
file_date DATE,
case_type VARCHAR(100),
url TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
UNIQUE KEY unique_case (case_name(255), file_date)
);
