<?php

define('QR_IMG_PATH', './waacs_qr.png');
$update_time = filemtime(QR_IMG_PATH);

echo $update_time;
