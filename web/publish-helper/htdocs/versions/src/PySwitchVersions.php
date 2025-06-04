<?php

/**
 * Determines all PySwitch versions in a location on the file system.
 * 
 * @author thomasweber
 */
class PySwitchVersions {
    
    /**
     * Determine versions. These are all folders in the passed directory which do not start with "versions".
     * 
     * @return array of objects with name and mtime properties.
     */
    public function get(string $path):array {
        $dir = new DirectoryIterator($path);
        
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