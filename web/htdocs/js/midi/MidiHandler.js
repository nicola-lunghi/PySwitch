/**
 * Implements the MIDI device scanning algorithms
 */
class MidiHandler {

    midiAccess = null;

    #listeners = null;

    /**
     * Sets up MIDI communication. After this, midiAccess is set and can be used.
     */
    async init() {
        const that = this;

        return new Promise(function(resolve, reject) {
            async function onMIDISuccess(midiAccess) {
                if (!midiAccess.sysexEnabled) {
                    reject({ message: "You must allow SystemExclusive messages" });
                }

                // Use a handler class for accessing the bridge and creating the connection
                that.midiAccess = midiAccess;

                // Get all in/out pairs sharing the same name
                const ports = that.getMatchingPortPairs();

                // Attach a globally used onmidimessage callback on all available input ports.
                that.#initReceive(ports);

                resolve();
            }

            async function onMIDIFailure(msg) {
                reject({ message: "Failed to get MIDI access: " + msg });
            }

            navigator.requestMIDIAccess({ sysex: true })
                .then(onMIDISuccess, onMIDIFailure);
        });
    }

    /**
     * Scans for devices. The scan callback can add ConnectionAttempt instances to a map which are terminated of finish() returns true.
     * 
     * id: Scan ID to manag attempts
     * connect(portName, attempts) => connection      // Must try to connect, and return a descriptor object of successful
     * onSuccess(connection, attempts) => void        // Called when an attempt has succeeded
     * onFailure() => void                            // Called when all attempts failed
     */
    scan(connect, onSuccess = null, onFailure = null) {
        // Get all in/out pairs sharing the same name
        const ports = this.getMatchingPortPairs();

        const attempts = new Map();
        let success = false;

        async function scanPorts(name) {            
            try {
                const connection = await connect(name, attempts);

                console.log("   -> Connection success with " + name);
                success = true;

                if (onSuccess) {
                    await onSuccess(connection, attempts);               
                }
    
            } catch (e) {
                //console.error(e);
                console.log("   -> Error connecting to " + name);

                // When the last attempt failed
                if (onFailure && !success && !attempts.size) {
                    await onFailure();
                }
            }        
        }

        // Start connecting to all of them (connectToPort will be called async without await 
        // for pseudo parallel processing)
        for (const pair of ports) {
            scanPorts(pair.input.name);
        }        
    }

    /**
     * Add a listener to the input listeners map
     */
    addListener(listener) {
        if (!(listener instanceof MidiListener)) {
            throw new Error("Invalid listener: " + typeof listener);
        }
        this.#listeners.set(listener.id, listener);        
    }

    /**
     * Removes a listener from the input listeners map
     */
    removeListener(listener) {
        if (!listener) return;

        this.#listeners.delete(listener.id);
    }

    /**
     * Attach a globally used onmidimessage callback on all available input ports.
     */
    #initReceive(ports) {
        this.#listeners = new Map();

        const that = this;
        for (const pair of ports) {
            pair.input.onmidimessage = async function(event) {
                for (const [id, listener] of that.#listeners) {
                    await listener.receive(pair.name, event.data);
                }
            }
        }
    }

    /**
     * Tries to find the port pair and returns it, or null if not found.
     */
    getPortPair(portName) {
        const ports = this.getMatchingPortPairs();
        for (const port of ports) {
            if (port.name != portName) continue;
            return port;
        }
        return null;
    }

    /**
     * Gets a port list, which is an array of objects like:
     * {
     *     input:
     *     output:
     * }
     */
    getMatchingPortPairs() {
        const ret = [];

        // Inputs
        for (const input of this.midiAccess.inputs) {
            const in_handler = input[1];

            // Get corresponding output
            for (const output of this.midiAccess.outputs) {
                const out_handler = output[1];

                if ((out_handler.manufacturer == in_handler.manufacturer) && (out_handler.name == in_handler.name)) {
                    ret.push({
                        name: out_handler.name,
                        input: in_handler,
                        output: out_handler
                    });
                }
            }
        }

        return ret;
    } 
}