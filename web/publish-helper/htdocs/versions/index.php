<?php 

// ini_set('display_errors', true);
// error_reporting(E_ALL);

include "src/PySwitchVersions.php";

// This handler loads and renders all versions
$versions = new PySwitchVersions();

?><!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PySwitch Emulator Versions</title>
    
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <style type="text/css">
    * {
	    font-family: Verdana, Geneva, Tahoma, sans-serif;
	    font-size: 15px;
	    box-sizing: border-box;	
	    text-align: center;
    }
    </style>
</head>
<body>
    <br>
    <h1>Available PySwitch Emulator versions:</h1>
    <br>
    <br>
    
    <?php $versions->render_version_links(); ?>
    
</body>
</html>
