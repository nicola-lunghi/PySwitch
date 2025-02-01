class MidiListener {
    
    id = null;
    portName = null;
    #callback = null;
    
    /**
     * callback(midiData) => void
     */
    constructor(portName, callback) {
        this.id = Tools.uuid();

        this.portName = portName;
        this.#callback = callback;
    }

    /**
     * If the incoming message is for our port, proccess it with our callback.
     */
    async receive(portName, data) {
        if (portName != this.portName) return;

        await this.#callback(data);
    }
}