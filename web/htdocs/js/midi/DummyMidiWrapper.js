class DummyMidiWrapper {

    messageQueue = [];   // Queue of raw MIDI bytes. Will be filled here message by message, and fetched from the python midi wrappers

    /**
     * Send a MIDI message. Expects a byte array of raw data.
     */
    async send(message) {}

    /**
     * Stop listening to the input
     */
    detach() {}
}