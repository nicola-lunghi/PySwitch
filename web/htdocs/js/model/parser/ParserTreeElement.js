class ParserTreeElement {

    data = null;
    parser = null;
    
    #parentInputs = null;

    constructor(parser, data) {
        this.parser = parser;
        this.data = data;
        this.setValid();
    }

    setValid() {
        this.#parentInputs = this.parser.inputs();
    }

    checkValid() {
        if (this.parser.inputs() === this.#parentInputs) return;
        throw new Error("This handler is not valid anymore", this.data);
    }

    getArgument(name) {
        this.checkValid()
        for (const arg of this.data.arguments) {
            if (arg.name == name) return arg;
        }
        return null;
    }

    setArgument(name, value) {
        this.checkValid()
        for (const arg of this.data.arguments) {
            if (arg.name == name) {
                arg.value = value;
                return true;
            }
        }
        this.data.arguments.push(
            {
                name: name,
                value: value
            }
        )
    }
}