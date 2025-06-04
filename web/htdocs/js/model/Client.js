class Client {

    static #clients = null;    // Buffer

    /**
     * Returns all available client handlers
     */
    static async getAvailable(basePath = "") {
        if (Client.#clients) return Client.#clients;

        const toc = JSON.parse(await Tools.fetch(basePath + "circuitpy/lib/pyswitch/clients/toc.php"));

        Client.#clients = toc.children
            .filter((item) => item.type == "dir")
            .map((item) => ClientFactory.getInstance(item.name))
            .filter((item) => item != null);

        return Client.#clients;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    id = null;            // Client ID

    constructor(id) {
        this.id = id;
    }

    /**
     * Factory for ParameterMeta instances
     */
    async createParameterMeta(parser, meta, paramDef) {
        return new ParameterMeta(parser, this, meta, paramDef);
    }

    /**
     * Factory for FunctionMeta instances
     */
    async createFunctionMeta(parser, meta, funcDef) {
        return new FunctionMeta(parser, this, meta, funcDef);
    }

    /**
     * Must return a ClientDetector instance for the configuration
     */
    async getClientDetector() {
        return null;
    }

    /**
     * Can return a virtual client, or null if the parsers config does not support a virtual client.
     */
    async getVirtualClient(options) {
        return null;
    }    

    /**
     * Can resolve tokens related to value ranges etc.
     */
    async resolveValueToken(value) {
        return value;
    }

    /**
     * If the client has mapping implementations in __init__.py, this can return the class name for them.
     */
    getInitMappingsClassName() {
        return null;
    }

    /**
     * If the client has action implementations in __init__.py, this can return the class name for them.
     */
    getInitActionsClassName() {
        return null;
    }

    /**
     * Returns a display name for the client
     */
    getDisplayName() {
        return this.id;
    }

    /**
     * Given a DisplayEditor instance, this has to render the client's implementations of DisplayElement.
     * Must return a DOM node or null.
     */
    async renderDisplayElement(node, editor) {
        return null;
    }
}