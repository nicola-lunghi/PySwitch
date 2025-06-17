class ActionPropertiesInternal {

    #props = null;
    #assignInput = null;
    #assignRow = null;
    #holdInput = null;

    constructor(props) {
        this.#props = props;
    }

    async get() {
        return [
            // Hold option
            (this.#props.actionDefinition.meta.data.target != "AdafruitSwitch") ? null :
            {
                element: $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text("Hold")
                    ),

                    // Input
                    $('<td />').append(
                        this.#holdInput = $('<input type="checkbox" />')
                        .prop('checked', false)
                    )
                ),
                comment: "Trigger on long press"
            },

            // Assign option
            {
                element: this.#assignRow = $('<tr />').append(                            
                    $('<td />').append(
                        $('<span />').text("Assign")
                    ),

                    // Input
                    $('<td />').append(
                        this.#assignInput = $('<input type="text" />')
                    )
                ),
                comment: "Define as separate assignment"
            }
        ]
    }

    async setup() {
        // Hold input
        if (this.#holdInput) {
            this.#props.inputs.set("hold", this.#holdInput);
            
            if (this.#props.oldProperties) {
                await this.#props.setHold(this.#props.oldProperties.hold());            
            }
        }

        // Assign input
        this.#props.inputs.set("assign", this.#assignInput);

        this.#props.registerAdvancedParameterRow(this.#assignRow, {
            name: "assign",
            meta: {
                data: {
                    advanced: 2
                }
            }
        });
    }
}