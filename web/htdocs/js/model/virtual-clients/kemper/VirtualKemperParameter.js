class VirtualKemperParameter {

    setFunctionCode = null;
    requestFunctionCode = null;
    returnFunctionCode = null;
    
    client = null;
    config = null;
    value = null;

    #callbacks = [];   // Callbacks executed on change

    /**
     * {
     *      value,                                      // Value (determines the type, too!) Default: 0
     *      keys: new VirtualKemperParameterKeys(),     // Keys for sending/requesting values (mandatory)
     *      parameterSets,                              // Optional array of parameter set IDs the parameter is part of
     *      callback,                                   // Optional callback. Will be added using addChangeCallback()
     * }
     */
    constructor(client, config) {
        this.client = client;
        this.config = config || {};

        this.value = this.config.value ? this.config.value : 0;
        delete this.config.value;

        if (this.config.callback) {
            this.addChangeCallback(this.config.callback);
            delete this.config.callback;
        }

        this.#detectFunctionCodes();
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
                this.requestFunctionCode = 65;    // 0x41
                this.returnFunctionCode = 1;
                this.setFunctionCode = 1;
                break;

            case "string":
                this.requestFunctionCode = 67;    // 0x43
                this.returnFunctionCode = 3;
                this.setFunctionCode = 3;
                break;

            default:
                throw new Error("Invalid value type: " + (typeof this.value));
        }
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
        // Is it a request message for this parameter?
        if (key instanceof NRPNKey) {           
            // Request parameter
            if (Tools.compareArrays(
                message.slice(0, 8 + key.data.length),
                [240, 0, 32, 51, this.client.config.productType, 127, this.requestFunctionCode, 0].concat(key.data)
            )) {   
                this.send();
                return true;
            }

            // Set parameter
            if (Tools.compareArrays(
                message.slice(0, 8 + key.data.length),
                [240, 0, 32, 51, this.client.config.productType, 127, this.setFunctionCode, 0].concat(key.data)
            )) {
                // Set parameter
                this.setValue(key.evaluateValue(message.slice(8, 10)));
                return true;
            }

        } else if (key instanceof CCKey) {
            if (Tools.compareArrays(
                message.slice(0, 2),
                [176, key.control]
            )) {
                // Set parameter
                this.setValue(key.evaluateValue(message[2]));
                return true;
            }

        } else if (key instanceof PCKey) {
            if (message[0] == 192) {
                // Set parameter
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

        // Set new value
        this.value = value;

        // Update UI and internal state
        for (const callback of this.#callbacks) {
            callback(this, value);
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
                this.encodeValue(this.value),
                [247]
            );

            //console.log("Send NRPN", msg)
            this.client.queueMessage(msg);
        
        } else if (this.config.keys.send instanceof CCKey) {
            const msg = [176, this.config.keys.send.control, this.value]
            
            // console.log("Send CC", msg)
            this.client.queueMessage(msg);

        } else if (this.config.keys.send instanceof PCKey) {
            const msg = [192, this.value]
            
            // console.log("Send PC", msg)
            this.client.queueMessage(msg);

        } else {
            throw new Error("Invalid key type: " + (typeof this.config.keys.send));
        }
    }

    /**
     * Returns a byte array containing the value
     */
    encodeValue(value) {
        switch (typeof value) {
            case "number":
                const lsb = value % 128;
                const msb = Math.floor(value / 128);
                return [msb, lsb];

            case "string":
                const ret = [];
                for (var i = 0; i < value.length; ++i) {
                    ret.push(value.charCodeAt(i));                    
                }
                ret.push(0);   // Null termination
                return ret;

            default:
                throw new Error("Invalid value type: " + (typeof value));
        }
    }
}