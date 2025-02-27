/**
 * Base class for virtual clients
 */
class VirtualClient {

    name = null;
    messageQueue = [];   // Queue of raw MIDI bytes. Will be filled here message by message, and fetched from the python midi wrappers
    
    constructor(name) {
        this.name = name;
    }

    /**
     * Send a MIDI message. Expects a byte array of raw data.
     */
    async send(message) {        
    }

    /**
     * Start processing regular updates to send messages. If not set, the caller has to 
     * call update() regularly.
     */
    run(updateInterval) {
    }

    /**
     * Stop listening to the input, and remove all UIs
     */
    detach() {        
    }

    /**
     * If supported, can create a user interface in the passed container DOM element
     */
    createUserInterface(container) {
    }
}