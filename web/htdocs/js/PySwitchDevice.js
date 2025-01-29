class PySwitchDevice {

    #controller = null;           // PySwitch runner
    bridge = null;                // MIDI bridge handler (connects to the Controller running PyMidiBridge, and is reused for connecting to the client, too)

    #connection = null;           // Current connection, holding the bridge instance and ports etc.

    constructor(controller) {
        this.#controller = controller;
    }

    /**
     * Set up MIDI bridge (this sets up Web MIDI)
     */
    async init() {
        this.bridge = new MidiBridgeHandler();
        await this.bridge.init();
    }

    /**
     * Returns the current connected port name.
     */
    portName() {
        if (!this.#connection) return "";
        return this.#connection.name;
    }

    /**
     * Tries to find the port pair and returns it, or null if not found.
     */
    getPortPair(portName) {
        const ports = this.bridge.getMatchingPortPairs();
        for (const port of ports) {
            if (port.name != portName) continue;
            return port;
        }
        return null;
    }

    /**
     * Connect to the passed port name
     */
    async connect(connectionName) {
        if (this.#connection && this.#connection.name == connectionName) return;   // Already connected to the bridge
        
        this.#controller.ui.progress(0, "Connecting to controller " + connectionName);

        if (this.#connection) {
            this.bridge.detach(this.#connection);
        }

        let connection = null;
        try {
            connection = await this.bridge.connect(connectionName, 3000);

        } catch (e) {
            this.#controller.ui.progress(1);
            throw new Error("Failed to connect to controller " + connectionName);
        }

        const bridge = connection.bridge;

        const that = this;

        console.log("Connected to controller " + connectionName);

        // // Progress (send)
        // bridge.onSendProgress = async function(data) {            
        //     if (data.type == "error") return;

        //     that.#controller.ui.progress((data.chunk + 1) / data.numChunks, "Writing chunk " + data.chunk + " of " + data.numChunks);

        //     if (data.chunk + 1 == data.numChunks) {
        //         console.info("Successfully saved " + data.path);
        //     }
        // };

        // Receive start
        bridge.onReceiveStart = async function(data) {
            that.#controller.ui.progress(0, "Loading " + data.path);
        };

        // Progress (receive)
        bridge.onReceiveProgress = async function(data) {
            that.#controller.ui.progress((data.chunk + 1) / data.numChunks, "Loading chunk " + data.chunk + " of " + data.numChunks);
        };

        // Receive finish
        bridge.onReceiveFinish = async function(data) {
            that.#controller.ui.progress(1);
            console.info("Loaded " + portName);
        };

        // Error handling for MIDI errors coming from the bridge
        bridge.onError = async function(message) {
            that.#controller.ui.progress(1);
            that.#controller.message(message);
        }      
        
        this.#connection = connection;        
    }

    /**
     * Returns the content of the passed file path, loaded from the device behind the currently connected bridge.
     */
    async loadFile(path) {
        if (!this.#connection) {
            throw new Error("No controller connected");
        }

        const bridge = this.#connection.bridge;

        const that = this;
        return new Promise(async function(resolve, reject) {
            bridge.throwExceptionsOnReceive = true;

            bridge.onReceiveStart = async function(data) {                
                that.#controller.ui.progress(0, "Loading " + data.path);
            };

            bridge.onReceiveProgress = async function(data) {
                that.#controller.ui.progress((data.chunk + 1) / data.numChunks, "Loading " + data.path); //"Loading chunk " + data.chunk + " of " + data.numChunks);
            };

            bridge.onReceiveFinish = async function(data) {
                that.#controller.ui.progress(1);
                resolve(data.data);
            }

            bridge.onError = async function(message) {
                console.error(message);
                reject(message)
            }  
    
            await bridge.request(path, BRIDGE_CHUNK_SIZE_REQUEST);
        })        
    }
}