<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *'); // Optional: for cross-origin if needed

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['file']) && $_FILES['file']['error'] === 0) {
        $uploadDir = __DIR__ . '/../../processed/';
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0777, true);
        }
        $fileName = uniqid('proc_', true) . '_' . basename($_FILES['file']['name']);
        $filePath = $uploadDir . $fileName;
        if (move_uploaded_file($_FILES['file']['tmp_name'], $filePath)) {
            echo json_encode(['success' => true, 'processed_id' => $fileName]);
        } else {
            echo json_encode(['success' => false, 'message' => 'Failed to move file']);
        }
    } else {
        echo json_encode(['success' => false, 'message' => 'No file uploaded or error']);
    }
} else {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
}

?>