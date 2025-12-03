<?php
// config.php

// File paths (for PDFs)
define('UPLOAD_DIR', __DIR__ . '/uploads/');
define('PROCESSED_DIR', __DIR__ . '/processed/');

// Ensure directories exist
if (!is_dir(UPLOAD_DIR)) {
    mkdir(UPLOAD_DIR, 0777, true);
}
if (!is_dir(PROCESSED_DIR)) {
    mkdir(PROCESSED_DIR, 0777, true);
}

// MariaDB connection settings
define('DB_HOST', 'localhost');
define('DB_NAME', 'pcc_accounting');
define('DB_USER', 'root');
define('DB_PASS', '');

// Create PDO connection, DB, and table if not exist
function get_db() {
    static $pdo = null;

    if ($pdo === null) {
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ];

        // 1) Connect to server (no DB yet)
        $serverDsn = 'mysql:host=' . DB_HOST . ';charset=utf8mb4';
        $pdoServer = new PDO($serverDsn, DB_USER, DB_PASS, $options);

        // 2) Create database if not exists
        $dbName = DB_NAME;
        $pdoServer->exec("CREATE DATABASE IF NOT EXISTS `$dbName` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");

        // 3) Connect to the database
        $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4';
        $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);

        // 4) Create main table if not exists (unchanged)
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS pdf_files (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,           -- stored name in uploads/
                original_name VARCHAR(255) NOT NULL,      -- original upload name
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                info TEXT NULL,
                uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processed_at DATETIME NULL,
                INDEX (status),
                INDEX (uploaded_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ");

        // 5) NEW: table to store processed file names
        $pdo->exec("
            CREATE TABLE IF NOT EXISTS pdf_processed_files (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                pdf_id INT UNSIGNED NOT NULL,
                processed_name VARCHAR(255) NOT NULL,     -- stored name in processed/
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_pdf (pdf_id),
                CONSTRAINT fk_pdf_id
                    FOREIGN KEY (pdf_id) REFERENCES pdf_files(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ");

    }

    return $pdo;
}

// Helper: fetch all PDFs
function get_all_pdfs() {
    $db = get_db();
    $stmt = $db->query("SELECT * FROM pdf_files ORDER BY uploaded_at DESC");
    return $stmt->fetchAll();
}

// Helper: Tailwind status badge
function status_badge($status) {
    $map = [
        'pending'    => 'bg-yellow-100 text-yellow-800',
        'processing' => 'bg-sky-100 text-sky-800',
        'done'       => 'bg-green-100 text-green-800',
        'error'      => 'bg-red-100 text-red-800',
    ];
    $classes = $map[$status] ?? 'bg-gray-100 text-gray-800';

    return '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ' .
        htmlspecialchars($classes) . '">' . htmlspecialchars(ucfirst($status)) . '</span>';
}
