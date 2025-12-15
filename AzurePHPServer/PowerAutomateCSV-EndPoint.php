<?php
// receive_csv.php

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo 'Method Not Allowed';
    exit;
}

// Read the raw POST body (this contains your CSV string from "Create CSV table")
$csvContent = file_get_contents('php://input');

if ($csvContent === false || $csvContent === '') {
    http_response_code(400);
    echo 'No CSV data received';
    exit;
}

// Optional: Basic validation - check if it looks like CSV (has at least one line break)
if (strpos($csvContent, "\n") === false && strpos($csvContent, "\r") === false) {
    // You can make this stricter if needed
    // http_response_code(400);
    // echo 'Invalid CSV format';
    // exit;
}

// Generate a unique filename (e.g., csv_20251212_143000.csv)
$timestamp = date('Ymd_His');
$filename = 'received_csv_' . $timestamp . '.csv';
$filePath = __DIR__ . '/' . $filename;  // Saves in the same directory as this script

// Save the CSV to a file
if (file_put_contents($filePath, $csvContent) === false) {
    http_response_code(500);
    echo 'Failed to save CSV file';
    exit;
}

// Optional: Parse the CSV into an array for further processing
$lines = array_map('str_getcsv', explode("\n", trim($csvContent)));
// Or use a temporary file handle for large CSVs:
// $temp = tmpfile();
// fwrite($temp, $csvContent);
// rewind($temp);
// $lines = [];
// while (($row = fgetcsv($temp)) !== false) {
//     $lines[] = $row;
// }
// fclose($temp);

// Example: Do something with the parsed data (e.g., insert into DB)
// foreach ($lines as $row) {
//     // Process each row
// }

// Respond with success (Power Automate will see 200 OK)
http_response_code(200);
echo 'CSV received and saved as ' . $filename;
?>