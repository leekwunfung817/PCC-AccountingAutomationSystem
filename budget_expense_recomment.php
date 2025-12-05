<?php
/***********************
 *  budget_grid.php
 ***********************/

require_once __DIR__ . '/config.php';
$pdo = get_db();
// // --- DB connection (adjust to your environment) ---
// $dsn  = 'mysql:host=localhost;dbname=your_db;charset=utf8mb4';
// $user = 'your_user';
// $pass = 'your_password';

// try {
//     $pdo = new PDO($dsn, $user, $pass, [
//         PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
//     ]);
// } catch (PDOException $e) {
//     die("DB connection failed: " . htmlspecialchars($e->getMessage()));
// }

// Optional filters from query string: ?file=...&tab=...
// $file = $_GET['file'] ?? null;
// $tab  = $_GET['tab']  ?? null;
$file = $_GET['file'] ?? "./budget_expense/2025_Budget_Expense.xlsx";
$tab  = $_GET['tab']  ?? "5100-510 Performance based";

// --- Load data from DB ---
$sql = "
    SELECT
        id,
        FileName,
        Tab,
        GI_name,
        Statistics,
        January,
        February,
        March,
        April,
        May,
        June,
        July,
        August,
        September,
        October,
        November,
        December,
        Total
    FROM budget_expense
    WHERE 1
";
$params = [];

// if ($file !== null && $file !== '') {
//     $sql .= " AND FileName = :file";
//     $params[':file'] = $file;
// }
// if ($tab !== null && $tab !== '') {
//     $sql .= " AND Tab = :tab";
//     $params[':tab'] = $tab;
// }

// Order however makes sense for your data
$sql .= " ORDER BY GI_name, Statistics, id";

$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Group by GI_name so we can show section headers like Excel
$groups = [];
foreach ($rows as $row) {
    $groups[$row['GI_name']][] = $row;
}
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Budget / Expense – Excel Style</title>
<style>
    body {
        font-family: Arial, sans-serif;
        font-size: 12px;
        margin: 10px;
        background: #f5f5f5;
    }

    h1 {
        font-size: 16px;
        margin-bottom: 10px;
    }

    .excel-wrapper {
        border: 1px solid #b3b3b3;
        background: #fff;
        padding: 5px;
        overflow: auto;
        max-width: 100%;
        max-height: calc(100vh - 80px);
    }

    table.excel-table {
        border-collapse: collapse;
        min-width: 1200px;
        table-layout: fixed;
    }

    .excel-table th,
    .excel-table td {
        border: 1px solid #d4d4d4;
        padding: 3px 5px;
        text-align: right;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        user-select: none; /* we use our own selection logic */
    }

    .excel-table th {
        background: #f0f0f0;
        font-weight: bold;
        text-align: center;
    }

    .col-gi {
        text-align: left;
        font-weight: bold;
        background: #e6e6e6;
    }

    .col-stat {
        text-align: left;
        background: #fafafa;
    }

    .group-header {
        background: #d9e1f2;
        font-weight: bold;
        text-align: left;
    }

    .group-header td {
        text-align: left;
    }

    .selected {
        background: #c6e0b4 !important;
        outline: 1px solid #548235;
    }

    .info-bar {
        margin-bottom: 8px;
        font-size: 11px;
        color: #444;
    }

    .info-bar code {
        background: #eee;
        padding: 1px 3px;
        border-radius: 3px;
    }
</style>
</head>
<body>

<h1>Budget / Expense – Excel Format</h1>

<div class="info-bar">
    Click and drag to select cells, then press <code>Ctrl+C</code> (Windows) or <code>⌘+C</code> (Mac) and paste into Excel.
</div>
<?php  
// var_dump($groups);
   ?>
