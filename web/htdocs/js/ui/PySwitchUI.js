class PySwitchUI {

    #controller = null;
    #options = null;
    #block = null;
    #progressBar = null;            // Progress bar inner element (the one to resize)
    #progressMessage = null;        // Messages for progress
    #progressBarContainer = null;
    #contentHeadline = null;
    #listElement = null;
    #deviceElement = null;

    notifications = null;
    examples = null;
    portBrowser = null;
    clientButton = null;

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
        this.#listElement.hide();
    }

    /**
     * Build the DOM tree
     */
    build() {
        const that = this;

        const containerElement = $(this.#options.containerElementSelector);
        if (!containerElement) {
            throw new Error("Container " + this.#options.containerElementSelector + " not found");
        }

        let messageElement = null;
        let clientButtonElement = null;
        
        // Settings panel
        containerElement.append(
            $('<div class="settings">').append(

                // Controllers link
                $('<div class="btn btn-primary"/>')
                .on("click", async function() {
                    try {
                        await that.portBrowser.browse(
                            "Select MIDI port to load configuration from:", 
                            async function(portName) {
                                that.#controller.routing.call(that.#controller.getControllerUrl(portName));
                            }
                        );

                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
                .text("Load from Controller"),

                // Examples link
                $('<div class="btn btn-primary"/>')
                .on("click", async function() {
                    location.href = "#example/";
                })
                .text("Load Example"),

                // Version display
                $('<div/>')
                .text("PySwitch Emulator v" + this.#controller.VERSION)
            ),

            /////////////////////////////////////////////////////////////////////////
            
            $('<div class="application"/>').append(
                // Header, showing the current config.
                this.#contentHeadline = $('<div class="headline"/>'),

                // Client connection button
                clientButtonElement = $('<div />'),

                // This will be filled by python. Can not have any class names in here, or they will be overwritten by python code.
                this.#deviceElement = $('<div id="pyswitch-device"></div>')
            ),

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

            // List browser 
            this.#listElement = $('<div class="list-browser"/>')
            .hide(),

            // Messages
            messageElement = $('<div class="messages"/>')
        );

        // Create handlers
        this.notifications = new Notifications(messageElement)
        this.examples = new ExampleBrowser(this.#controller, this.#listElement);        
        this.portBrowser = new PortBrowser(this.#controller, this.#listElement);  
        this.clientButton = new ClientConnectionButton(this.#controller, clientButtonElement);      
    }

    /**
     * Sets the UI properties for the configuration
     */
    async applyConfig(config) {
        // Headline (config name)
        this.#contentHeadline.text(await config.headline());

        // CSS classes for the main device element
        this.#deviceElement[0].className = await (await config.parser()).getClass();
    }

    /**
     * Shows the example browser showing the path.
     */
    async browseExample(path) {
        await this.examples.browse(path);
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