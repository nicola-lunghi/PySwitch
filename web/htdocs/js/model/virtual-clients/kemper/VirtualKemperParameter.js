class VirtualKemperParameter {

    requestFunctionCode = null;
    returnFunctionCode = null;
    
    client = null;
    config = null;

    /**
     * {
     *      value,          // Value (determines the type, too!)
     *      key,            // Key for sending/requesting values
     *      receiveKey,     // Optional key(s) for receiving value changes. Can be a single key or an array of keys.
     *      parameterSets   // Optional list of parameter set IDs the parameter is part of
     * }
     */
    constructor(client, config) {
        this.client = client;
        this.config = config || {};

        this.#detectFunctionCodes();
    }

    /**
     * Auto detect the send and return function ciodes from the value type
     */
    #detectFunctionCodes() {
        switch (typeof this.config.value) {
            case "number":
                this.requestFunctionCode = 65;    // 0x41
                this.returnFunctionCode = 1;
                break;

            case "string":
                this.requestFunctionCode = 67;    // 0x43
                this.returnFunctionCode = 3;
                break;

            default:
                throw new Error("Invalid value type: " + (typeof this.config.value));
        }
    }

    /**
     * Parse a parameter request message. Must return if successful.
     */
    parse(message) {
        // Ensure that receiveKey is an Array
        if (this.config.receiveKey) {
            if (!Array.isArray(this.config.receiveKey)) {
                // Single entry
                this.config.receiveKey = [this.config.receiveKey];
            }
        } else {
            // Use general key
            this.config.receiveKey = [this.config.key]
        }

        // Try to parse with all keys
        for (const key of this.config.receiveKey) {
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

            // // Set parameter
            // if (Tools.compareArrays(
            //     message.slice(0, 8 + key.data.length),
            //     [240, 0, 32, 51, this.client.config.productType, 127, this.requestFunctionCode, 0].concat(key.data)
            // )) {
            //     // Set parameter
            //          return true;
            // }

        } else if (key instanceof CCKey) {
            if (Tools.compareArrays(
                message.slice(0, 2),
                [176, key.control]
            )) {
                // TODO set value




                return true;
            }

        } else {
            throw new Error("Invalid key type: " + (typeof key));
        }

        return false;
    }

    /**
     * Send a single parameter (numeric or string)
     */
    send() {
        if (this.config.key instanceof NRPNKey) {
            const msg = [240, 0, 32, 51, 0, 0, this.returnFunctionCode, 0].concat(
                Array.from(this.config.key), 
                this.encodeValue(this.config.value),
                [247]
            );
            
            this.client.queueMessage(msg);
        
        } else if (this.config.key instanceof CCKey) {
            const msg = [176, this.config.key.control, this.config.value]
            
            this.client.queueMessage(msg);

        } else {
            throw new Error("Invalid key type: " + (typeof this.config.key));
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