<div class="excel-wrapper">
    <table id="budgetTable" class="excel-table">
        <thead>
        <tr>
            <th class="col-gi">GI Name</th>
            <th class="col-stat">Statistics</th>
            <th>January</th>
            <th>February</th>
            <th>March</th>
            <th>April</th>
            <th>May</th>
            <th>June</th>
            <th>July</th>
            <th>August</th>
            <th>September</th>
            <th>October</th>
            <th>November</th>
            <th>December</th>
            <th>Total</th>
        </tr>
        </thead>
        <tbody>
        <?php foreach ($groups as $giName => $items): ?>
            <!-- group header row like the big “5100-510 Performance based” row -->
            <tr class="group-header">
                <td colspan="15"><?= htmlspecialchars($giName) ?></td>
            </tr>

            <?php foreach ($items as $row): ?>
                <tr>
                    <td class="col-gi"><?= htmlspecialchars($row['GI_name']) ?></td>
                    <td class="col-stat"><?= htmlspecialchars($row['Statistics']) ?></td>
                    <td><?= $row['January']   !== null ? htmlspecialchars($row['January'])   : '' ?></td>
                    <td><?= $row['February']  !== null ? htmlspecialchars($row['February'])  : '' ?></td>
                    <td><?= $row['March']     !== null ? htmlspecialchars($row['March'])     : '' ?></td>
                    <td><?= $row['April']     !== null ? htmlspecialchars($row['April'])     : '' ?></td>
                    <td><?= $row['May']       !== null ? htmlspecialchars($row['May'])       : '' ?></td>
                    <td><?= $row['June']      !== null ? htmlspecialchars($row['June'])      : '' ?></td>
                    <td><?= $row['July']      !== null ? htmlspecialchars($row['July'])      : '' ?></td>
                    <td><?= $row['August']    !== null ? htmlspecialchars($row['August'])    : '' ?></td>
                    <td><?= $row['September'] !== null ? htmlspecialchars($row['September']) : '' ?></td>
                    <td><?= $row['October']   !== null ? htmlspecialchars($row['October'])   : '' ?></td>
                    <td><?= $row['November']  !== null ? htmlspecialchars($row['November'])  : '' ?></td>
                    <td><?= $row['December']  !== null ? htmlspecialchars($row['December'])  : '' ?></td>
                    <td><?= $row['Total']     !== null ? htmlspecialchars($row['Total'])     : '' ?></td>
                </tr>
            <?php endforeach; ?>

        <?php endforeach; ?>
        </tbody>
    </table>
</div>

<script>
// Simple Excel-style selection & copy
(function () {
    const table = document.getElementById('budgetTable');
    let isMouseDown = false;
    let startCell = null;

    function clearSelection() {
        table.querySelectorAll('.selected').forEach(td => td.classList.remove('selected'));
    }

    function selectRect(cell1, cell2) {
        clearSelection();
        if (!cell1 || !cell2) return;

        const r1 = cell1.parentElement.rowIndex;
        const c1 = cell1.cellIndex;
        const r2 = cell2.parentElement.rowIndex;
        const c2 = cell2.cellIndex;

        const rStart = Math.min(r1, r2);
        const rEnd   = Math.max(r1, r2);
        const cStart = Math.min(c1, c2);
        const cEnd   = Math.max(c1, c2);

        for (let r = rStart; r <= rEnd; r++) {
            const row = table.rows[r];
            if (!row) continue;
            for (let c = cStart; c <= cEnd; c++) {
                const cell = row.cells[c];
                if (!cell) continue;
                cell.classList.add('selected');
            }
        }
    }

    table.addEventListener('mousedown', function (e) {
        const cell = e.target.closest('td, th');
        if (!cell) return;
        isMouseDown = true;
        startCell = cell;
        selectRect(startCell, startCell);
        e.preventDefault(); // avoid native selection
    });

    table.addEventListener('mousemove', function (e) {
        if (!isMouseDown || !startCell) return;
        const cell = e.target.closest('td, th');
        if (!cell) return;
        selectRect(startCell, cell);
    });

    document.addEventListener('mouseup', function () {
        isMouseDown = false;
        startCell = null;
    });

    // Ctrl+C / Cmd+C -> copy selected cells as TSV
    document.addEventListener('keydown', function (e) {
        if (!((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c')) return;

        const selected = Array.from(table.querySelectorAll('.selected'));
        if (!selected.length) return;

        e.preventDefault();

        // collect row/col indices
        const rowIdx = [...new Set(selected.map(c => c.parentElement.rowIndex))].sort((a, b) => a - b);
        const colIdx = [...new Set(selected.map(c => c.cellIndex))].sort((a, b) => a - b);

        let lines = [];

        rowIdx.forEach(r => {
            const row = table.rows[r];
            const cells = colIdx.map(c => {
                const cell = row.cells[c];
                if (!cell) return '';
                // Excel handles simple tabs/newlines, strip inner newlines
                return cell.innerText.replace(/\r?\n/g, ' ').trim();
            });
            lines.push(cells.join('\t'));
        });

        const tsv = lines.join('\n');

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(tsv).catch(() => {
                // Fallback: textarea
                fallbackCopy(tsv);
            });
        } else {
            fallbackCopy(tsv);
        }
    });

    function fallbackCopy(text) {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
    }
})();
</script>

</body>
</html>
