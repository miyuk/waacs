<?php

define('TOKEN_DB', './data/token.sqlite3');
$pdo = new PDO("sqlite:$TOKEN_DB");
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$pdo->exec('CREATE TABLE IF NOT EXISTS token(id INTEGER PRIMARY KEY AUTOINCREMENT, token VARCHAR(32) NOT NULL, issuance_time DATETIME)');
$stmt = $pdo->prepare('SELECT token, issuance_time FROM token ORDER BY id DESC LIMIT 1');
$stmt->execute();
$latest_token = $stmt->fetchOne();
echo json_encode($latest_token);
