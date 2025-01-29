class PySwitchUI {

    #controller = null;
    #options = null;
    #block = null;
    #progressBar = null;            // Progress bar inner element (the one to resize)
    #progressMessage = null;        // Messages for progress
    #progressBarContainer = null;
    #contentHeadline = null;
    #listElement = null;

    selectController = null;        
    selectClient = null;
    notifications = null;
    examples = null;
    controllers = null;

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
        const ports = this.#controller.device.bridge.getMatchingPortPairs();

        const containerElement = $(this.#options.containerElementSelector);
        if (!containerElement) {
            throw new Error("Container " + this.#options.containerElementSelector + " not found");
        }

        /**
         * Helper: Get option element list for client connections
         */
        function getOptions(ports, prefix, noneValue) {
            const ret = [
                $('<option/>')
                .val(noneValue)
                .text(prefix + noneValue)
            ]

            for (const port of ports) {
                ret.push(
                    $('<option/>')
                    .val(port.name)
                    .text(prefix + port.name)
                )            
            }
            return ret;
        }

        let messageElement = null;
        
        // Settings panel
        containerElement.append(
            $('<div class="settings">').append(

                // Select client
                this.selectClient = 
                $('<select />')
                .on("change", async function() {
                    try {
                        await that.#controller.selectClient(that.selectClient.val());

                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
                .append(
                    getOptions(ports, "Client Device: ", "Not connected")
                ),

                // // Select controller
                // this.selectController = 
                // $('<select />')
                // .on("change", async function() {
                //     try {
                //         await that.#controller.selectController(that.selectController.val());

                //     } catch (e) {
                //         that.#controller.handle(e);
                //     }
                // })
                // .append(
                //     getOptions(ports, "Controller: ", "Not connected")
                // ),

                // Controllers link
                $('<div class="btn btn-primary"/>')
                .on("click", async function() {
                    try {
                        await that.controllers.browse("Select MIDI port to load configuration from:", async function(portName) {
                            console.log(portName);
                            that.#controller.routing.call(that.#controller.getControllerUrl(portName));
                        });

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
                .text("Examples"),

                // Version display
                $('<div/>')
                .text("PySwitchUI v" + this.#controller.VERSION)
            ),
            
            // Content area
            $('<div class="content">').append(
                // Header, showing the current config
                this.#contentHeadline = $('<div class="headline"/>'),

                // This will be filled by python
                $('<div id="pyswitch-device" class="midicaptain-nano-4"></div>')
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

        this.notifications = new Notifications(messageElement)

        this.examples = new ExampleBrowser(this.#controller, this.#listElement);        
        this.controllers = new ControllerBrowser(this.#controller, this.#listElement);
    }

    /**
     * Sets the headline text
     */
    setHeadline(text) {
        this.#contentHeadline.text(text);
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