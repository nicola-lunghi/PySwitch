class FunctionMeta {

    #meta = null;         // Function metadata
    #function = null;     // Function descriptor

    constructor(meta, func) {
        this.#meta = meta;
        this.#function = func;
    }   

    toJSON() {
        return this.#meta || {}
    }
}