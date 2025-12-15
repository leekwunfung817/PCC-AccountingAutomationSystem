<?php
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['file_id'])) {
    $fileId = basename($_GET['file_id']); // Sanitize to prevent path traversal
    $filePath = __DIR__ . '/../../uploads/' . $fileId;
    if (file_exists($filePath)) {
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($filePath) . '"');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($filePath));
        readfile($filePath);
        exit;
    } else {
        http_response_code(404);
        echo 'File not found';
    }
} else {
    http_response_code(400);
    echo 'Invalid request';
}
?>