/**
 * Parameter range
 */
class ParameterRange {

    #parser = null;
    #rangeDefinition = null;

    constructor(parser, rangeDefinition) {
        this.#parser = parser;
        this.#rangeDefinition = rangeDefinition || {};
    }

    async min() {        
        return this.#resolve(this.#rangeDefinition.min);        
    }

    async max() {
        return this.#resolve(this.#rangeDefinition.max);        
    }

    /**
     * Returns all possible values
     */
    async getValues() {
        const values = [];
        
        if (this.#rangeDefinition.none) {
            values.push({
                name: "None",
                value: "None"
            })
        }

        const min = await this.min();
        const max = await this.max();
        
        for(let i = min; i <= max; ++i) {
            values.push({
                name: "" + i,
                value: i
            })
        }

        return values;
    }

    /**
     * Resolve tokens
     */
    async #resolve(value) {        
        return this.#parser.resolveValueToken(value);
    }
}