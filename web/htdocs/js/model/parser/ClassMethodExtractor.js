/**
 * Adapter to the python based ClassMethodExtractor (which can extract all attributes of a class)
 */
class ClassMethodExtractor {

    #runner = null  // PySwitchRunner instance

    constructor(runner) {
        this.#runner = runner;
    }

    /**
     * options: {
     *      file: The file to parse,
     *      className
     *      importPath
     *      includeUnderscore: bool
     * }
     */
    async get(options) {
        // Tell the python code which files to examine, process it and return the decoded result.
        const resultJson = await this.#runner.pyodide.runPython(`
            import json
            from parser.misc.ClassMethodExtractor import ClassMethodExtractor

            classMethodExtractor = ClassMethodExtractor(
                file               = '` + options.file + `',
                className          = '` + options.className + `',
                importPath         = '` + options.importPath + `',
                include_underscore = ` + (options.includeUnderscore ? "True" : "False") + `
            )
            
            json.dumps(classMethodExtractor.get())
        `);
        
        return JSON.parse(resultJson);
    }
}