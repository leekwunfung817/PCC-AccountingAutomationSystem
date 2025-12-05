
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Budget File</title>
    <script src="tailwind.js"></script>
</head>
<body class="">
    <?php require_once './TopNav.php'; ?>


    <div class="bg-gray-100 min-h-screen flex flex-col items-center py-10">
        <div class="bg-white p-6 rounded shadow-md w-full max-w-md mb-8">
            <h1 class="text-2xl font-bold mb-4 text-center">Upload Budget Expense Xlsx</h1>
            <form action="" method="POST" enctype="multipart/form-data" class="space-y-4">
                <input type="file" name="budget_file" class="block w-full text-sm text-gray-700 border border-gray-300 rounded p-2">
                <button type="submit" name="upload" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                    Upload
                </button>
            </form>

            <?php
            $uploadDir = __DIR__ . '/budget_expense/';
            if (isset($_POST['upload'])) {
                if (isset($_FILES['budget_file']) && $_FILES['budget_file']['error'] === 0) {
                    $filename = $_FILES['budget_file']['name'];
                    $fileTmpPath = $_FILES['budget_file']['tmp_name'];
                    $fileSize = $_FILES['budget_file']['size'];
                    $fileType = mime_content_type($fileTmpPath);
                    $uploadDate = date("Y-m-d H:i:s");

                    if (preg_match('/^\d{4}_Budget_Expense\.xlsx$/', $filename)) {
                        $allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
                        if (in_array($fileType, $allowedTypes)) {
                            if (!is_dir($uploadDir)) {
                                mkdir($uploadDir, 0777, true);
                            }
                            $destination = $uploadDir . $filename;
                            move_uploaded_file($fileTmpPath, $destination);

                            echo "<div class='mt-4 p-4 bg-green-100 rounded'>
                                    <p class='text-green-700 font-semibold'>File uploaded successfully!</p>
                                    <ul class='mt-2 text-gray-700 text-sm'>
                                        <li><strong>Name:</strong> $filename</li>
                                        <li><strong>Size:</strong> " . round($fileSize / 1024, 2) . " KB</li>
                                        <li><strong>MIME Type:</strong> $fileType</li>
                                        <li><strong>Upload Date:</strong> $uploadDate</li>
                                    </ul>
                                  </div>";
                        } else {
                            echo "<p class='text-red-600 mt-4'>Invalid file type. Only .xlsx files are allowed.</p>";
                        }
                    } else {
                        echo "<p class='text-red-600 mt-4'>Invalid file name format. Please use YYYY_Budget_Expense.xlsx</p>";
                    }
                } else {
                    echo "<p class='text-red-600 mt-4'>Please select a file to upload.</p>";
                }
            }
            ?>
        </div>

        <!-- Display all uploaded files -->
        <div class="bg-white p-6 rounded shadow-md w-full max-w-3xl">
            <h2 class="text-xl font-bold mb-4">Uploaded Files</h2>
            <?php
            if (is_dir($uploadDir)) {
                $files = array_diff(scandir($uploadDir), ['.', '..']);
                if (count($files) > 0) {
                    echo "<table class='table-auto w-full border-collapse border border-gray-300'>
                            <thead>
                                <tr class='bg-gray-200'>
                                    <th class='border px-4 py-2'>File Name</th>
                                    <th class='border px-4 py-2'>Size</th>
                                    <th class='border px-4 py-2'>Upload Date</th>
                                    <th class='border px-4 py-2'>MIME Type</th>
                                </tr>
                            </thead>
                            <tbody>";
                    foreach ($files as $file) {
                        if (str_starts_with($file, "~")) {
                            continue;
                        }
                        $filePath = $uploadDir . $file;
                        $size = round(filesize($filePath) / 1024, 2) . ' KB';
                        $mime = mime_content_type($filePath);
                        $uploadDate = date("Y-m-d H:i:s", filemtime($filePath));
                        echo "<tr>
                                <td class='border px-4 py-2'>$file</td>
                                <td class='border px-4 py-2'>$size</td>
                                <td class='border px-4 py-2'>$uploadDate</td>
                                <td class='border px-4 py-2'>$mime</td>
                              </tr>";
                    }
                    echo "</tbody></table>";
                } else {
                    echo "<p class='text-gray-600'>No files uploaded yet.</p>";
                }
            } else {
                echo "<p class='text-gray-600'>Upload directory not found.</p>";
            }
            ?>
        </div>
    </div>

</body>
</html>
