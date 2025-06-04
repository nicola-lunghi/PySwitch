<?php

// ini_set('display_errors', true);
// error_reporting(E_ALL);

include "src/PySwitchVersions.php";

class PySwitchUpdater {

    /**
     * Updates the parents folder .htaccess file
     */
    public function process(string $path):void {
        $versions = (new PySwitchVersions())->get($path);

        if (!$versions) {
            echo "No versions available, exiting.\n";
            exit;
        }

        ob_start();
        $this->render_htaccess($versions);
        $htaccess = ob_get_clean();

        file_put_contents($path.DIRECTORY_SEPARATOR.'.htaccess', $htaccess);
    }

    /**
     * Render .htaccess contents
     */
    private function render_htaccess(array $versions):void {
        $this->render_line("RewriteEngine On");
        $this->render_line("RewriteCond %{REQUEST_URI} !/versions");
        $this->render_line();
        $this->render_line("###########################################################");
        $this->render_line();
        $this->render_line("# All versions have to be ignored here if called directly:");
        $this->render_line();

        foreach ($versions as $version) {
            $this->render_line("RewriteCond %{REQUEST_URI} !".$version->name."/PySwitch/web/htdocs/");
        }

        $this->render_line();
        $this->render_line("###########################################################");
        $this->render_line();
        
        $this->render_line("# This points to the latest version");
        $this->render_line();
        $this->render_line("RewriteRule ^(.*)$ /".$versions[0]->name."/PySwitch/web/htdocs/$1");

    }

    /**
     * Renders one line of .htaccess
     */
    private function render_line(string $line = ""):void {
        echo $line."\n";
    }
}

?>