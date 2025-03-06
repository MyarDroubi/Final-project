<?php
session_start(); 


if (isset($_SESSION["user_id"])) {
    header("Location: index.php");
    exit;
}

error_reporting(E_ALL);
ini_set('display_errors', 1);

require __DIR__ . "/database.php"; 

global $mysqli; 

$is_invalid = false;

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    
    if (!isset($mysqli) || $mysqli->connect_error) {
        die("Database connection error: " . $mysqli->connect_error);
    }

    $sql = sprintf(
        "SELECT * FROM user WHERE email = '%s'",
        $mysqli->real_escape_string($_POST["email"])
    );

    $result = $mysqli->query($sql);
    $user = $result->fetch_assoc();

    if ($user) {
        if (password_verify($_POST["password"], $user["password_hash"])) {
            session_regenerate_id();
            $_SESSION["user_id"] = $user["id"];

            header("Location: index.php");
            exit;
        }
    }
    $is_invalid = true;
}
?>

<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Logga in</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="mycss.css" />
</head>
<body>
    <nav class="navbar">
        <h1>Livechat</h1>
        <div class="menu">
            <a href="Index.html">Introduktion</a>
            <a href="Livechats.html">Livechats</a>
            <a href="Kontakt.html">Kontakt</a>
            <a href="Om_oss.html">Om oss</a>
        </div>
        <a href="signup.html" class="navbar-button">Registrera</a>
    </nav>
    </nav>

    <?php if ($is_invalid): ?>
        <em>Invalid login</em>
    <?php endif; ?>

    <div class="Inlog_kroppen">
        <section class="login-section">
            <h2>Logga in</h2>
            <form id="login-form" method="post">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" value="<?= htmlspecialchars($_POST["email"] ?? "") ?>" required />
                </div>

                <div class="form-group">
                    <label for="password">Lösenord:</label>
                    <input type="password" id="password" name="password" required />
                </div>

                <button type="submit" class="login-button">Logga in</button>
            </form>

            <p>Har du inget konto?</p>
            <a href="signup.html" class="signup-button">Registrera dig</a>
        </section>
    </div>

    <footer>
        <p>&copy; 2024 Livechat. Alla rättigheter förbehållna.</p>
    </footer>
</body>
</html>

