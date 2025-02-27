/**
 * Virtual Kemper.
 */
class VirtualKemperClient extends VirtualClient {
    
    #runIntervalHandler = null;
    #ui = null;

    options = null;
    protocol = null;
    parameters = null;
    tempo = null;
    tuner = null;
    morph = null;

    /**
     * {
     *      productType: 2            (Player),
     *      simulateMorphBug: true    Simulates the morph bug of the Kemper (as of 02/2025) causing morph state not 
     *                                being updated internally on morph button triggers. Remove the option when the bug is fixed.
     *      overrideTimeCallback:     Optional callback function replacing Date.now() for testing.
     * }
     */
    constructor(options) {
        super("Virtual Kemper Profiler Player");
        this.options = options || {};

        // Parameter storage
        this.parameters = new VirtualKemperParameters(this);

        // Bidirectional protocol
        this.protocol = new VirtualKemperProtocol(this, options.overrideTimeCallback);

        // Tempo handler
        this.tempo = new VirtualKemperTempo(this, options.overrideTimeCallback);

        // Virtual tuner
        this.tuner = new VirtualKemperTuner(this, options.overrideTimeCallback);

        // Morph state handler
        this.morph = new VirtualKemperMorph(this, options.overrideTimeCallback);

        // Initialize the parameters with values and types
        (new VirtualKemperClientSetup(this)).setup();
        
        this.updateRig();
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
        this.protocol.update();

        this.tempo.update();
        this.tuner.update();
        this.morph.update();
    }

    /**
     * Updates everything to the current rig ID.
     */
    updateRig() {
        const rigId = this.getRigId();

        const bank = Math.floor(rigId / 5);
        const rig = rigId % 5;
        const rigName = "Rig " + (bank + 1) + "-" + (rig + 1);

        this.parameters.get(new NRPNKey([0, 1])).setValue(rigName);
    }

    /**
     * Determine current rig ID
     */
    getRigId() {
        const rigId_cc32 = this.parameters.get(new CCKey(32)).value;
        const rigId_pc = this.parameters.get(new PCKey()).value;

        return 128 * rigId_cc32 + rigId_pc;
    }

    /**
     * Sets the rig ID
     */
    setRigId(rigId) {
        this.parameters.get(new CCKey(32)).setValue(Math.floor(rigId / 128));
        this.parameters.get(new PCKey()).setValue(rigId % 128);

        this.updateRig();
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Called by PySwitch when a message should be sent to the client. 
     * Naming is misleading here: this effectively receives data!
     */
    async send(message) {
        try {
            message = message.toJs();
            // console.log(message)
            
            // Try to parse message: Protocol
            if (this.protocol.parse(message)) return;

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
    queueMessage(message) {   
        // console.log(message)     
        this.messageQueue.push(message);
    }

    /**
     * Stop listening to the input
     */
    detach() {  
        clearInterval(this.#runIntervalHandler);

        this.parameters.destroy();
        this.tempo.destroy();
        this.tuner.destroy();
        this.morph.destroy();

        if (this.#ui) this.#ui.destroy();
    }

    /**
     * If supported, can create a user interface in the passed container DOM element
     */
    getUserInterface(container) {
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