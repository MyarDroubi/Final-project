<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$host = "localhost";       
$username = "root";        
$password = "root";        
$dbname = "login_db";      
$port = 8889;              


$mysqli = new mysqli($host, $username, $password, $dbname, $port);


if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
} else {
    echo "Connected successfully!";
}
?>
