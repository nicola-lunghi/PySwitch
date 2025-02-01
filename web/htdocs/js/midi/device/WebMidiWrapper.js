class WebMidiWrapper {

    messageQueue = [];   // Queue of raw MIDI bytes. Will be filled here message by message, and fetched from the python midi wrappers

    #midi = null;        // MidiHandler instance
    #input = null;       // Web MIDI input port
    #output = null;      // Web MIDI output port
    #listener = null;

    constructor(midi, input, output) {
        this.#input = input;
        this.#output = output;
        this.#midi = midi;

        // Receive messages (these go into a queue)
        const that = this;
        this.#midi.addListener(
            this.#listener = new MidiListener(
                this.#input.name, 
                async function(data) {
                    that.messageQueue.push(data);
                }
            )
        );
    }

    /**
     * Send a MIDI message. Expects a byte array of raw data.
     */
    async send(message) {
        await this.#output.send(message.toJs());
    }

    /**
     * Stop listening to the input
     */
    detach() {
        this.#midi.removeListener(this.#listener);
        this.#listener = null;
    }
}