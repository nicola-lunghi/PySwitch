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
        const that = this;

        function getFontSize(item) {
            return parseInt(item.replace(/[^0-9]/g, ''));
        }

        await this.#createInput(list, {
            name: "font",
            text: "Font",
            type: 'select',
            options: (await this.#handler.editor.getConfig().parser.getAvailableFonts())
                .map((font) => {
                    return {
                        value: '"' + font + '"',
                        text: font.replace('/fonts/', '') + " (" + getFontSize(font) + "px)"
                    }
                })  
        });

        await this.#createInput(list, {
            name: "backColor",
            comment: "Background color. Must be set for labels which will get a background later because of RAM saving constraints.",
            text: "Back Color",
            type: 'color'
        });

        await this.#createInput(list, {
            name: "textColor",
            text: "Text Color",
            type: 'color'
        });

        await this.#createInput(list, {
            name: "maxTextWidth",
            comment: "Max. text size before wrapping. NOTE: If scale is set, you have to adjust this by the same factor.",
            text: "Max. Text Width",
            type: 'text'
        });
        
        await this.#createInput(list, {
            name: "lineSpacing",
            text: "Line Spacing",
            type: 'text'
        });

        await this.#createInput(list, {
            name: "text",
            comment: "Optional initial text. If set, the label shows the passed text until some action or callback overwrites it. NOTE: For string literals, you have to add quotes!",
            text: "Initial Text",
            type: 'text',
            additionalContent: [
                $('<span class="parameter-option parameter-link" />')
                .text('Show PySwitch version on boot')
                .on('click', function() {
                    try {
                        const v = 'f"PySwitch { PYSWITCH_VERSION }"';
                        list.setParameter('text', v);
                        that.setParameter('text', v);
                        
                    } catch (e) {
                        that.#handler.editor.controller.handle(e);
                    }
                })
            ]
        });

        await this.#createInput(list, {
            name: "stroke",
            comment: "Optional stroke size. This does not really generate a real stroke (because of RAM issues) but instead just reduces the size by the entered amount.",
            text: "Stroke",
            type: 'text'
        });
    }

    /**
     * Returns a layout parameter value from the data model
     */
    getParameter(name) {
        const node = Tools.getArgument(this.#layout.value, name);
        return node ? node.value : null;
    }

    /**
     * Sets a parameter on the data model
     */
    setParameter(name, value) {
        if (value == "") {
            // Remove parameter
            this.#layout.value.arguments = this.#layout.value.arguments.filter((entry) => (entry.name != name));

        } else {
            // Set/add parameter
            let valueNode = Tools.getArgument(this.#layout.value, name);
            if (!valueNode) {
                this.#layout.value.arguments.push(valueNode = {
                    name: name
                })
            }
            valueNode.value = value;
        }

        this.#handler.update();
    }

    /**
     * {
     *      type,
     *      name,
     *      text,
     *      options:  (select only),
     *      additionalContent
     * }
     */
    async #createInput(list, options) {
        const that = this;

        await list.createInput({
            type: options.type,
            name: options.name,
            comment: options.comment,
            displayName: options.text,
            value: this.getParameter(options.name),
            options: options.options,
            onChange: async function(value) {
                // Remove assignment, if any
                delete that.#layout.value.assign;

                that.setParameter(options.name, value);
            },
            additionalContent: options.additionalContent
        });
    }
}