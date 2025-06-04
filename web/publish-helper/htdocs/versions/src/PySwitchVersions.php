<?php

/**
 * Shows all PySwitch versions
 * 
 * @author thomasweber
 */
class PySwitchVersions {
    
    /**
     * Renders the list of available versions.
     */
    public function render_version_links():void {
        $versions = $this->get_versions();
        
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
    
    /**
     * Determine versions. These are all folders in the parent directory which do not start with "versions".
     * 
     * @return array of objects with name and mtime properties, sorted in descending order by last modified timestamp.
     */
    public function get_versions():array {
        $dir = new DirectoryIterator('../');
        
        $versions = array();
        foreach ($dir as $node) {
            if (!$node->isDir() || $node->isDot() || str_starts_with($node->getFilename(), "versions")) continue;
            
            array_push($versions, (object)array(
                "name" => $node->getFilename(),
                "mtime" => $node->getMTime()
            ));
        }
        
        usort($versions, function ($a, $b) {
            return $b->mtime - $a->mtime;
        });
            
        return $versions;
    }
}

?>