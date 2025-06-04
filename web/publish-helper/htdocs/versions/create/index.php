<?php 

ini_set('display_errors', true);
error_reporting(E_ALL);

/**
 * Create versions
 * 
 * @author thomasweber
 */
class PySwitchCreateVersion {
    
    /**
     * Run the application
     */
    public function process():void {
        $name = $_GET["name"];

        // Ask for name
        if (!$name) {
            $this->render_form();
            return;
        }

        // Create version
        $this->create_version($name);
    }

    /**
     * Creates a new version
     */
    private function create_version(string $path):void {
        // Check if already exists
        if (file_exists($path)) {
            throw Exception("Path already exists");
        }

        // Create folder
        throw Exception("Path already exists");

        // Clone repo

        // Copy examples and content

        // Adjust .htaccess
    }

    /**
     * Renders the form to create the version
     */
    private function render_form():void {
        ?>
            <form method="get" action="">
                <input type="text" name="name" placeholder="Enter Version Number..." />
                <input type="submit" value="Create Version" />
            </form>
        <?php
    }
}

$appl = new PySwitchCreateVersion();

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

?><!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Create PySwitch Emulator Versions</title>
    
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
    <h1>Create new Version</h1>
    <br>
    <br>
    
    <?php 
        $appl->process();
    ?>
        
</body>
</html>
