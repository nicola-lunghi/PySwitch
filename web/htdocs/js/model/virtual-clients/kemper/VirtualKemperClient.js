class VirtualKemperClient extends VirtualClient {
    
    messageQueue = [];   // Queue of raw MIDI bytes. Will be filled here message by message, and fetched from the python midi wrappers

    #runIntervalHandler = null;
    config = null;
    parameters = null;
    rigId = 0;
     
    #protocol = null;
    
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

        // Some values
        this.#setupParameters();

        this.#updateRig();
    }

    /**
     * Set up some data on parameters not contained in any parameter set
     */
    #setupParameters() {
        // Amp comment
        this.parameters.set({ key: [0, 16], value: "Amp Comment" });

        // FX Slot DLY
        this.parameters.set({ key: [60, 0], value: 160 });  // DLY
        this.parameters.set({ key: [60, 3], value: 1 });     // On

        // FX Slot REV
        this.parameters.set({ key: [61, 0], value: 180 });  // REV
        this.parameters.set({ key: [61, 3], value: 1 });  // On

        // Default values
        this.parameters.setDefault({ value: 0 });         // Default for numeric parameters
        this.parameters.setDefault({ value: "none" });    // Default for string parameters

        
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
     * Send a MIDI message. Expects a byte array of raw data.
     * In this case, as we are a client, this effectively receives data!
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
        // console.log(msg);
        this.messageQueue.push(msg);
    }

    /**
     * Stop listening to the input
     */
    detach() {  
        clearInterval(this.#runIntervalHandler);
    }

    /**
     * Logging with prefix
     */
    log() {
        [].unshift.call(arguments, this.name + ":");
        console.log.apply(null, arguments);
    }
}