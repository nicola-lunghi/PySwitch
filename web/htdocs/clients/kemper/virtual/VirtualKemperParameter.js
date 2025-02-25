class VirtualKemperParameter {

    setFunctionCode = null;
    requestFunctionCode = null;
    returnFunctionCode = null;
    
    client = null;
    config = null;
    value = null;

    #callbacks = [];   // Callbacks executed on change
    valueType = null;

    // // Debug specific keys
    // debugParamKeys = [
    //     // new NRPNKey([127, 126]),     // Tuner state
    //     // new NRPNKey([0, 11]),        // Morph state
    //     // new NRPNKey([60, 3]),        // DLY state
    //     // new NRPNKey([50, 3]),        // A state
    //     new CCKey(50),                   // Select rig
    //     new CCKey(51),                   // Select rig
    //     new CCKey(52),                   // Select rig
    //     new CCKey(53),                   // Select rig
    //     new CCKey(54),                   // Select rig
    // ];

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
    constructor(client, config) {
        this.client = client;
        this.config = config || {};

        if (this.config.keys && !(this.config.keys instanceof VirtualKemperParameterKeys)) throw new Error("Invalid parameter set");

        this.value = this.config.value ? this.config.value : 0;
        delete this.config.value;

        if (this.config.callback) {
            this.addChangeCallback(this.config.callback);
            delete this.config.callback;
        }

        this.#detectFunctionCodes();
        this.#detectValueType();
    }

    /**
     * Name for display
     */
    getDisplayName() {
        if (this.config.keys) return this.config.keys.getDisplayName();
        return "??";
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
                this.requestFunctionCode = this.config.requestFunctionCode ? this.config.requestFunctionCode : 65;    // 0x41
                this.returnFunctionCode = this.config.returnFunctionCode ? this.config.returnFunctionCode : 1;
                this.setFunctionCode = this.config.setFunctionCode ? this.config.setFunctionCode : 1;
                break;

            case "string":
                this.requestFunctionCode = this.config.requestFunctionCode ? this.config.requestFunctionCode : 67;    // 0x43
                this.returnFunctionCode = this.config.returnFunctionCode ? this.config.returnFunctionCode : 3;
                this.setFunctionCode = this.config.setFunctionCode ? this.config.setFunctionCode : 3;
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
        for (const key of this.config.keys.receive) {
            if (this.#parseKey(key, message)) return true;
        }

        return false;
    }

    #parseKey(key, message) {
        if (key instanceof NRPNKey) {           
            // NRPN: Request parameter
            if (Tools.compareArrays(
                message.slice(0, 8 + key.data.length),
                [240, 0, 32, 51, this.client.config.productType, 127, this.requestFunctionCode, 0].concat(key.data)
            )) {   
                this.send();                
                return true;
            }

            // NRPN: Set parameter
            if (Tools.compareArrays(
                message.slice(0, 8 + key.data.length),
                [240, 0, 32, 51, this.client.config.productType, 127, this.setFunctionCode, 0].concat(key.data)
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
        if (!this.config.noBuffer && this.value == value) return;

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
        if (this.config.parameterSets && this.config.parameterSets.includes(this.client.protocol.parameterSet)) {
            this.send();
        }
    }

    /**
     * Send a single parameter (numeric or string)
     */
    send() {
        if (!this.config.keys.send) return;

        if (this.config.keys.send instanceof NRPNKey) {
            const msg = [240, 0, 32, 51, 0, 0, this.returnFunctionCode, 0].concat(
                Array.from(this.config.keys.send.data),                 
                this.config.keys.send.encodeValue(this.value),
                [247]
            );
            
            this.client.queueMessage(msg);
            this.#debugParam("send: (raw: " + this.value + ")" + msg);
        
        } else if (this.config.keys.send instanceof CCKey) {
            const msg = [176, this.config.keys.send.control, this.value]
            
            this.client.queueMessage(msg);
            this.#debugParam("send: (raw: " + this.value + ")" + msg);

        } else if (this.config.keys.send instanceof PCKey) {
            const msg = [192, this.value]
            
            this.client.queueMessage(msg);
            this.#debugParam("send: (raw: " + this.value + ")" + msg);

        } else {
            throw new Error("Invalid key type: " + (typeof this.config.keys.send));
        }
    }

    /**
     * Print debug info when the parameter is in debugParamKeys
     */
    #debugParam(msg) {
        if (!this.config.keys || !this.debugParamKeys) return;

        for (const key of this.debugParamKeys) {
            if (key.getId() != this.config.keys.getId()) continue;

            console.log(key.getDisplayName(), msg);
        }
    }
}