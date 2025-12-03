<?php
// info.php
require_once __DIR__ . '/config.php';

$pdfs = get_all_pdfs();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PDF Information</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Top nav -->
    <?php require_once './TopNav.php'; ?>

    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <section class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div class="flex items-center justify-between mb-3">
                <div>
                    <h1 class="text-lg font-semibold text-slate-900">PDF Information</h1>
                    <p class="text-sm text-slate-500 mt-1">Details extracted by the Python process.</p>
                </div>
            </div>

            <?php if (empty($pdfs)): ?>
                <p class="text-sm text-slate-400">No PDFs available yet.</p>
            <?php else: ?>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-200 text-sm">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">ID</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">File</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">Pages</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">Size (KB)</th>
                                <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500">Status</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                        <?php foreach ($pdfs as $pdf): ?>
                            <?php
                            $info = [];
                            if (!empty($pdf['info'])) {
                                $decoded = json_decode($pdf['info'], true);
                                if (is_array($decoded)) {
                                    $info = $decoded;
                                }
                            }
                            $pages = $info['pages'] ?? null;
                            $size_kb = $info['size_kb'] ?? null;
                            ?>
                            <tr class="hover:bg-slate-50/60">
                                <td class="px-3 py-2 text-slate-700">#<?= (int)$pdf['id'] ?></td>
                                <td class="px-3 py-2">
                                    <div class="text-slate-900"><?= htmlspecialchars($pdf['original_name']) ?></div>
                                    <div class="text-[11px] text-slate-400">Stored as: <?= htmlspecialchars($pdf['filename']) ?></div>
                                </td>
                                <td class="px-3 py-2 text-slate-700">
                                    <?= $pages !== null ? (int)$pages : '-' ?>
                                </td>
                                <td class="px-3 py-2 text-slate-700">
                                    <?= $size_kb !== null ? number_format($size_kb, 1) : '-' ?>
                                </td>
                                <td class="px-3 py-2">
                                    <?= status_badge($pdf['status']) ?>
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
