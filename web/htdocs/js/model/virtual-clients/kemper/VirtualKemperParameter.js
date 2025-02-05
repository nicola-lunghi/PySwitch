class VirtualKemperParameter {

    requestFunctionCode = null;
    returnFunctionCode = null;
    
    client = null;
    config = null;

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
        // Is it a request message for this parameter?
        if (!Tools.compareArrays(
            message.slice(0, 10),
            [240, 0, 32, 51, this.client.config.productType, 127, this.requestFunctionCode, 0].concat(this.config.key)
        )) return false;

        // Send parameter value
        this.send();

        return true;
    }

    /**
     * Send a single parameter (numeric or string)
     */
    send() {
        const msg = [240, 0, 32, 51, 0, 0, this.returnFunctionCode, 0].concat(
            Array.from(this.config.key), 
            this.encodeValue(this.config.value),
            [247]
        );
        
        this.client.queueMessage(msg);
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