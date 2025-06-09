class LocalFolderSelection {

    /**
     * Lets the user select a directory and remembers it using indexedDB
     */
    async select() {
        if (!("showDirectoryPicker" in window)) {
            throw new Error("File System Access is not supported by your browser.");
        }

        // Let the user choose the folder to open (this must be done here because the File API does not 
        // support calling this from a load function, it requires user interaction)
        try {
            const dirHandle = await window.showDirectoryPicker({
                mode: "readwrite"
            });
            if (!dirHandle) return;

            // Store dir handle in indexedDB and call the localfolder configuration which will load the handle again
            (new LocalFolderSelection()).setHandle(dirHandle);

            return true;

        } catch (e) {
            if (e.name != "AbortError") {
                throw e;
            }

            return false;
        }
    }

    /**
     * Calls the local folder config (either by restarting or calling via routing)
     */
    async call(controller) {
        if (controller.currentConfig instanceof LocalFolderConfiguration) {
            // Already at local folder config
            await controller.loadConfiguration(
                new LocalFolderConfiguration(controller)
            )
        } else {
            // Navigate to local folder config
            controller.routing.call("localfolder");
        }
    }

    /**
     * Sets the current dir handle
     */
    async setHandle(handle) {
        await window.idbKeyval.set("localDirHandle", handle);
    }

    /**
     * Returns the current dir handle or undefined
     */
    async getHandle() {
        return window.idbKeyval.get("localDirHandle");
    }
}