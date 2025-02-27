/**
 * User interface controller
 */
class PySwitchUI {

    #controller = null;
    #options = null;
    
    #block = null;
    #progressBar = null;            // Progress bar inner element (the one to resize)
    #progressMessage = null;        // Messages for progress
    #progressBarContainer = null;
    #contentHeadline = null;
    #deviceElement = null;
    #versionElement = null;
    
    #virtualClientTab = null;
    #virtualClientUI = null;    
    
    container = null;

    notifications = null;
    loadBrowser = null;
    saveBrowser = null;
    clientBrowser = null;
    clientButton = null;
    frontend = null;
    tabs = null;

    editors = {
        inputs: null,
        display: null
    }

    /**
     * Options:
     * {
     *      containerElementSelector: "body",       DOM Selector for the container DOM element the ui should be built in 
     *                                             (optional, default: "body")
     * }
     */
    constructor(controller, options) {
        this.#controller = controller;
        this.#options = options;
    }

    /**
     * Reset the UI
     */
    async reset() {
        // this.listElement.hide();
    }

    /**
     * Update the version
     */
    updateVersion() {
        this.#versionElement.html("PySwitch Emulator<br>v" + this.#controller.VERSION);
    }

    /**
     * Build the DOM tree
     */
    async build() {
        const containerElement = $(this.#options.containerElementSelector);
        if (!containerElement) {
            throw new Error("Container " + this.#options.containerElementSelector + " not found");
        }

        let messageElement = null;
        let clientButtonElement = null;
        let tabsElement = null;
        let showTabsButton = null;
        
        // Settings panel
        const that = this;
        containerElement.append(
            this.container = $('<div class="container"/>').append(
                // Tabs area
                tabsElement = $('<div class="tabs" />'),

                // Application area
                //this.#applicationElement = 
                $('<div class="application"/>').append(
                    
                    $('<div class="about" />').append(
                        // Version
                        this.#versionElement = $('<div class="version"/>').html("PySwitch Emulator")
                        .on('click', async function() {
                            try {
                                await that.showAbout();

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        }),

                        // Donate
                        $('<a class="donate" href="https://www.paypal.com/webapps/mpp/page-not-found?cmd=_s-xclick&hosted_button_id=6WHW7WRXSGQXY" target="_blank" />')
                        .text('Donate')
                    ),
                    
                    // Client connection button (class is set in the ClientConnectionButton)
                    clientButtonElement = $('<div data-toggle="tooltip"/>'),

                    // This will be filled by python and show the device. Can not have any class names in 
                    // here, or they will be overwritten by python code.
                    this.#deviceElement = $('<div id="pyswitch-device"></div>'),

                    // Buttons
                    $('<div class="buttons" />').append(
                        // Load
                        $('<div class="appl-button fas fa-folder-open" data-toggle="tooltip" title="Open configuration..." />')
                        .on("click", async function() {
                            try {
                                that.loadBrowser.options.selectedValue = that.#controller.currentConfig ? (await that.#controller.currentConfig.name()) : null;
                                await that.loadBrowser.browse();

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })  ,

                        // Save
                        $('<div class="appl-button fas fa-save" data-toggle="tooltip" title="Save configuration..." />')
                        .on("click", async function() {
                            try {
                                await that.saveBrowser.browse();

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })  ,

                        // Show/hide tabs
                        showTabsButton = $('<div class="appl-button fas fa-code" data-toggle="tooltip" title="Show code"/>')
                        .on('click', async function() {
                            try {
                                that.tabs.toggle();

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        }),
                    ),

                    // Header, showing the current Configuration name
                    this.#contentHeadline = $('<div class="headline"/>'),
                ),

                /////////////////////////////////////////////////////////////////////////////////////

                // Progress bar and blocker
                this.#block = $('<div class="block"/>').append(
                    this.#progressBarContainer = $('<span class="progressBar" />').append(   // progressBarOuterContainer
                        $('<span />').append(  //progressBarContainer
                            $('<span />').append(   // progressBarBack
                                this.#progressBar = $('<span />')  // progressBar
                            )
                        ),                        
                    ),
                    this.#progressMessage = $('<span class="progressMessage" />').text("Initializing")
                ),

                /////////////////////////////////////////////////////////////////////////////////////

                // Messages
                messageElement = $('<div class="messages"/>')
            )
        );

        // Browsers
        await this.#initLoadBrowser();
        await this.#initSaveBrowser();
        await this.#initClientBrowser();

        // Client state button
        this.clientButton = new ClientConnectionButton(this.#controller, clientButtonElement);      

        // Message alerts etc.
        this.notifications = new Notifications(messageElement);

        // Parser UI handler
        this.frontend = new PySwitchFrontend(this.#controller, this.#deviceElement, this.#options);

        // Show or hide tabs
        this.tabs = new Tabs(this.#controller, tabsElement, showTabsButton);

        // if (!this.#controller.getState('suppressInfoPopup')) {
        //     await this.showAbout();
        // }
    }

    /**
     * Show the about popup
     */
    async showAbout() {
        const that = this;

        this.getPopup({ 
            container: this.container,
            fullscreen: true,
            onClose: function() {
                // that.#controller.setState('suppressInfoPopup', true);
            }
        })
        .show(
            $('<div class="about-content" />').append(
                await Tools.fetch('about.html')
            )
        );
    }

    /**
     * Returns a new simple Popup instance
     */
    getPopup(options = {}) {
        if (!options.container) options.container = this.container;
        if (!options.errorHandler) options.errorHandler = this.#controller;
        return new Popup(options);        
    }

    /**
     * Returns a new BrowserPopup instance
     */
    getBrowserPopup(options = {}) {
        if (!options.container) options.container = this.container;
        if (!options.errorHandler) options.errorHandler = this.#controller;
        return new BrowserPopup(options);        
    }

    /**
     * Init browser for loading configurations
     */
    async #initLoadBrowser() {
        const that = this;

        // A browser for loading configurations, triggered by the load button
        this.loadBrowser = this.getBrowserPopup({
            wide: true,
            headline: "Please select a configuration to load",
            providers: [
                // Templates
                new TemplatesProvider(this.#controller, "templates/toc.php"),

                // Examples
                new ExamplesProvider(this.#controller, "examples/toc.php"),
                
                // Connected controllers
                new PortsProvider(this.#controller, {
                    rootText: "Connected Controllers",
                    onSelect: async function(entry) {
                        that.#controller.routing.call(that.#controller.getControllerUrl(entry.value));
                    }
                }),

                // Presets
                new LocalPresetsProvider(this.#controller, {
                    onSelect: async function(entry) {
                        // Open existing preset
                        that.#controller.routing.call(encodeURI("preset/" + entry.value));
                    }
                })
            ]
        }); 
    }

    /**
     * Init browser for loading configurations
     */
    async #initSaveBrowser() {
        const that = this;

        // A browser for loading configurations, triggered by the load button
        this.saveBrowser = this.getBrowserPopup({
            wide: true,
            headline: "Please select a destination to store the current configuration",
            providers: [
                // Connected controllers
                new PortsProvider(this.#controller, {
                    rootText: "Connected Controllers",
                    onSelect: async function(entry) {
                        that.saveBrowser.hide();
                        await that.#controller.device.saveConfig(that.#controller.currentConfig, entry.value);
                    }
                }),

                // Presets
                new LocalPresetsProvider(this.#controller, {
                    newPresetsEntry: true,
                    onSelect: async function(entry) {
                        let data = null;
                        try {
                            data = await that.#controller.currentConfig.get();

                        } catch(e) {
                            console.log(e);
                            throw new Error("No data to save");
                        }

                        if (entry.data.newPreset) {
                            // Create new preset
                            let presetId = null;
                            
                            while (!presetId || that.#controller.presets.has(presetId)) {
                                presetId = prompt("Name for the new preset:");
                                if (!presetId) return; // Canceled by user
                            }

                            await that.#controller.presets.set(presetId, data);

                            that.#controller.ui.notifications.message("Successfully created preset " + presetId, "S");

                            that.#controller.routing.call(encodeURI("preset/" + presetId));

                        } else {
                            if (!confirm("Do you want to overwrite preset " + entry.text + "?")) return;

                            await that.#controller.presets.set(entry.value, data);

                            that.#controller.ui.notifications.message("Successfully saved preset " + entry.text, "S");

                            that.#controller.routing.call(encodeURI("preset/" + entry.value));
                        }                        
                    }
                })
            ]
        }); 
    }

    /**
     * Init browser for client connection select
     */
    async #initClientBrowser() {
        const that = this;

        const additionalEntries = [                        
            {
                value: "auto",
                text: function(/*entry*/) {
                    const client = that.#controller.client.state.get("selectedClient");
                    const currentDeviceText = (client == "auto") ? (" (" + (that.#controller.client.current ? that.#controller.client.current : "None found") + ")") : "";

                    return "Auto-detect client device" + currentDeviceText;
                },
                sortString: "___01"
            },
            {
                value: "Not connected",
                text: "Not connected",
                sortString: "___02"
            }
        ];

        const clients = await Client.getAvailable();
        for (const client of clients) {
            const vc = await client.getVirtualClient();
            if (!vc) continue;
                    
            additionalEntries.push({
                value: "virtual-" + client.id,
                text: async function(/*entry*/) {
                    return vc.name;
                },
                sortString: "ZZZZZZZ" + vc.name
            });
        }

        // A browser to select client connections (to Kemper etc.), triggered by the client select button
        this.clientBrowser = this.getBrowserPopup({
            headline: "Please select a client device to control",
            providers: [
                new PortsProvider(this.#controller, {
                    onSelect: async function(entry) {
                        that.#controller.client.state.set("selectedClient", entry.value);
                        
                        await that.#controller.client.init(that.#controller.currentConfig);
                    },
                    additionalEntries: additionalEntries
                })
            ]
        });
    }

    /**
     * Sets the UI properties for the configuration
     */
    async applyConfig(config) {
        // Headline (config name)
        this.#contentHeadline.text(await config.name());

        // Apply the parser to the frontend (generates all switches etc.)
        await this.frontend.apply(config.parser);

        // Create editor tabs if not yet done
        if (!this.editors.inputs) {
            this.editors.inputs = new CodeEditor(this.#controller, "inputs.py", "inputs_py");
            this.tabs.add(this.editors.inputs, 0);
        }
        if (!this.editors.display) {
            this.editors.display = new CodeEditor(this.#controller, "display.py", "display_py");
            this.tabs.add(this.editors.display, 1);
        }
        
        // Set new content on editors
        await this.editors.inputs.setConfig(config);
        await this.editors.display.setConfig(config);
    }

    confirmIfDirty() {
        return this.tabs.confirmIfDirty();
    }

    /**
     * Shows the passed virtual client as a tab.
     */
    showVirtualClient(client) {
        if (this.#virtualClientTab) {
            this.tabs.remove(this.#virtualClientTab);
            this.#virtualClientTab = null;
        }

        if (this.#virtualClientUI) {
            this.#virtualClientUI.destroy();
            this.#virtualClientUI = null;
        }
        
        if (client) {
            let virtualClientElement = null;

            // Add tab
            this.tabs.add(
                this.#virtualClientTab = new Tab(
                    // Virtual client if enabled
                    virtualClientElement = $('<div class="virtual-client"/>'),
                    client.name ? client.name : "Virtual Client"
                )
            );

            this.#virtualClientUI = client.getUserInterface(virtualClientElement);    
        }
    }

    /**
     * Sjow a block screen
     */
    block() {
        this.#progressBarContainer.hide();
        this.#progressMessage.hide();

        this.#block.show();
    }

    /**
     * Show progress. Values above 1 hide the progress bar.
     * 
     * @param {*} percentage range [0..1]
     * @param {*} message 
     */
    progress(percentage, message) {
        if (percentage >= 1) {
            this.#block.hide();
            return;
        }

        const perc = (percentage * 100).toFixed(2);  
		
        this.#progressBarContainer.show();
		this.#progressBar.css('width', perc + '%');		

        this.#progressMessage.show();
        this.#progressMessage.text(message);

        this.#block.show();
    }

    /**
     * Wrapper to show messages.
     */
    message(msg, type, options) {
        this.progress(1);
        this.notifications.message(msg, type, options);
    }   
}