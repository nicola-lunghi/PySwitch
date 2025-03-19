class ParserInputAction extends ParserTreeElement {

    name = null;
    proxyName = null;
    client = null;
    assign = null;
    input = null;

    #id = null;

    #arguments = null;

    constructor(parser, input, data) {
        super(parser, data);

        this.input = input;
        this.#id = Tools.uuid();
        this.name = data.name;
        this.client = data.client;
        this.assign = data.assign;
        
        // this.proxyName = data.assign ? (this.name + "." + data.assign) : null;
    }

    id() {
        return this.#id;
    }

    pager() {
        this.checkValid()
        const ec = this.argument("enable_callback");
        if (!ec || ec) return null;
        
        const id = this.argument("id");
        
        if (!id || id == "None")  return null;
        
        const splt = ec.split(".");
        if (splt.length != 2) return null;
        
        return splt[0];
    }

    page() {        
        if (!this.pager()) return null;
        return self.argument("id");
    }

    arguments() {
        this.checkValid()
        if (this.#arguments) return this.#arguments;

        const that = this;

        this.#arguments = this.data.arguments.map((arg) => {
            if (this.name == "PagerAction" && arg.name == "pages") {
                return {
                    name: arg.name ? arg.name : null,
                    value: that.#mapPages(arg)
                }
            }

            return {
                name: arg.name ? arg.name : null,
                value: this.parser.codeForNode(arg.value)
            }
        });

        return this.#arguments;
    }

    argument(name) {
        this.checkValid()
        const args = this.arguments();

        for (const arg of args) {
            if (arg.name == name) return arg.value;
        }

        return null;
    }

    #mapPages(arg) {
        return arg.value.map((page) => {
            function getPageArg(name) {
                for (const a of page.arguments) {
                    if (a.name == name) {
                        return a.value
                    }
                }
            }

            return {
                id: getPageArg("id"),
                color: getPageArg("color"),
                text: getPageArg("text")
            }
        })
    }
}