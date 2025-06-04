<?php 

// ini_set('display_errors', true);
// error_reporting(E_ALL);

include 'src/PySwitchVersions.php';

/**
 * Shows all PySwitch versions
 * 
 * @author thomasweber
 */
class PySwitchVersionsPage {
    
    /**
     * Renders the list of available versions.
     */
    public function render():void {
        $versions = (new PySwitchVersions())->get('../');
        
        $addtext = ' (latest)';
        foreach ($versions as $version) {
            $vtext = $version->name;
            
            ?>
                <a href="/<?php echo $vtext; ?>/PySwitch/web/htdocs"
                   target="_blank">
                	PySwitch Emulator for Version <?php echo $vtext . $addtext; ?>
                </a>    
                <br>
                <br>
            <?php
            
            $addtext = '';
        }
    }    
}

$appl = new PySwitchVersionsPage();

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
    
    <?php 
        $appl->render(); 
    ?>
</body>
</html>
