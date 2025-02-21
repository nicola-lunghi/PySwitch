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
    build() {
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
                                that.getPopup({ 
                                    container: that.container,
                                    fullscreen: true
                                })
                                .show(
                                    $('<div class="about-content" />').append(
                                        await Tools.fetch('about.html')
                                    )
                                );

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
                        // Show/hide tabs
                        showTabsButton = $('<div class="button fas fa-ellipsis-v"/>')
                        .on('click', async function() {
                            try {
                                that.tabs.toggle();
                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        }),

                        // Load
                        $('<div class="button button-primary"/>')
                        .text("Load")
                        .on("click", async function() {
                            try {
                                await that.loadBrowser.browse();

                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })  
                    ),

                    // Header, showing the current config name
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

                // // List browsers and popups (shared)
                // this.listElement = $('<div class="list-browser"/>')
                // .hide(),

                // Messages
                messageElement = $('<div class="messages"/>')
            )
        );

        // Browsers
        this.#initLoadBrowser();
        this.#initClientBrowser();

        // Client state button
        this.clientButton = new ClientConnectionButton(this.#controller, clientButtonElement);      

        // Message alerts etc.
        this.notifications = new Notifications(messageElement);

        // Parser UI handler
        this.frontend = new PySwitchFrontend(this.#controller, this.#deviceElement, this.#options);

        // Show or hide tabs
        this.tabs = new Tabs(this.#controller, tabsElement, showTabsButton);
    }

    /**
     * Returns a new simple Popup instance
     */
    getPopup(config = {}) {
        if (!config.container) config.container = this.container;
        return new Popup(config);        
    }

    /**
     * Returns a new BrowserPopup instance
     */
    getBrowserPopup(config = {}) {
        if (!config.container) config.container = this.container;
        return new BrowserPopup(config);        
    }

    /**
     * Init browser for loading configurations
     */
    #initLoadBrowser() {
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
                    rootText: "Load from a connected Controller",
                    onSelect: async function(entry) {
                        that.#controller.routing.call(that.#controller.getControllerUrl(entry.value));
                    }
                })
            ],
            postProcess: async function(entry, generatedElement) {
                // Highlight currently selected config
                const currentName = that.#controller.currentConfig ? (await that.#controller.currentConfig.name()) : null;
                
                if (that.#controller.currentConfig && (entry.value == currentName)) {
                    generatedElement.addClass('highlighted');
                }    
            }
        }); 
    }

    /**
     * Init browser for client connection select
     */
    #initClientBrowser() {
        const that = this;

        // A browser to select client connections (to Kemper etc.), triggered by the client select button
        this.clientBrowser = this.getBrowserPopup({
            headline: "Please select a client device to control",
            providers: [
                new PortsProvider(this.#controller, {
                    onSelect: async function(entry) {
                        that.#controller.setState("client", entry.value);
                        await that.#controller.client.init(that.#controller.currentConfig);
                    },
                    additionalEntries: [                        
                        {
                            value: "auto",
                            text: function(/*entry*/) {
                                const client = that.#controller.getState("client");
                                const currentDeviceText = (client == "auto") ? (" (" + (that.#controller.client.current ? that.#controller.client.current : "None found") + ")") : "";

                                return "Auto-detect client device" + currentDeviceText;
                            },
                            sortString: "___01"
                        },
                        {
                            value: "Not connected",
                            text: "Not connected",
                            sortString: "___02"
                        },
                        {
                            value: "virtual",
                            text: async function(/*entry*/) {
                                const vc = (await VirtualClient.getInstance(that.#controller.currentConfig));
                                if (!vc) {
                                    return "Virtual client (not supported for " + (await that.#controller.currentConfig.name()) + ")";
                                }
                                return vc.name;
                            },
                            sortString: "ZZZZZZZ"
                        }
                    ]
                })
            ],
            postProcess: function(entry, generatedElement) {
                // Highlight currently selected client
                const client = that.#controller.getState("client");

                if (client == entry.value) {
                    generatedElement.addClass('highlighted');
                }
            }
        });
    }

    /**
     * Sets the UI properties for the configuration
     */
    async applyConfig(config) {
        // Headline (config name)
        this.#contentHeadline.text(await config.name());

        // Apply the parser to the frontend (generates all switches etc.)
        const parser = await config.parser(this.#controller.pyswitch);        
        await this.frontend.apply(parser);

        // Add tabs for the editors: First remove old editors
        if (this.editors.inputs) this.editors.inputs.destroy();
        if (this.editors.display) this.editors.display.destroy();

        const code = await config.get();
        this.editors.inputs = new CodeEditor("inputs.py", code.inputs_py);
        this.editors.display = new CodeEditor("display.py", code.display_py);

        this.tabs.add(this.editors.inputs, 0);
        this.tabs.add(this.editors.display, 1);

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
                    "Virtual Kemper"
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