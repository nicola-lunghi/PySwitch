/**
 * Generates a parameter list for general params
 */
class DisplayGeneralParameterList extends ParameterList {
    
    #editor = null;

    constructor(editor) {
        super(editor.controller);
        this.#editor = editor;
    }

    /**
     * Sets up the parameters
     */
    async setup() {
        const that = this;

        async function setType(type) {
            try {
                await that.#editor.setSplashesCallback(type);

            } catch(e) {
                await that.rebuild();

                throw e;
            }
        }

        function getOptions() {
            const ret = [];
            for (const cl of that.#editor.availableCallbacks) {
                for (const cb of cl.callbacks) {
                    if (cb.target != "Splashes") continue;
                    ret.push(
                        $('<option />')
                            .prop('value', cb.name)
                            .text(cb.name)
                    );
                }
            }
            return ret;
        }

        let select = null;
        await this.createTextInput({
            name: "splashes_type",
            displayName: "Display Driver",
            value: this.#editor.splashes.name,
            additionalClasses: "wide",
            onChange: async function(value) {
                await setType(value);
            },
            additionalContent: [
                select = $('<select class="parameter-option" />')
                    .append(
                        $('<option />')
                            .prop('value', "")
                            .text('Select type...'),
                    )
                    .append(
                        getOptions()
                    )
                    .on('change', async function() {
                        try {
                            await setType(select.val());                            

                        } catch(e) {
                            that.#editor.controller.handle(e);
                        }
                    })
            ]
        });
    }
}