class DisplayLabelTypeLayout {

    #handler = null;
    #layout = null;    // Layout raw data node

    constructor(handler) {
        this.#handler = handler;

        this.#layout = Tools.getArgument(this.#handler.node, "layout");
    }

    /**
     * Sets up some parameters
     */
    async setupParameters(list) {
        this.#createInput(list, {
            name: "font",
            text: "Font",
            type: 'select',
            options: (await this.#handler.editor.getConfig().parser.getAvailableFonts()).map((font) => ('"' + font + '"'))            
        });

        this.#createInput(list, {
            name: "maxTextWidth",
            text: "Max. Text Width",
            type: 'text'
        });
        
        this.#createInput(list, {
            name: "lineSpacing",
            text: "Line Spacing",
            type: 'text'
        });

        // TODO colors

        this.#createInput(list, {
            name: "text",
            text: "Initial Text",
            type: 'text'
        });

        this.#createInput(list, {
            name: "stroke",
            text: "Stroke",
            type: 'text'
        });
    }

    /**
     * {
     *      type,
     *      name,
     *      text,
     *      options:  (select only)      
     * }
     */
    #createInput(list, options) {
        const that = this;

        const valueNode = Tools.getArgument(this.#layout.value, options.name);
        const value = valueNode ? valueNode.value : "";

        list.createInput({
            type: options.type,
            name: options.name,
            displayName: options.text,
            value: value,
            options: options.options,
            onChange: async function(value) {
                // Remove assignment, if any
                delete that.#layout.value.assign;

                if (value == "") {
                    // Remove parameter
                    that.#layout.value.arguments = that.#layout.value.arguments.filter((entry) => (entry.name != options.name));

                } else {
                    // Set/add parameter
                    let valueNode = Tools.getArgument(that.#layout.value, options.name);
                    if (!valueNode) {
                        that.#layout.value.arguments.push(valueNode = {
                            name: options.name
                        })
                    }
                    valueNode.value = value;
                }
            }
        });
    }
}