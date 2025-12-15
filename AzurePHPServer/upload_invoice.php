
<?php
// test_sqlite.php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Path to your SQLite database file.
// You can change the filename or path if you already have a .db file.
$dbFile = __DIR__ . '/test.sqlite.db';
// Example if you already have one somewhere else:
// $dbFile = '/home/site/wwwroot/mydata.db';

echo "<h2>SQLite Test</h2>";
echo "<p>DB file: <code>{$dbFile}</code></p>";

// Check if SQLite extensions are available
echo "<p>PDO SQLite available: " . (extension_loaded('pdo_sqlite') ? 'YES' : 'NO') . "</p>";
echo "<p>SQLite3 extension available: " . (extension_loaded('sqlite3') ? 'YES' : 'NO') . "</p>";

try {
    // Connect using PDO
    $pdo = new PDO('sqlite:' . $dbFile);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    echo "<p>✅ Connected to SQLite database.</p>";

    // Create a test table if it doesn't exist
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ");
    echo "<p>✅ Table <code>users</code> is ready.</p>";

    // Insert a test row
    $name = 'User_' . rand(1000, 9999);
    $stmt = $pdo->prepare("INSERT INTO users (name, created_at) VALUES (:name, datetime('now'))");
    $stmt->execute([':name' => $name]);
    echo "<p>✅ Inserted test row with name: <strong>{$name}</strong></p>";

    // Query the last 5 rows
    $stmt = $pdo->query("SELECT * FROM users ORDER BY id DESC LIMIT 5");
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo "<h3>Last 5 rows in <code>users</code>:</h3>";
    if (empty($rows)) {
        echo "<p>No rows found.</p>";
    } else {
        echo "<table border='1' cellpadding='5' cellspacing='0'>
                <tr><th>ID</th><th>Name</th><th>Created At</th></tr>";
        foreach ($rows as $row) {
            echo "<tr>";
            echo "<td>" . htmlspecialchars($row['id']) . "</td>";
            echo "<td>" . htmlspecialchars($row['name']) . "</td>";
            echo "<td>" . htmlspecialchars($row['created_at']) . "</td>";
            echo "</tr>";
        }
        echo "</table>";
    }

} catch (Exception $e) {
    echo "<p style='color:red;'>❌ Error: " . htmlspecialchars($e->getMessage()) . "</p>";
}

?>