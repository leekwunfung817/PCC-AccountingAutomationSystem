<?php
require_once __DIR__ . '/config.php';
$pdo = get_db();

$pdo->exec("
CREATE TABLE IF NOT EXISTS `budget_expense` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    FileName VARCHAR(255) NOT NULL,
    Tab VARCHAR(100) NOT NULL,
    GI_name VARCHAR(255) NOT NULL,
    Statistics VARCHAR(50) NOT NULL,
    January DECIMAL(15,2) DEFAULT 0,
    February DECIMAL(15,2) DEFAULT 0,
    March DECIMAL(15,2) DEFAULT 0,
    April DECIMAL(15,2) DEFAULT 0,
    May DECIMAL(15,2) DEFAULT 0,
    June DECIMAL(15,2) DEFAULT 0,
    July DECIMAL(15,2) DEFAULT 0,
    August DECIMAL(15,2) DEFAULT 0,
    September DECIMAL(15,2) DEFAULT 0,
    October DECIMAL(15,2) DEFAULT 0,
    November DECIMAL(15,2) DEFAULT 0,
    December DECIMAL(15,2) DEFAULT 0,
    Total DECIMAL(15,2) DEFAULT 0,
    UNIQUE KEY unique_entry (FileName, Tab, GI_name, Statistics)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
");

try {
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $sqlFile = './budget_expense.sql';
    $sqlContent = file_get_contents($sqlFile);
    $statements = explode(';', $sqlContent);
    foreach ($statements as $stmt) {
        $stmt = trim($stmt);
        echo "$stmt";
        if (!empty($stmt)) {
            $pdo->exec($stmt);
        }
    }
    echo "SQL file executed successfully!";
} catch (PDOException $e) {
    echo "Error: " . $e->getMessage();
}
?>