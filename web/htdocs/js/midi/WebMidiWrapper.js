class WebMidiWrapper {

    messageQueue = [];   // Queue of raw MIDI bytes. Will be filled here message by message, and fetched from the python midi wrappers

    #input = null;       // Web MIDI input port
    #output = null;      // Web MIDI output port
    
    constructor(input, output) {
        this.#input = input;
        this.#output = output;

        // Receive messages (thise go into a queue)
        const that = this;
        this.#input.onmidimessage = function(event) {
            //console.log("Receive ", event.data)
            that.messageQueue.push(event.data);
        }
    }

    /**
     * Send a MIDI message. Expects a byte array of raw data.
     */
    async send(message) {
        //console.log("Send ", message)
        await this.#output.send(message.toJs());        
    }

    /**
     * Stop listening to the input
     */
    detach() {
        this.#input.onmidimessage = null;
    }
}