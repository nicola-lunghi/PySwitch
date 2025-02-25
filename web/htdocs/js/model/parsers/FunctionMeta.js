/**
 * Metadata for functions
 */
class FunctionMeta {

    data = null;          // Function metadata
    #function = null;     // Function descriptor

    constructor(meta, func) {
        this.data = meta || {};
        this.#function = func;
    }   

    getCategory() {
        return this.data.category ? this.data.category : "none";
    }
}