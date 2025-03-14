/**
 * Implements the parameter editor
 */
class ActionProperties {
    
    #actionDefinition = null;
    #inputs = null;
    #oldProperties = null;
    #advancedRows = null;
    #parserFrontend = null;
    #messages = null;
    #pages = null;
    #controller = null;
    #pageButtons = [];

    constructor(controller, parserFrontend, actionDefinition, oldProperties = null, messages = []) {
        this.#controller = controller;
        this.#parserFrontend = parserFrontend;
        this.#actionDefinition = actionDefinition;
        this.#oldProperties = oldProperties;
        this.#messages = messages;
    }

    /**
     * Initialize after adding to DOM
     */
    async init() {
        if (this.#pages) await this.#pages.init();
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        this.#advancedRows = [];
        this.#inputs = new Map();

        let holdInput = null;
        let assignInput = null;
        let assignRow = null;
        let pagerProxyRow = null;
        let pagerProxyInput = null;

        /**
         * Take over old values from the old props object, if different from the default
         */
        async function takeOverValues(input, param) {
            if (!that.#oldProperties) return;
                
            const oldParam = that.#oldProperties.getParameterDefinition(param.name);
            const oldValue = that.#oldProperties.getParameterValue(param.name);
            
            if (oldValue !== null && oldValue != oldParam.meta.getDefaultValue()) {
                await that.#setInputValue(input, param, oldValue);
            }
        }

        /**
         * Returns the passed element with the passed comment on hover
         */
        function withComment(el, param, comment) {
            if (param && param.meta.data.hideComment) return el;

            if (comment) {
                tippy(el[0], {
                    content: comment,
                    theme: "actionparameter",
                    placement: "left",
                    duration: 0
                });
            }

            return el;
        }

        const that = this;
        const parameters = await Promise.all(
            this.#actionDefinition.parameters
            .sort(function(a, b) {
                return (a.meta.data.advanced ? 1 : 0) + (b.meta.data.advanced ? -1 : 0);
            })
            .map(
                async (param) => {
                    const input = await this.#createInput(param);

                    that.#inputs.set(param.name, input);

                    // Take over old values from the old props object, if different from the default
                    await takeOverValues(input, param);

                    // Get messages for the parameter
                    const messages = that.#messages.filter((item) => item.parameter == param.name)
                    
                    // Build DOM for row
                    const row = withComment(
                        $('<tr class="selectable" />').append(
                            // Parameter Name                        
                            $('<td />').append(
                                $('<span />').text(param.name)
                            ),                     

                                
                            // Input
                            $('<td />')
                            .addClass(messages.length ? "has-messages" : null)
                            .append(
                                input,
                                ...(await that.#createAdditionalColorInputOptions(input, param))
                            )
                        ),
                        param,
                        await this.#getParameterComment(param)
                    );

                    if (!messages.length) {
                        // No messages: Hide if advanced
                        if (param.meta.data.advanced) {
                            that.#advancedRows.push({
                                row: row,
                                parameterName: param.name
                            });
                            row.hide();
                        }

                        return row;

                    } else {
                        // Messages: Also return additional rows. The result array (parameters) will be flattened later.
                        return [
                            // Main input row
                            row,

                            // Message rows
                            ...messages.map((item) => {
                                return $('<tr class="param-messages" />').append(
                                    $('<td />'),
    
                                    $('<td />').append(
                                        item.message
                                    )
                                )
                            })                            
                        ]
                    }
                }
            )
        );
        
        let tbody = null;

        const pagerActions = await this.#parserFrontend.parser.pagerActions();
        
        const ret = $('<div class="action-properties" />').append(
            // Comment
            $('<div class="action-header" />')
            .text(this.#actionDefinition.meta.getDisplayName()),
            
            $('<div class="action-comment" />')
            .html(this.#getActionComment()),

            // Parameters
            $('<div class="action-header" />')
            .text("Parameters:"),

            $('<div class="action-parameters" />').append(
                $('<table />').append(
                    tbody = $('<tbody />').append(

                        // Hold option
                        (this.#actionDefinition.meta.data.target != "AdafruitSwitch") ? null :
                        withComment(
                            $('<tr />').append(                            
                                $('<td />').append(
                                    $('<span />').text("hold")
                                ),
    
                                // Input
                                $('<td />').append(
                                    holdInput = $('<input type="checkbox" />')
                                    .prop('checked', false)
                                )
                            ),
                            null,
                            "Trigger on long press"
                        ),

                        // Assign option
                        assignRow = withComment(
                            $('<tr />').append(                            
                                $('<td />').append(
                                    $('<span />').text("assign")
                                ),
    
                                // Input
                                $('<td />').append(
                                    assignInput = $('<input type="text" />')
                                    .val(await this.#getDefaultAssign())
                                )
                            ),
                            null,
                            "Define as separate assignment"
                        ),

                        pagerProxyRow = withComment(
                            $('<tr />').append(                            
                                $('<td />').append(
                                    $('<span />').text("pager")
                                ),
        
                                // Input
                                $('<td />').append(
                                    pagerProxyInput = (await this.#createPageProxyInput())
                                ),
                            )
                            .hide(),
                            null,
                            "Pager to connect the action to"
                        ),

                        // Action parameters
                        parameters.flat()
                    )
                )
            ),

            // Pager buttons
            ...(
                !pagerActions.length ? [] : [
                    $('<div class="action-header" />')
                    .text("Assign to Page:"),
                    
                    await this.#getPagerButtons(pagerActions)
                ]
            )
        );

        if (this.#actionDefinition.name != "PagerAction") {
            assignRow.hide();

            this.#advancedRows.push({
                row: assignRow,
                parameterName: "assign"
            });
        }

        if (this.#actionDefinition.name == "PagerAction.proxy") {
            pagerProxyRow.show();
            this.#inputs.set("pager", pagerProxyInput);
        }

        // Advanced parameters: Show all button
        if (this.#advancedRows.length > 0) {
            let advRow = null;
            tbody.append(
                advRow = $('<tr />').append(
                    $('<td colspan="2" />').append(
                        $('<span class="show-advanced" />')
                        .text("more...")
                        .on('click', async function() {
                            try {
                                for (const row of that.#advancedRows) {
                                    row.row.show();
                                }

                                advRow.hide();
                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })
                    )
                )
            )
        }

        // Hold input
        if (this.#actionDefinition.meta.data.target == "AdafruitSwitch") {
            this.#inputs.set("hold", holdInput);
            if (this.#oldProperties) {
                this.setHold(this.#oldProperties.hold());            
            }
        }

        // Assign input
        this.#inputs.set("assign", assignInput);        
        // if (this.#oldProperties) {
        //     this.setAssign(this.#oldProperties.assign());            
        // }

        return ret;
    }

    /**
     * Creates the pager proxy input for PagerAction.proxy
     */
    async #createPageProxyInput() {
        const pagerActions = await this.#parserFrontend.parser.pagerActions();
        const that = this;

        return $('<select />').append(
            pagerActions.map((option) => {
                return $('<option value="' + option.assign + '" />')
                .text(option.assign)
            })                        
        )
        .on('change', async function() {
            await that.#update();
        })
    }

    /**
     * Returns the default assign value
     */
    async #getDefaultAssign() {
        if (this.#actionDefinition.name == "PagerAction") {
            return this.#getNextPagerAssign();
        }
        return "";
    }

    /**
     * Returns an unused pager assign target name
     */
    async #getNextPagerAssign() {
        const pagerActions = await this.#parserFrontend.parser.pagerActions();

        function pagerExists(assign) {
            for (const pager of pagerActions) {
                if (pager.assign == assign) return true;
            }
            return false;
        }

        let ret = "_pager";
        let cnt = 2;
        while (pagerExists(ret)) {
            ret = "_pager" + cnt++;
        }
        return ret;
    }

    /**
     * Strip the page text from quotes
     */
    #stripPageText(page) {
        return page.text ? page.text.replaceAll('"', "").replaceAll("'", "") : null;
    }

    /**
     * Returns DOM for the pager buttons
     */
    async #getPagerButtons(pagerActions) {
        this.#pageButtons = [];
        const that = this;

        function getPageText(actionCallProxy, el) {
            const pageText = that.#stripPageText(el) || el.id;

            if (pagerActions.length == 1) {
                return "" + pageText;
            }
            
            return (actionCallProxy.assign ? (actionCallProxy.assign + "|") : "") + pageText;
        }

        const noPageButton = $('<span class="button"/>')
            .text("No Page")
            .on('click', async function() {
                try {
                    await that.#setPageParameters(null, null);

                } catch (e) {
                    that.#controller.handle(e);
                }
            });
        
        this.#pageButtons.push({
            pager: "None",
            page: "None",
            button: noPageButton
        })

