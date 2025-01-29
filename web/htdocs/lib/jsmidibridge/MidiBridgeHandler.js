/**
 * (C) Thomas Weber 2024 tom-vibrant@gmx.de
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>. 
 */

/**
 * Chunk size for requesting data. The Web MIDI API does silently fail on incoming messages
 * too big, by experiment 111 was the value which was working any time. Should be fixed with
 * issue https://github.com/WebAudio/web-midi-api/issues/158 of the Web MIDI API, which sadly is 
 * still open at the time of writing this (12/2024). Later this could be enlarged to reduce
 * protocol overhead.
 */
const BRIDGE_CHUNK_SIZE_REQUEST = 100;

/**
 * Chunk size for sending data. This also has been determined empirically.
 */
const BRIDGE_CHUNK_SIZE_SEND = 65;

/**
 * Timeout until it is assumed there is no client listening
 */
const BRIDGE_TIMEOUT_INTERVAL_MILLIS = 10000;

/**
 * Debug bridge messages on the console
 */
const BRIDGE_DEBUG = false;

/**
 * Use this class to initialize the bridge and connect it to Web MIDI API ports. 
 * You can either use scan() or directly connect() to a pair of input/output ports.
 */
class MidiBridgeHandler {

    midiAccess = null;           // MIDIAccess instance
    console = console;           // Console output (can be redirected)
    #connectionAttempts = null;  // Map of attempts for scan
    
    constructor(midiAccess = null) {
        this.#connectionAttempts = new Map();
        this.midiAccess = midiAccess;
    }

    /**
     * Sets up MIDI communication. After this, midiAccess is set and can be used.
     */
    async init() {
        const that = this

        return new Promise(function(resolve, reject) {
            async function onMIDISuccess(midiAccess) {
                if (!midiAccess.sysexEnabled) {
                    reject({ message: "You must allow SystemExclusive messages" });
                }

                // Use a handler class for accessing the bridge and creating the connection
                that.midiAccess = midiAccess;

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
     * Scan for ports with bridges behind (attach a bridge to every port, and see where something is coming back).
     * onFinish can be a callback like (data) => boolean, where data is like: 
     * {
     *     bridge: Bridge instance to attach callbacks on. The sendSysex callback is already set.
     *     input: Input port (MIDIInput)
     *     output: Output port (MIDIOutput)
     * }
     * 
     * The callback must return if it used the connection (in this case all other connection attempts are terminated)
     */
    scan(onFinish = null) {
        // Get all in/out pairs sharing the same name
        const ports = this.getMatchingPortPairs();

        const that = this;        
        async function scanPorts(name) {            
            try {
                const connection = await that.connect(name);

                that.console.log("   -> Connection success with " + name);

                if (onFinish) {
                    const terminate = await onFinish(connection);

                    if (terminate) {
                        (new Map(that.#connectionAttempts)).forEach(function(attempt) {
                            attempt.reject();
                        });
                    }
                }
    
            } catch (e) {
                that.console.log("   -> Error connecting to " + name);
            }        
        }

        // Start connecting to all of them (connectToPort will be called async without await 
        // for pseudo parallel processing)
        for (const pair of ports) {            
            scanPorts(pair.input.name);
        }        
    }

    /**
     * Connect to a port input/output pair by port name.
     */
    async connect(portName, timeoutMillis = BRIDGE_TIMEOUT_INTERVAL_MILLIS) {
        const that = this;

        function findPort(ports) {
            for (const port of ports) {
                const handler = port[1];
                    
                if (handler.name == portName) {
                    return handler;
                }                
            }
            
            throw new Error("Port " + portName + " not found");
        }

        const input = findPort(this.midiAccess.inputs);
        const output = findPort(this.midiAccess.outputs);

        // We use a name most likely not existing. If it does exist, this would also work,
        // but the overhead is bigger.
        const path = "/mostlikelynotexistingfolder/ping";

        return new Promise(function(resolve, reject) {
            const bridge = new JsMidiBridge();

            if (BRIDGE_DEBUG) {
                bridge.console = that.console;
            }

            // Connect bridge output to the output
            bridge.sendSysex = async function(manufacturerId, data) {
                await that.#sendSysex(
                    output,
                    manufacturerId,
                    data
                )
            }

            function doResolve(/*data*/) {
                that.#connectionAttempts.delete(portName);

                // Remove callbacks only used for pinging
                bridge.onReceiveFinish = async function() {};
                bridge.onError = async function() {};
                
                // Stop the timout
                clearTimeout(timeout);
                
                resolve({
                    bridge: bridge,
                    name: output.name,
                    input: input,
                    output: output
                });
            }

            function doReject() {
                that.#connectionAttempts.delete(portName);

                // Remove all callbacks
                that.detach({
                    input: input,
                    bridge: bridge
                })

                // Stop the timout
                clearTimeout(timeout);

                reject(new Error("Failed to connect to " + output.name)); 
                // reject({
                //     name: output.name,
                //     input: input,
                //     output: output
                // });
            }

            // Listen to both finish and error events to know there is a bridge listening
            bridge.onReceiveFinish = doResolve;
            bridge.onError = doResolve;
            
            // Attach listener
            that.#listenTo(input, bridge);

            // Request the non-existing file (async but not awaited)
            bridge.request(path, BRIDGE_CHUNK_SIZE_REQUEST);

            // Timeout
            let timeout = setTimeout(doReject, timeoutMillis);

            // Register the connection attempt
            that.#connectionAttempts.set(portName, {
                reject: doReject
            })
        });
    }
    
    /**
     * Called with the result of connect(), this detaches the connection.
     */
    detach(connection) {
        connection.bridge.sendSysex = async function() {};
        connection.bridge.onReceiveFinish = async function() {};
        connection.bridge.onError = async function() {};

        connection.input.onmidimessage = async function() {};
    }

    /**
     * Start listening to a port (connects the bridge to it)
     */
    #listenTo(input, bridge) {
        //this.console.log("Listening to input port " + input.name)

        input.onmidimessage = async function(event) {
            // Check if its a sysex message
            if (event.data[0] != 0xf0 || event.data[event.data.length - 1] != 0xf7) {
                return;
            }

            const manufacturerId = Array.from(event.data).slice(1, 4);
            const data = Array.from(event.data).slice(4, event.data.length - 1);
            
            // Pass it to the bridge
            await bridge.receive({
                manufacturerId: manufacturerId,
                data: data
            });
        }
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
                    //this.console.log("Scan: Found matching ins/outs: " + out_handler.name);
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
      
    /**
     * Send a sysex message to the passed output Port (instance of MIDIOutput)
     */
    async #sendSysex(output, manufacturerId, data) {
        const msg = [
            0xf0
        ].concat(
            manufacturerId,   
            data,
            [
                0xf7
            ]
        );

        await output.send(msg);
    }
}