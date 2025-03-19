class ParserInput extends ParserTreeElement {

    assignment = null;

    constructor(parser, data, assignment) {
        super(parser, data);

        this.assignment = assignment;
    }

    /**
     * If invalid, replace the data by searching for the input again
     */
    checkValid() {
        try {
            super.checkValid();

        } catch (e) {
            // Try to find the current version of the input data
            this.data = this.parser.inputData(this.assignment.name);
            
            if (!this.data) {
                throw new Error("The input is invalid and cannot be reactivated again: " + this.assignment.name);
            }

            this.setValid();
            super.checkValid();
        }
    }

    displayName() {
        return this.assignment.displayName;
    }

    holdTimeMillis() {
        this.checkValid()
        const arg = this.getArgument("holdTimeMillis");
        return (arg && arg.value) ? parseInt(Tools.stripQuotes(arg.value)) : null;
    }

    setHoldTimeMillis(htm) {
        this.checkValid()
        if (this.setArgument("holdTimeMillis", "" + parseInt(htm))) {
            this.parser.updateConfig();
        }
    }

    holdRepeat() {
        this.checkValid()
        const arg = this.getArgument("holdRepeat");
        return (arg && arg.value) ? (arg.value == "True") : null;
    }

    setHoldRepeat(hr) {
        this.checkValid()
        if (this.setArgument("holdRepeat", hr ? "True" : "False")) {
            this.parser.updateConfig();
        }
    }

    actions(hold = false) {
        this.checkValid()

        const actions = this.getArgument(hold ? "actionsHold" : "actions");
        if (!actions) return []

        return actions.value
        .filter((item) => item != "None")
        .map((item) => new ParserInputAction(this.parser, this, item));
    }

    setActions(actions, hold = false, noUpdate = false) {
        this.checkValid()

        const prepped = actions.map((item) => { 
            return {
                name: item.name,
                assign: item.assign,
                arguments: item.arguments.map((arg) => {
                    if (item.name == "PagerAction" && arg.name == "pages") {
                        return {
                            name: arg.name,
                            value: arg.value.map((page) => {
                                return {
                                    arguments: [
                                        {
                                            name: "id",
                                            value: page.id
                                        },
                                        {
                                            name: "color",
                                            value: page.color
                                        },
                                        {
                                            name: "text",
                                            value: page.text
                                        }
                                    ]
                                }
                            })
                        }    
                    }

                    return {
                        name: arg.name,
                        code: (typeof arg.value == "string") ? arg.value : null,
                        value: (typeof arg.value == "string") ? null : arg.value,
                        assign: arg.assign ? arg.assign : null
                    }
                })
            }
        })
        
        this.setArgument(hold ? "actionsHold" : "actions", prepped);

        if (!noUpdate) {
            this.parser.updateConfig();
        }
    }
}