        return $('<div class="action-pages" />').append(
            // $('<div class="action-pages-comment" />')
            // .text('To assign this action to a page, use these buttons:'),

            noPageButton,

            (
                await Promise.all(
                    pagerActions
                    .map(
                        async (item) => {
                            const pagesArg = JSON.parse(item.arguments()).filter((e) => e.name == "pages");
                            if (!pagesArg || !pagesArg.length) return null;

                            const pages = pagesArg[0].value;
                            return (
                                await Promise.all(
                                    pages.map(async (el) => 
                                        {
                                            let pageColorIcon = null;
                                            const button = $('<span class="button"/>').append(
                                                // Page color icon
                                                pageColorIcon = $('<span class="page-icon" />'),

                                                // Page ID
                                                $('<span />')
                                                .text(getPageText(item, el))
                                            )
                                            .on('click', async function() {
                                                try {
                                                    await that.#setPageParameters(item, el);

                                                } catch (e) {
                                                    that.#controller.handle(e);
                                                }
                                            });

                                            const color = await that.#parserFrontend.icons.getPageColor(item.assign, el.id);
                                            if (color) {
                                                pageColorIcon.css('background-color', "rgb" + color);
                                            } else {
                                                pageColorIcon.hide()
                                            }

                                            that.#pageButtons.push({
                                                pager: item.assign,
                                                page: el.id,
                                                button: button
                                            })                    

                                            return button;
                                        }
                                    )
                                )
                            )
                        }
                    )
                )
            ).flat()
        );
    }

    /**
     * Update the state of the pager buttons
     */
    async #updatePagerButtons() {
        const pager = this.#getPager();
        const page = this.#getPage();
        
        for (const button of this.#pageButtons) {
            const selected = (button.pager == pager && button.page == page);
            button.button.toggleClass("page-selected", selected);
        }
    }

    /**
     * Returns the current pager (derived from the enable callback)
     */
    #getPager() {
        if (!this.#inputs.has("enable_callback")) return null;
        return this.#extractPager(this.#inputs.get("enable_callback").val());
    }

    /**
     * Extracts the pager name from _pager.xxx
     */
    #extractPager(name) {
        const splt = name.split(".");
        if (!splt.length == 2) return null;

        return splt[0];
    }

    /**
     * Returns the currently set page (parameter "id")
     */
    #getPage() {
        if (!this.#inputs.has("id")) return null;
        return this.#inputs.get("id").val();
    }

    /**
     * Sets the parameters for the given page of the given PagerAction.
     */
    async #setPageParameters(actionCallProxy, page) {
        await this.setArgument("enable_callback", ((actionCallProxy && actionCallProxy.assign) ? (actionCallProxy.assign + ".enable_callback") : "None"));
        await this.setArgument("id", (page && page.id) ? page.id : "None");

        // this.#showParameter("enable_callback");
        // this.#showParameter("id");
    }

    /**
     * Updates the page inputs to the currently available pages
     */
    async #updatePagesInputs() {
        const that = this;

        /**
         * Add pages as options to a select input
         */
        function addPagesToInput(input, pages) {
            input.empty().append(                
                pages.map((item) => {
                    const pageText = that.#stripPageText(item);
                    return $('<option value="' + item.id + '" />')
                    .text(pageText ? (item.id + " " + pageText) : item.id)
                })
            );
        }

        // Pager
        if (this.#pages && this.#actionDefinition.name == "PagerAction") {
            const pages = this.#pages.get();
            pages.push({
                id: "None"                
            })

            const input = this.#inputs.get("select_page");
            if (input) {
                const value = input.val() || "None";
                addPagesToInput(input, pages);
                input.val(value);
            }
        }

        // Pager proxy
        if (this.#actionDefinition.name == "PagerAction.proxy") {
            const pagerProxy = this.#inputs.get("pager").val();
            
            if (pagerProxy) {
                const pager = await this.#parserFrontend.parser.getPagerAction(pagerProxy)
                if (pager) {
                    const pages = pager.argument("pages");
                    if (pages) {
                        const input = this.#inputs.get("page_id");
                        if (input) {
                            const value = input.val();
                            addPagesToInput(
                                input, 
                                pages.map((item) => item.toJs())
                            );
                            input.val(value);
                        }
                    }
                }
            }
        }
    }

    /**
     * Returns an action definition which can be added to the Configuration.
     */
    createActionDefinition() {
        const that = this;

        function getName() {
            if (that.#actionDefinition.name == "PagerAction.proxy") {
                const pagerProxy = that.#inputs.get("pager").val();
                
                if (pagerProxy) {
                    return that.#actionDefinition.name.replace("PagerAction", pagerProxy)
                }
            }
            return that.#actionDefinition.name;
        }

        return {
            name: getName(),
            assign: this.#inputs.get('assign').val(),
            arguments: this.#actionDefinition.parameters
                .filter((param) => {
                    const input = that.#inputs.get(param.name);
                    if (!input) throw new Error("No input for param " + param.name + " found");
        
                    const value = that.#getInputValue(input, param);

                    return !param.hasOwnProperty("default") || (value != param.default);
                })
                .map((param) => {
                    const input = that.#inputs.get(param.name);
                    if (!input) throw new Error("No input for param " + param.name + " found");
        
                    return {
                        name: param.name,
                        value: that.#getInputValue(input, param)
                    };
                })
        }
    }

    /**
     * Returns if the user selected hold or not (JS bool, no python value)
     */
    hold() {
        if (this.#actionDefinition.meta.data.target == "AdafruitSwitch") {
            return !!this.#inputs.get("hold").prop('checked');
        }
        return false;
    }

    /**
     * Sets the hold input
     */
    setHold(hold) {
        if (this.#actionDefinition.meta.data.target != "AdafruitSwitch") {
            return;
        }
        this.#inputs.get("hold").prop('checked', !!hold)
    }

    /**
     * Returns the assign value if set
     */
    assign() {
        return this.#inputs.get("assign").val();
    }

    /**
     * Sets the assign input
     */
    setAssign(assign) {
        this.#inputs.get("assign").val(assign);
    }

    /**
     * Returns the pager proxy value if set
     */
    pagerProxy() {
        return this.#inputs.get("pager").val();
    }

    /**
     * Sets the pager proxy input
     */
    setPagerProxy(proxy) {
        this.#inputs.get("pager").val(proxy);
    }

    /**
     * Sets the input values to the passed arguments list's values
     */
    async setArguments(args) {
        await this.#update();

        for (const arg of args) {
            await this.setArgument(arg.name, arg.value);
            
            // If not default value, show the row
            const param = this.getParameterDefinition(arg.name);
            const defaultValue = param.meta.getDefaultValue()
            if (defaultValue != arg.value) {
                this.#showParameter(arg.name)
            }
        }

        await this.#update();
    }

    /**
     * Set the value of a parameter input
     */
    async setArgument(name, value) {
        await this.#update();

        // Get parameter definition first
        const param = this.getParameterDefinition(name);
        if (!param) throw new Error("Parameter " + name + " not found");

        const input = this.#inputs.get(param.name);
        if (!input) throw new Error("No input for param " + param.name + " found");

        await this.#setInputValue(input, param, value);

        await this.#update();
    }

    /**
     * Shows an advanced parameter
     */
    #showParameter(name) {
        for (const row of this.#advancedRows) {
            if (row.parameterName == name) {
                row.row.show();
            }
        }
    }

    /**
     * Searches a parameter mode by name
     */
    getParameterDefinition(name) {
        for (const param of this.#actionDefinition.parameters) {
            if (param.name == name) return param;
        }
        return null;
    }

    /**
     * Determine the comment for the action
     */
    #getActionComment() {
        if (!this.#actionDefinition.comment) return "No information available";
        let comment = "" + this.#actionDefinition.comment;

        if (comment.slice(-1) != ".") comment += ".";

        return comment;
    }

    /**
     * Determine parameter comment
     */
    #getParameterComment(param) {
        if (param.meta.data.comment) return param.meta.data.comment;
        if (!param.comment) return "";
        return param.comment;
    }

    /**
     * Update the UI
     */
    async #update() {
        await this.#updatePagerButtons();
        await this.#updatePagesInputs();
    }

    /**
     * Generates the DOM for one parameter
     */
    async #createInput(param) {
        const type = this.#deriveType(param);

        const that = this;
        async function onChange() {            
            await that.#update();
        }

        switch(type) {
            case "bool": {                             
                return $('<input type="checkbox" />')
                .prop('checked', param.meta.getDefaultValue() == "True")
                .on('change', onChange)
            }

            case "int": {
                return (await this.#getNumberInput(param))
                .on('change', onChange)
                .val(param.meta.getDefaultValue());
            }

            case 'select': {
                const values = await param.meta.getValues();
                if (values) {
                    return $('<select />').append(
                        values.map((option) => 
                            $('<option value="' + option.value + '" />')
                            .text(option.name)
                        )
                    )
                    .on('change', onChange)
                    .val(param.meta.getDefaultValue())
                }
                break;
            }

            case 'select-page': {
                return $('<select />')
                .on('change', onChange)
            }
                
            case 'pages': {
                // Dedicated type for the pager actions's "pages" parameter
                this.#pages = new PagesList(this.#controller, onChange);
                return this.#pages.create()
            }
        }        

        return $('<input type="text" />')
        .on('change', onChange)
        .val(param.meta.getDefaultValue())
    }

    /**
     * If the parameter is of type "color", this returns additional elements to add to the input. If
     * not an empty array is returned.
     */
    async #createAdditionalColorInputOptions(input, param) {
        const that = this;
        const type = this.#deriveType(param);
        if (type != "color") return [];
        
        let colorInput = null;

        async function updateColorInput() {
            const color = await that.#parserFrontend.parser.resolveColor(input.val());
            if (color) {
                colorInput.val(Tools.rgbToHex(color))
            }
        }

        const ret = [
            $('<select class="parameter-option" />').append(
                (await this.#parserFrontend.parser.getAvailableColors())
                .concat([{
                    name: "Select color..."
                }])
                .map((item) => 
                    $('<option value="' + item.name + '" />')
                    .text(item.name)
                )
            )
            .on('change', async function() {
                const color = $(this).val();
                if (color == "Select color...") return;

                await that.setArgument(param.name, color);

                $(this).val("Select color...")

                await updateColorInput();
            })
            .val("Select color..."),

            colorInput = $('<input type="color" class="parameter-option parameter-link" />')
            .on('change', async function() {
                const rgb = Tools.hexToRgb($(this).val());

                await that.setArgument(param.name, "(" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")");
            })
        ];

        input.on('change', updateColorInput)

        return ret;
    }

    /**
     * Returns a parameter value by name
     */
    getParameterValue(name) {
        const param = this.getParameterDefinition(name);
        if (!param) return null;

        const input = this.#inputs.get(param.name);
        if (!input) return null;

        return this.#getInputValue(input, param);        
    }

    /**
     * Converts the input values to action argument values
     */
    #getInputValue(input, param) {
        const type = this.#deriveType(param);

        switch(type) {
            case "bool": return input.prop('checked') ? "True" : "False";
            case "pages": return this.#pages.get();
        }        

        let value = input.val();
        if (value == "") value = param.meta.getDefaultValue();

        function getTextTypeValue(v) {
            // TODO Allow other values, move to ParameterMeta
            return Tools.autoQuote(v);
        }

        switch (type) {
            case "text": return getTextTypeValue(value)
        }
        return value;
    }

    /**
     * Sets the input value according to an argumen/parameter value
     */
    async #setInputValue(input, param, value) {
        const type = this.#deriveType(param);

        switch(type) {
            case "bool": 
                input.prop('checked', value == "True");
                input.trigger('change');
                break;

            case "pages":
                await this.#pages.set(value)
                break;

            default:
                input.val(value.replaceAll('"', "'"));
                input.trigger('change');
        }      
    }

    /**
     * Create a numeric input (int)
     */
    async #getNumberInput(param) {
        const values = await param.meta.getValues();
        if (!values) {
            return $('<input type="number" />');
        }

        return $('<select />').append(
            values.map((option) => 
                $('<option value="' + option.value + '" />')
                .text(option.name)
            )
        ) 
    }

    /**
     * Tries to derive the parameter type from its default value. Returns null if not successful.
     */
    #deriveType(param) {
        if (param.meta.data.type) return param.meta.data.type;;

        const defaultValue = param.meta.getDefaultValue();
        switch (defaultValue) {
            case "False": return "bool";
            case "True": return "bool";            
        }

        if (parseInt(defaultValue)) return "int";

        return null;
    }
}