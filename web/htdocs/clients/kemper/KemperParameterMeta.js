/**
 * Parameter metadata
 */
class KemperParameterMeta extends ParameterMeta {

    /**
     * If possible, returns a list of values, null if not possible.
     */
    async getValues() {
        if (this.parameter.name == "display") {
            return (await this.parser.getAvailableDisplays())
                .concat(["None"])
                .map((item) => {
                    return {
                        name: item,
                        value: item
                    };
                })
        }

        if (this.parameter.name == "mapping") {
            return this.#generateMappingOptions();
        }

        return super.getValues();
    }

    /**
     * Generates the mapping list for input
     */
    async #generateMappingOptions() {
        const mappings = await this.parser.getAvailableMappings();

        async function getMappingVariants(mapping) {
            if (mapping.parameters.length == 0) {
                return [
                    {
                        name: mapping.name + "()",
                        value: mapping.name + "()"
                    }
                ]
            }

            // We only resolve the first parameter here (mappings never have more)
            const param = mapping.parameters[0];

            function addValues(values) {
                for(const value of values) {
                    ret.push({
                        name: mapping.name + "(" + param.name + " = " + value.value + ")",
                        value: mapping.name + "(" + param.name + " = " + value.value + ")",
                    });
                }
            }

            const ret = [];
            if (param.meta && param.meta.range()) {
                const values = await param.meta.range().getValues();
                addValues(values);

            } else if (param.meta && param.meta.data.values) {
                addValues(param.meta.data.values);
                
            } else {
                throw new Error("No parameter values for parameter " + param.name + " of mapping " + mapping.name + " found in meta.json")
            }
            return ret;
        }

        let ret = [];
        for(const mapping of mappings) {
            ret = ret.concat(await getMappingVariants(mapping))
        }
        return ret;
    }
}