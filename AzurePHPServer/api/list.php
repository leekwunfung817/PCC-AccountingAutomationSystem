<?php
header('Content-Type: application/json');

$base = __DIR__ . '/../../';
$type = $_GET['type'] ?? '';

if ($type === 'original') {
    $dir = $base . 'uploads/';
} elseif ($type === 'processed') {
    $dir = $base . 'processed/';
} else {
    echo json_encode([]);
    exit;
}

$files = [];
if (is_dir($dir)) {
    foreach (scandir($dir) as $file) {
        if ($file === '.' || $file === '..') continue;
        $path = $dir . $file;
        $files[] = [
            'name' => $file,
            'mtime' => filemtime($path)
        ];
    }
}
echo json_encode($files);

?>