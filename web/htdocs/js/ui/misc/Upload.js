/**
 * Upload tools
 */
class Upload {

    #controller = null;

    constructor(controller) {
        this.#controller = controller;
    }

    /**
     * Updates the passed Configuration from uploaded files
     */
    async upload(config) {
        const that = this;

        const el = $('<input type="file" id="input" multiple />')
        .addClass('upload-file-input')
        .on('change', async function(e) {
            el.remove();
            await that.#load(e, config);
        });

        this.#controller.ui.container.append(el);
        el.trigger('click');
    }

    /**
     * Clean up file inputs which have been canceled
     */
    cleanup() {
        $('.upload-file-input').remove();
    }

    /**
     * Load files from the passed event
     */
    async #load(e, config) {
        const that = this;
        await this.#controller.restart({
            message: "none",
            changeCallback: async function() {
                const data = await config.get();

                for (const file of e.target.files) {
                    if (file.name == "inputs.py") {
                        data.inputs_py = await Tools.loadFile(file);
                    }
                    if (file.name == "display.py") {
                        data.display_py = await Tools.loadFile(file);
                    }
                }
        
                await config.parser.updateFromData(data);
            }
        });
    }
}