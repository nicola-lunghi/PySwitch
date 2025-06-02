class LocalFolderConfiguration extends Configuration {
    
    #name = 'Local Folder';

    #observer = null;

    constructor(controller) {
        super(controller, null);
    }

    /**
     * Stop watching the files
     */
    async destroy() {
        await this.#unobserve();
    }

    /**
     * Loads config files from a local folder (opens it if there is no file handle in memory)
     */
    async load() {
        // Get file handles from indexedDB
        let handles = null;
        try {
            handles = await this.#getHandles(true);
        
        } catch (e) {
            throw new Error("Local folder could not be found anymore.");
        }

        const inputsFile = await handles.inputs.getFile();
        const displayFile = await handles.display.getFile();

        // Load data
        let inputs_py = await Tools.loadFile(inputsFile);
        let display_py = await Tools.loadFile(displayFile);

        // Load default template when files do not exist
        if (!inputs_py) {
            inputs_py = await Tools.fetch(encodeURI("templates/MIDICaptain 10/inputs.py"));
        }
        if (!display_py) {
            display_py = await Tools.fetch(encodeURI("templates/MIDICaptain 10/display.py"));
        }

        // Set config name
        this.#name = handles.dir.name;

        // Start watching the files
        await this.#observe(handles);

        return {
            inputs_py: inputs_py,
            display_py: display_py
        }
    }

    /**
     * Can the config be saved?
     */
    canBeSaved() {
        return true;
    }

    /**
     * Returns the text for the head line
     */
    async name() {
        return this.#name;
    }
    
    /**
     * Save the data to the location of the configuration
     */
    async doSave() {
        // Get file handles from indexedDB
        const handles = await this.#getHandles(true);

        // Get data
        const data = await this.get();

        // Stop observing, if running
        await this.#unobserve();

        // Write to the files in parallel
        await Promise.all(
            [
                this.#writeFile(handles.inputs, data.inputs_py), 
                this.#writeFile(handles.display, data.display_py)
            ]
        );

        // Start observing again
        await this.#observe(handles);
    }

    /**
     * Returns the file handles, or throws an exception
     */
    async #getHandles(create = false) {
        // Retrieve dir handle from indexedDB (must have been set before by the "Open" dialog, as
        // the File API does require this to be triggered by an user action)
        const dirHandle = await (new LocalFolderSelection()).getHandle();

        if (!dirHandle) {
            throw new Error("Please open a local folder first.");
        }

        // Get handles to the files needed
        return {
            dir: dirHandle,
            inputs: await dirHandle.getFileHandle("inputs.py", { create: create }),
            display: await dirHandle.getFileHandle("display.py", { create: create })
        }
    }

    /**
     * Writes to a file handle
     */
    async #writeFile(fileHandle, contents) {
        // Create a FileSystemWritableFileStream to write to.
        const writable = await fileHandle.createWritable();

        // Write the contents of the file to the stream.
        await writable.write(contents);

        // Close the file and write the contents to disk.
        await writable.close();
    }

    /**
     * Watches the file handles passed. When they change and the config is not dirty, this will reload the config.
     */
    async #observe(handles) {
        if (!('FileSystemObserver' in self)) {
            console.warn("File Observer API not supported! Changes from external editors will not reload the emulator automatically.");
            return;
        }

        try {
            const that = this;
            this.#observer = new FileSystemObserver(async (records, observer) => {
                await that.#unobserve();

                try {
                    await (new LocalFolderSelection()).call(that.controller);
                    
                } catch (e) {
                    that.controller.handle(e);
                }
            });

            await this.#observer.observe(handles.inputs);
            await this.#observer.observe(handles.display);

        } catch (e) {
            console.error(e);
        }
    }

    /**
     * Stop observing any files
     */
    async #unobserve() {
        if (!this.#observer) return;

        this.#observer.disconnect();
        this.#observer = null;
    }
}