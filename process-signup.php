<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

require 'database.php';


if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    die("405 Method Not Allowed");
}


if (!isset($mysqli) || $mysqli->connect_error) {
    die("Database connection error: " . $mysqli->connect_error);
}


if (!isset($_POST["name"], $_POST["email"], $_POST["password"])) {
    die("Missing required fields");
}


$name = trim($_POST["name"]);
$email = trim($_POST["email"]);
$password = password_hash($_POST["password"], PASSWORD_DEFAULT);


$stmt = $mysqli->prepare("INSERT INTO user (name, email, password_hash) VALUES (?, ?, ?)");

if (!$stmt) {
    die("Prepare failed: " . $mysqli->error);  
}

$stmt->bind_param("sss", $name, $email, $password);

if ($stmt->execute()) {
    header("Location: index.html");
    exit;
} else {
    die("Error executing query: " . $stmt->error);
}
?>
