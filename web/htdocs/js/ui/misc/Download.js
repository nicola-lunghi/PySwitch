/**
 * Download tools
 */
class Download {

    /**
     * Downloads the passed Configuration instance's data
     */
    async download(config) {
        const data = await config.get();

        const files = [
            {
                name: "inputs.py",
                lastModified: new Date(),
                input: data.inputs_py
            },
            {
                name: "display.py",
                lastModified: new Date(),
                input: data.display_py
            }
        ]

        // Get the ZIP stream in a Blob (this function comes from the client-zip module)
        const blob = await downloadZip(files).blob();

        // Create an URL for the data blob
        const url = URL.createObjectURL(blob);

        window.saveAs(url, (await config.name()) + ".zip");
    }
}