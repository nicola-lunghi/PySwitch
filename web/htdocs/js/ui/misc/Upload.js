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

        const popup = this.#controller.ui.getPopup({ 
            container: this.#controller.ui.container,
        });

        popup.show(
            $('<div />').append(
                $('<div />')
                .text("Please select the files to load."),
                $('<br />'),

                $('<div />')
                .text("Only display.py and/or inputs.py files will be processed."),
                $('<br />'),

                $('<hr />'),
                $('<br />'),

                $('<input type="file" id="input" multiple />')
                .on('change', async function(e) {
                    popup.hide();
                    await that.#load(e, config);
                })
            )
        );
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
                        data.inputs_py = await that.#loadFile(file);
                    }
                    if (file.name == "display.py") {
                        data.display_py = await that.#loadFile(file);
                    }
                }
        
                await config.parser.updateFromData(data);
            }
        });
    }

    /**
     * Reads one file from the form input
     */
    async #loadFile(file) {
		return new Promise((resolve, reject) => {
    		var reader = new FileReader();

    	    reader.onload = function(evt) {
    	        try {
    	    		resolve(evt.target.result);

    	        } catch (e) {
    	        	reject(e);
    	        }    	        
    	    }

    	    reader.onerror = function(evt) {
    	    	reject('Error reading ' + file.name);
    	    }

    	    reader.readAsText(file); 
		});
	}
}