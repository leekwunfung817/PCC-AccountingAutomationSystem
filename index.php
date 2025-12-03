<?php
// index.php
require_once __DIR__ . '/config.php';

$db = get_db();
$error = '';
$success = '';

// ---------- DOWNLOAD HANDLER (GET) ----------
if (isset($_GET['download']) && isset($_GET['id'])) {
    $id = (int) $_GET['id'];
    $type = $_GET['download'];

    if ($type === 'original') {
        // Original upload: from pdf_files
        $stmt = $db->prepare("SELECT filename, original_name FROM pdf_files WHERE id = :id");
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($row) {
            $stored = $row['filename'];
            $origName = $row['original_name'];
            $path = UPLOAD_DIR . $stored;

            if (is_file($path)) {
                header('Content-Description: File Transfer');
                header('Content-Type: application/pdf');
                header('Content-Disposition: attachment; filename="' . rawurlencode($origName) . '"');
                header('Content-Length: ' . filesize($path));
                readfile($path);
                exit;
            } else {
                $error = 'Original file not found on server.';
            }
        } else {
            $error = 'Record not found.';
        }
    } elseif ($type === 'processed') {
        // Processed file: via join to pdf_processed_files
        $stmt = $db->prepare("
            SELECT pf.processed_name
            FROM pdf_processed_files pf
            WHERE pf.pdf_id = :id
        ");
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($row) {
            $processedName = $row['processed_name'];
            $path = PROCESSED_DIR . $processedName;

            if (is_file($path)) {
                // Download with the processed filename (the "new name")
                header('Content-Description: File Transfer');
                header('Content-Type: application/pdf');
                header('Content-Disposition: attachment; filename="' . rawurlencode($processedName) . '"');
                header('Content-Length: ' . filesize($path));
                readfile($path);
                exit;
            } else {
                $error = 'Processed file not found on server.';
            }
        } else {
            $error = 'No processed file recorded for this PDF.';
        }
    } else {
        $error = 'Invalid download type.';
    }
}

// ---------- POST HANDLER (UPLOAD / DELETE) ----------
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // DELETE
    if (isset($_POST['delete_id'])) {
        $id = (int) $_POST['delete_id'];
        try {
            // Get stored + processed filenames
            $stmt = $db->prepare("
                SELECT f.filename, f.original_name, p.processed_name
                FROM pdf_files f
                LEFT JOIN pdf_processed_files p ON p.pdf_id = f.id
                WHERE f.id = :id
            ");
            $stmt->execute([':id' => $id]);
            $pdf = $stmt->fetch(PDO::FETCH_ASSOC);

            if (!$pdf) {
                $error = 'PDF record not found.';
            } else {
                $stored = $pdf['filename'];
                $processedName = $pdf['processed_name'] ?? null;

                // Delete physical files if present
                $paths = [
                    UPLOAD_DIR . $stored,
                ];
                if ($processedName) {
                    $paths[] = PROCESSED_DIR . $processedName;
                }
                foreach ($paths as $path) {
                    if (is_file($path)) {
                        @unlink($path);
                    }
                }

                // Delete DB record in pdf_files (pdf_processed_files is ON DELETE CASCADE)
                $stmt = $db->prepare("DELETE FROM pdf_files WHERE id = :id");
                $stmt->execute([':id' => $id]);

                $success = 'PDF "' . $pdf['original_name'] . '" and its related records were deleted.';
            }
        } catch (Exception $e) {
            $error = 'Failed to delete PDF: ' . $e->getMessage();
        }

    // UPLOAD (multiple)
    } elseif (isset($_FILES['pdf_files'])) {
        $files = $_FILES['pdf_files'];

        // Normalize / count
        $total = is_array($files['name']) ? count($files['name']) : 0;

        if ($total === 0) {
            $error = 'No files selected.';
        } else {
            $uploadedCount = 0;
            $errorMessages = [];

            for ($i = 0; $i < $total; $i++) {
                // Skip completely empty slots
                if ($files['error'][$i] === UPLOAD_ERR_NO_FILE) {
                    continue;
                }

                $fileError = $files['error'][$i];
                $tmpName   = $files['tmp_name'][$i];
                $origName  = $files['name'][$i];

                if ($fileError !== UPLOAD_ERR_OK) {
                    $errorMessages[] = $origName . ': upload failed.';
                    continue;
                }

                $ext = strtolower(pathinfo($origName, PATHINFO_EXTENSION));
                if ($ext !== 'pdf') {
                    $errorMessages[] = $origName . ': only PDF files are allowed.';
                    continue;
                }

                $safeName    = bin2hex(random_bytes(8)) . '.pdf';
                $destination = UPLOAD_DIR . $safeName;

                if (!move_uploaded_file($tmpName, $destination)) {
                    $errorMessages[] = $origName . ': could not save the file.';
                    continue;
                }

                // Insert into DB
                $stmt = $db->prepare("
                    INSERT INTO pdf_files (filename, original_name, status)
                    VALUES (:filename, :original_name, 'pending')
                ");
                $stmt->execute([
                    ':filename'      => $safeName,
                    ':original_name' => $origName,
                ]);

                $uploadedCount++;
            }

            if ($uploadedCount > 0) {
                $success = "Uploaded and queued {$uploadedCount} file(s) for processing.";
            }

            if (!empty($errorMessages)) {
                // Merge multiple errors into one string for display
                $error = implode(' ', $errorMessages);
            }
        }
    }

}

// ---------- LOAD LIST: JOIN PROCESSED FILENAMES ----------
$stmt = $db->query("
    SELECT f.*, p.processed_name
    FROM pdf_files f
    LEFT JOIN pdf_processed_files p ON p.pdf_id = f.id
    ORDER BY f.uploaded_at DESC
");
$pdfs = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PDF Upload & Status</title>
    <script src="tailwind.js"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Top nav -->
    <?php require_once './TopNav.php'; ?>

    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 w-full">
        <!-- Upload card -->
        <section class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 w-full">

            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-lg font-semibold text-slate-900">Upload PDF</h1>
                    <p class="text-sm text-slate-500 mt-1">Upload PDFs to queue them for Python processing.</p>
                </div>
            </div>

            <div class="mt-4 space-y-3">
                <?php if ($error): ?>
                    <div class="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                        <?= htmlspecialchars($error) ?>
                    </div>
                <?php endif; ?>
                <?php if ($success): ?>
                    <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                        <?= htmlspecialchars($success) ?>
                    </div>
                <?php endif; ?>

                <form method="post" enctype="multipart/form-data" class="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                    <input
                        type="file"
                        name="pdf_files[]"
                        accept="application/pdf"
                        multiple
                        required
                        class="block w-full text-sm text-slate-700
                               file:mr-4 file:py-2 file:px-4
                               file:rounded-full file:border-0
                               file:text-sm file:font-semibold
                               file:bg-slate-900 file:text-slate-50
                               hover:file:bg-slate-700"
                    />

                    <button
                        type="submit"
                        class="inline-flex items-center justify-center rounded-full bg-emerald-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
                    >
                        Upload & Queue
                    </button>
                </form>

                <p class="text-xs text-slate-400">
                    After uploading, run <code class="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-[11px]">python3 process_pdfs.py</code> to process pending files.
                </p>
            </div>
        </section>

        <!-- Status table -->
        <section class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 w-full">

            <div class="flex items-center justify-between mb-3">
                <div>
                    <h2 class="text-lg font-semibold text-slate-900">Processing Status</h2>
                    <p class="text-sm text-slate-500 mt-1">
                        Download the original upload or the processed file (when available).
                    </p>
                </div>
            </div>

            <?php if (empty($pdfs)): ?>
                <div class="py-10 text-center">
                    <p class="text-sm text-slate-400">No PDFs uploaded yet.</p>
                </div>
            <?php else: ?>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-200 text-sm">
                        <thead class="bg-slate-50">
                            <tr>
                                <!-- <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">ID</th> -->
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">File</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">Status</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">Uploaded</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">Processed</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                        <?php foreach ($pdfs as $pdf): ?>
                            <tr class="hover:bg-slate-50/60">
                                <!-- <td class="px-3 py-2 text-slate-700">#<?= (int)$pdf['id'] ?></td> -->
                                <td class="px-3 py-2">
                                    <div class="text-slate-900"><?= htmlspecialchars($pdf['original_name']) ?></div>
                                    <div class="text-[11px] text-slate-400">
                                        Stored: <?= htmlspecialchars($pdf['filename']) ?>
                                    </div>
                                    <?php if (!empty($pdf['processed_name'])): ?>
                                        <div class="text-slate-600">
                                            <?= htmlspecialchars($pdf['processed_name']) ?>
                                        </div>
                                    <?php endif; ?>



                                    <!-- Download original -->
                                    <a
                                        href="index.php?download=original&id=<?= (int)$pdf['id'] ?>"
                                        class="inline-flex items-center rounded-full bg-slate-200 px-3 py-1 text-xs font-medium text-slate-800 hover:bg-slate-300"
                                    >
                                        Download Original
                                    </a>

                                    <!-- Download processed (only if exists) -->
                                    <?php if (!empty($pdf['processed_name'])): ?>
                                        <a
                                            href="index.php?download=processed&id=<?= (int)$pdf['id'] ?>"
                                            class="inline-flex items-center rounded-full bg-blue-500 px-3 py-1 text-xs font-medium text-white hover:bg-blue-600"
                                        >
                                            Download Processed
                                        </a>
                                    <?php endif; ?>

                                    <!-- Delete -->
                                    <form
                                        method="post"
                                        class="inline-block"
                                        onsubmit="return confirm('Delete this PDF and its related processed file?');"
                                    >
                                        <input type="hidden" name="delete_id" value="<?= (int)$pdf['id'] ?>">
                                        <button
                                            type="submit"
                                            class="inline-flex items-center rounded-full bg-red-500 px-3 py-1 text-xs font-medium text-white hover:bg-red-600"
                                        >
                                            Delete
                                        </button>
                                    </form>
                                </td>
                                <td class="px-3 py-2">
                                    <?= status_badge($pdf['status']) ?>
                                </td>
                                <td class="px-3 py-2 text-slate-600 text-xs"><?= htmlspecialchars($pdf['uploaded_at']) ?></td>
                                <td class="px-3 py-2 text-slate-600 text-xs">
                                    <?= htmlspecialchars($pdf['processed_at'] ?? '-') ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </section>
    </main>
</body>
</html>
