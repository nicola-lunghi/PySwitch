/**
 * Manages connection to client devices (like Kemper)
 */
class ClientController {

    #controller = null;

    current = null;     // Name of the currently connected client

    constructor(controller) {
        this.#controller = controller;
    }
    
    /**
     * Initialize client to the given config instance.
     */
    async init(config) {
        if (!config) return;

        const savedClient = this.#controller.getState("client");

        if (savedClient == "auto" || !savedClient) {
            await this.#scan(config);
        } else {
            await this.#connect(savedClient, config);
        }
    }
            
    /**
     * Scans for clients of the given config.
     */
    async #scan(config) {
        const that = this;

        await this.#controller.midi.scan(
            // connect
            async function(portName, attempts) {
                return await that.#scanPort(config, portName, attempts);
            },

            // finish
            async function(connection, attempts) {
                // Reject all older attempts
                (new Map(attempts)).forEach(async function(attempt) {
                    await attempt.reject();
                });

                //console.log("Found client: ", connection);
                await that.#connect(connection.name, config);
            },

            // onFailure
            async function() {
                await that.#connect("virtual", config);
            }
        );
    }

    /**
     * Checks if the passed port is connected to a valid client for the current configuration. If yes, returns
     * a connection object.
     */
    async #scanPort(config, portName, attempts, timeoutMillis = 1000) {
        console.log("Scan for client on " + portName)
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

        const input = findPort(this.#controller.midi.midiAccess.inputs);
        const output = findPort(this.#controller.midi.midiAccess.outputs);

        return new Promise(async function(resolve, reject) {
            // Get a detector fir the config
            const detector = await config.parser.getClientDetector();
            
            function cleanup() {
                if (attempts) {
                    attempts.delete(portName);
                }

                // Stop the timout
                clearTimeout(timeout);

                // Remove listener (else the detector would parse all messages, too)
                that.#controller.midi.removeListener(listener);
            }

            function doResolve(/*data*/) {
                cleanup();
                resolve({
                    name: output.name,
                    input: input,
                    output: output
                });
            }

            function doReject() {
                cleanup();
                reject(new Error("Failed to connect to " + output.name)); 
            }

            // Use the detector to check if there is a client listening
            const listener = await detector.test(that.#controller.midi, input, output, doResolve);

            // Timeout
            const timeout = setTimeout(doReject, timeoutMillis);

            // Register the connection attempt
            if (attempts) {
                attempts.set(portName, {
                    reject: doReject
                });
            }            
        });
    }

    /**
     * Connect to a client directly
     */
    async #connect(portName, config) {
        // First throw out the old MIDI wrapper, if any
        this.#controller.pyswitch.setMidiWrapper(null);
        this.current = null;

        // In case its a virtual client, use that one        
        if (portName == "virtual") {
            // Create virtual client
            const virtualClient = await VirtualClient.getInstance(config);
            if (!virtualClient) {
                this.#controller.ui.message((await config.name()) + " does not support a virtual client device", "W");
                return;
            }

            // Set client as MIDI wrapper to connect it to PySwitch
            this.#controller.pyswitch.setMidiWrapper(virtualClient);
            
            // Run the virtual client
            virtualClient.run(5);

            // Show user interface, if any
            this.#controller.ui.showVirtualClient(virtualClient);

            this.#controller.ui.message("Connecting to " + virtualClient.name, "I");
            return;
        } else {
            this.#controller.ui.showVirtualClient(null);
        }

        // Search for the ports
        const port = this.#controller.midi.getPortPair(portName);       
        if (!port) {
            this.#controller.ui.message("No client device connected", "I");
            return;
        }

        // Set a MIDI wrapper to connect the ports to PySwitch
        this.#controller.pyswitch.setMidiWrapper(
            new PythonMidiWrapper(this.#controller.midi, port.input, port.output)
        );

        // Report states etc.
        this.#controller.ui.message("Connecting to client at " + port.name, "I");

        this.current = portName;
    }
}