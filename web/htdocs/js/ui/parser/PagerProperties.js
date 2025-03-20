class PagerProperties {

    pages = null;

    #buttons = [];
    #props = null;

    constructor(props) {
        this.#props = props;
    }

    async init() {
        if (this.pages) await this.pages.init();
    }

    async pagers() {
        return await this.#props.parserFrontend.parser.pagerActions();
    }

    async getButtons() {
        const pagers = await this.pagers();
        if (!pagers.length) return [];

        return [
            $('<div class="action-header" />')
            .text("Assign to Page:"),
            
            await this.#getButtons(pagers)
        ]    
    }

    getPagesList(onChange) {
        this.pages = new PagesList(this.#props.controller, onChange);
        return this.pages.create()
    }

    /**
     * Returns the current pager (derived from the enable callback)
     */
    pager() {
        if (!this.#props.inputs.has("enable_callback")) return null;
        return this.#extractPager(this.#props.inputs.get("enable_callback").val());
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
    page() {
        if (!this.#props.inputs.has("id")) return null;
        return this.#props.inputs.get("id").val();
    }

    async update() {
        await this.#updateButtons();
        await this.#updateInputs();
    }

    /**
     * Updates the page inputs to the currently available pages
     */
    async #updateInputs() {
        const that = this;

        /**
         * Add pages as options to a select input
         */
        function addPagesToInput(input, pages) {
            input.empty().append(                
                pages.map((item) => {
                    const pageText = that.stripText(item);
                    return $('<option value="' + item.id + '" />')
                    .text(pageText ? (item.id + " " + pageText) : item.id)
                })
            );
        }

        // Pager
        if (this.pages && this.#props.actionDefinition.name == "PagerAction") {
            const pages = this.pages.get();
            pages.push({
                id: "None"                
            })

            const input = this.#props.inputs.get("select_page");
            if (input) {
                const value = input.val() || "None";
                addPagesToInput(input, pages);
                input.val(value);
            }
        }

        // Pager proxy
        if (this.#props.actionDefinition.name == "PagerAction.proxy" && this.#props.inputs.has("pager")) {
            const pagerProxy = this.#props.inputs.get("pager").val();
        
            if (pagerProxy) {
                const pager = await this.#props.parserFrontend.parser.getPagerAction(pagerProxy)
                if (pager) {
                    const pages = pager.argument("pages");
                    if (pages) {
                        const input = this.#props.inputs.get("page_id");
                        if (input) {
                            const value = input.val();
                            addPagesToInput(
                                input, 
                                pages
                            );
                            input.val(value);
                        }
                    }
                }
            }
        }
    }

    /**
     * Update the state of the pager buttons
     */
    async #updateButtons() {
        const pager = this.pager();
        const page = this.page();
        
        for (const button of this.#buttons) {
            const selected = (button.pager == pager && button.page == page);
            button.button.toggleClass("page-selected", selected);

            if (this.#props.actionDefinition.name == "PagerAction" && !selected) {
                // Prevent that pagers are assigned to their own pages (only if not already selected)
                button.button.toggle(button.pager != this.#props.assign());
            }

            if (this.#props.actionDefinition.name == "PagerAction.proxy" && !selected) {
                // Prevent that pager proxies are assigned to their own pages (only if not already selected)
                button.button.toggle(button.pager != this.#props.pagerProxy());
            }
        }
    }

    /**
     * Strip the page text from quotes
     */
    stripText(page) {
        return page.text ? page.text.replaceAll('"', "").replaceAll("'", "") : null;
    }
    
    /**
     * Creates the pager proxy input for PagerAction.proxy
     */
    async createProxyInput() {
        const pagerActions = await this.pagers();
        const that = this;

        return $('<select />').append(
            pagerActions.map((option) => {
                return $('<option value="' + option.assign + '" />')
                .text(option.assign)
            })                        
        )
        .on('change', async function() {
            await that.#props.update();
        })
    }

    /**
     * Returns an unused pager assign target name
     */
    async getNextPagerAssign() {
        const pagerActions = await this.pagers();

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
     * Sets the parameters for the given page of the given PagerAction.
     */
    async #setParameters(actionCallProxy, page) {
        await this.#props.setArgument("enable_callback", ((actionCallProxy && actionCallProxy.assign) ? (actionCallProxy.assign + ".enable_callback") : "None"));
        await this.#props.setArgument("id", (page && page.id) ? page.id : "None");
    }

    /**
     * Returns DOM for the pager buttons
     */
    async #getButtons(pagerActions) {
        this.#buttons = [];
        const that = this;

        function getPageText(actionCallProxy, el) {
            const pageText = that.stripText(el) || el.id;

            if (pagerActions.length == 1) {
                return "" + pageText;
            }
            
            return (actionCallProxy.assign ? (actionCallProxy.assign + "|") : "") + pageText;
        }

        const noPageButton = $('<span class="button"/>')
            .text("No Page")
            .on('click', async function() {
                try {
                    await that.#setParameters(null, null);

                } catch (e) {
                    that.#props.controller.handle(e);
                }
            });
        
        this.#buttons.push({
            pager: "None",
            page: "None",
            button: noPageButton
        })

        return $('<div class="action-pages" />').append(
            noPageButton,
            (
                await Promise.all(
                    pagerActions
                    .map(
                        async (item) => {
                            const pagesArg = item.arguments().filter((e) => e.name == "pages");
                            if (!pagesArg || !pagesArg.length) return null;

                            const pages = pagesArg[0].value;
                            
                            return (
                                await Promise.all(
                                    pages
                                    .map(async (el) => 
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
                                                    await that.#setParameters(item, el);

                                                } catch (e) {
                                                    that.#props.controller.handle(e);
                                                }
                                            });

                                            const color = await that.#props.parserFrontend.icons.getPageColor(item.assign, el.id);
                                            if (color) {
                                                pageColorIcon.css('background-color', "rgb" + color);
                                            } else {
                                                pageColorIcon.hide()
                                            }

                                            that.#buttons.push({
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
}