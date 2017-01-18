<?php
date_default_timezone_set('Asia/Tokyo');
define('TOKEN_DB', './data/token.sqlite3');
$pdo = new PDO('sqlite:'.TOKEN_DB);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$stmt = $pdo->prepare('SELECT token, issuance_time, activation_time, connection_number, access_type FROM token WHERE ORDER BY id DESC LIMIT 1');
$stmt->execute();
$latest_token = $stmt->fetch();
echo json_encode($latest_token);
