class VirtualKemperParameter {

    setFunctionCode = null;
    requestFunctionCode = null;
    returnFunctionCode = null;
    
    client = null;
    options = null;
    value = null;

    #callbacks = [];   // Callbacks executed on change
    valueType = null;

    // // Debug specific keys
    debugParamKeys = [
    //     // new NRPNKey([127, 126]),     // Tuner state
    //     // new NRPNKey([0, 11]),        // Morph state
    //     // new NRPNKey([60, 3]),        // DLY state
    //     // new NRPNKey([50, 3]),        // A state
    //     new CCKey(50),                   // Select rig
    //     new CCKey(51),                   // Select rig
    //     new CCKey(52),                   // Select rig
    //     new CCKey(53),                   // Select rig
    //     new CCKey(54),                   // Select rig
    //     new CCKey(11),                   // Morph Pedal
    //     new NRPNKey([0, 11])             // Morph Pedal
         new NRPNKey([0, 1]),             // Rig name
         new NRPNKey([0, 16])             // Amp name
    ];

    /**
     * {
     *      value,                                      // Value (determines the type, too!) Default: 0
     *      keys: new VirtualKemperParameterKeys(),     // Keys for sending/requesting values (mandatory)
     *      parameterSets,                              // Optional array of parameter set IDs the parameter is part of
     *      callback,                                   // Optional callback. Will be added using addChangeCallback()
     *      requestFunctionCode,
     *      returnFunctionCode,
     *      setFunctionCode
     * }
     */
    constructor(client, options) {
        this.client = client;
        this.options = options || {};

        if (this.options.keys && !(this.options.keys instanceof VirtualKemperParameterKeys)) throw new Error("Invalid parameter set");

        this.value = this.options.value ? this.options.value : 0;
        delete this.options.value;

        if (this.options.callback) {
            this.addChangeCallback(this.options.callback);
            delete this.options.callback;
        }

        this.#detectFunctionCodes();
        this.#detectValueType();
    }

    /**
     * Name for display
     */
    getDisplayName() {
        const tokens = [];
        if (this.options.name) tokens.push(this.options.name);
        if (this.options.keys) tokens.push(this.options.keys.getDisplayName());

        const ret = tokens.join(" ");
        return ret.length ? ret : "??";
    }

    /**
     * callback(VirtualKemperParameter, value) => void
     */
    addChangeCallback(callback) {
        this.#callbacks.push(callback);
    }

    /**
     * Auto detect the send and return function ciodes from the value type
     */
    #detectFunctionCodes() {
        switch (typeof this.value) {
            case "number":
                this.requestFunctionCode = this.options.requestFunctionCode ? this.options.requestFunctionCode : 65;    // 0x41
                this.returnFunctionCode = this.options.returnFunctionCode ? this.options.returnFunctionCode : 1;
                this.setFunctionCode = this.options.setFunctionCode ? this.options.setFunctionCode : 1;
                break;

            case "string":
                this.requestFunctionCode = this.options.requestFunctionCode ? this.options.requestFunctionCode : 67;    // 0x43
                this.returnFunctionCode = this.options.returnFunctionCode ? this.options.returnFunctionCode : 3;
                this.setFunctionCode = this.options.setFunctionCode ? this.options.setFunctionCode : 3;
                break;

            default:
                throw new Error("Invalid value type: " + (typeof this.value));
        }
    }

    /**
     * Auto detect value type
     */
    #detectValueType() {
        this.valueType = typeof this.value;
    }

    /**
     * Parse a parameter request message. Must return if successful.
     */
    parse(message) {        
        // Try to parse with all keys
        for (const key of this.options.keys.receive) {
            if (this.#parseKey(key, message)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Parse one receive key 
     */
    #parseKey(key, message) {
        if (key instanceof NRPNKey) {           
            // NRPN: Request parameter
            if (Tools.compareArrays(
                message.slice(0, 8 + key.data.length),
                [240, 0, 32, 51, this.client.options.productType, 127, this.requestFunctionCode, 0].concat(key.data)
            )) {   
                this.send();                
                return true;
            }

            // NRPN: Set parameter
            if (Tools.compareArrays(
                message.slice(0, 8 + key.data.length),
                [240, 0, 32, 51, this.client.options.productType, 127, this.setFunctionCode, 0].concat(key.data)
            )) {
                const value = key.evaluateValue(message.slice(8 + key.data.length, 10 + key.data.length));
                this.setValue(value);
                return true;
            }
        
        } else if (key instanceof CCKey) {
            // CC: Set parameter
            if (Tools.compareArrays(
                message.slice(0, 2),
                [176, key.control]
            )) {
                const value = key.evaluateValue(message[2]);
                this.setValue(value);
                return true;
            }

        } else if (key instanceof PCKey) {
            // PC: Set parameter
            if (message[0] == 192) {
                this.setValue(key.evaluateValue(message[1]));
                return true;
            }

        } else {
            throw new Error("Invalid key type: " + (typeof key));
        }

        return false;
    }

    /**
     * Set the value with listeners update, if changed
     */
    setValue(value) {
        if (!this.options.noBuffer && this.value == value) return;

        if (value !== null && (typeof value != this.valueType)) {
            throw new Error("Invalid value type in setValue: " + (typeof value));
        }
        
        this.value = value;
        
        this.#debugParam("setValue: " + this.value);

        // Update UI and internal state
        for (const callback of this.#callbacks) {
            callback(this, this.value);
        }
        
        // Send current state, if the parameter is part of an active parameter set. All others must be requested.
        if (this.options.parameterSets && this.options.parameterSets.includes(this.client.protocol.parameterSet)) {
            this.send();
        }
    }

    /**
     * Send a single parameter (numeric or string)
     */
    send() {
        if (!this.options.keys.send) return;

        if (this.options.keys.send instanceof NRPNKey) {
            const msg = [240, 0, 32, 51, 0, 0, this.returnFunctionCode, 0].concat(
                Array.from(this.options.keys.send.data),                 
                this.options.keys.send.encodeValue(this.value),
                [247]
            );
            
            this.client.queueMessage(msg, this.getDisplayName());
            this.#debugParam("send: (raw: " + this.value + ")" + msg);
        
        } else if (this.options.keys.send instanceof CCKey) {
            const msg = [176, this.options.keys.send.control, this.options.keys.send.encodeValue(this.value)]
            
            this.client.queueMessage(msg, this.getDisplayName());
            this.#debugParam("send: (raw: " + this.value + ")" + msg);

        } else if (this.options.keys.send instanceof PCKey) {
            const msg = [192, this.options.keys.send.encodeValue(this.value)]
            
            this.client.queueMessage(msg, this.getDisplayName());
            this.#debugParam("send: (raw: " + this.value + ")" + msg);

        } else {
            throw new Error("Invalid key type: " + (typeof this.options.keys.send));
        }
    }

    /**
     * Print debug info when the parameter is in debugParamKeys
     */
    #debugParam(msg) {
        if (!this.options.keys || !this.debugParamKeys) return;

        for (const key of this.debugParamKeys) {
            if (key.getId() != this.options.keys.getId()) continue;

            console.log(key.getDisplayName(), msg);
        }
    }
}