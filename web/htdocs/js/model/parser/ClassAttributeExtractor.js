/**
 * Adapter to the python based ClassAttributeExtractor (which can extract all attributes of a class)
 */
class ClassAttributeExtractor {

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
            from parser.misc.ClassAttributeExtractor import ClassAttributeExtractor

            classAttributeExtractor = ClassAttributeExtractor(
                file               = '` + options.file + `',
                className          = '` + options.className + `',
                importPath         = '` + options.importPath + `',
                include_underscore = ` + (options.includeUnderscore ? "True" : "False") + `
            )
            
            json.dumps(classAttributeExtractor.get())
        `);
        
        return JSON.parse(resultJson);
    }
}