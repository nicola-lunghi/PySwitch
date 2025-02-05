class VirtualKemperClient extends VirtualClient {
    
    #runIntervalHandler = null;
    #protocol = null;
    #ui = null;

    config = null;
    parameters = null;
    rigId = 0;
     
    /**
     * {
     *      productType: 2   (Player)
     * }
     */
    constructor(config) {
        super("Virtual Kemper Profiler Player");
        this.config = config || {};

        // Parameter storage
        this.parameters = new VirtualKemperParameters(this);

        // Bidirectional protocol
        this.#protocol = new VirtualKemperProtocol(this);

        // Initialize the parameters with values and types
        (new VirtualKemperClientSetup(this.parameters)).setup();
        
        this.#updateRig();
    }

    /**
     * Start processing regular updates to send messages. If not set, the caller has to 
     * call update() regularly.
     */
    run(updateInterval) {
        const that = this;
        this.#runIntervalHandler = setInterval(
            function() {
                try {
                    that.update();

                } catch (e) {
                    console.error(e);
                }
            }, 
            updateInterval
        );
    }

    /**
     * When running, this is called regularly to update the protocol and other timed stuff
     */
    update() {
        this.#protocol.update();
    }

    /**
     * Updates everything to the current rig ID.
     */
    #updateRig() {
        const bank = Math.floor(this.rigId / 5);
        const rig = this.rigId % 5;
        const rigName = "Rig " + (bank + 1) + "-" + (rig + 1);

        this.parameters.get([0, 1]).config.value = rigName;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Called by PySwitch when a message should be sent to the client. 
     * Naming is misleading here: this effectively receives data!
     */
    async send(message) {
        try {
            message = message.toJs();
            
            // Try to parse message: Protocol
            if (this.#protocol.parse(message)) return;

            // Try to parse message: Parameters
            if (this.parameters.parse(message)) return;

            // Unparsed!
            console.warn(this.name + ": Unparsed message: ", message);

        } catch (e) {
            // We must catch here to get usable stack traces, as this is called by python code.
            console.error(e);
        }
    }

    /**
     * Add a raw message to the queue
     */
    queueMessage(msg) {        
        this.messageQueue.push(msg);
    }

    /**
     * Stop listening to the input
     */
    detach() {  
        clearInterval(this.#runIntervalHandler);

        if (this.#ui) this.#ui.destroy();
    }

    /**
     * If supported, can create a user interface in the passed container DOM element
     */
    createUserInterface(container) {
        if (this.#ui) this.#ui.destroy();
        this.#ui = new VirtualKemperClientUI(container, this);
    }

    /**
     * Logging with prefix
     */
    log() {
        [].unshift.call(arguments, this.name + ":");
        console.log.apply(null, arguments);
    }
}