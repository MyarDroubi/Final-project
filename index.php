<?php
session_start(); 

require __DIR__ . "/database.php"; 

global $mysqli; 

$user = null;

if (isset($_SESSION["user_id"])) {
    if (!isset($mysqli) || $mysqli->connect_error) {
        die("Database connection error: " . $mysqli->connect_error);
    }

    $stmt = $mysqli->prepare("SELECT * FROM user WHERE id = ?");
    $stmt->bind_param("i", $_SESSION["user_id"]);
    $stmt->execute();
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();
}
?>

<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="mycss.css" />
</head>
<body>
    <nav class="navbar">
        <h1>Home</h1>
        <div class="menu">
            <a href="Index.html">Introduktion</a>
            <a href="Livechats.html">Livechats</a>
            <a href="Kontakt.html">Kontakt</a>
            <a href="Om_oss.html">Om oss</a>
        </div>

        <div class="auth-buttons">
            <?php if ($user): ?>
                <a href="logout.php" class="navbar-button">Logga ut</a>
            <?php else: ?>
                <a href="login.php" class="navbar-button">Logga in</a>
            <?php endif; ?>
        </div>
    </nav>

    <main>
        <?php if ($user): ?>
            <p>Hello, <?= htmlspecialchars($user["name"]) ?>! you are logged in</p>
        <?php else: ?>
            <p><a href="login.php">Log in</a> or <a href="signup.html">Sign up</a></p>
        <?php endif; ?>
    </main>

</body>
</html>

