class ParameterKeys {
    send = null;
    receive = null;

    /**
     * {
     *      send:     Key instance for sending data to the controller. Also used for receiving requests for values. Cannot be an array. Optional.
     *      receive:  Key instance(s) for receiving data. Can be an array. If not set, the send key will be used.
     * }
     */
    constructor(config) {
        this.send = config.send;
        this.receive = config.receive;

        // Ensure that receiveKey is an Array
        if (this.receive) {
            if (!Array.isArray(this.receive)) {
                // Single entry
                this.receive = [this.receive];
            }

            // Alse receive values for the sending key
            if (this.send) {
                this.receive.push(this.send);
            }
        } else {
            if (!this.send) {
                throw new Error("Invalid definitions for keys");
            }

            // Use send key as receive key
            this.receive = [this.send];
        }
    }

    /**
     * Get ID of the constellation
     */
    getId() {
        if (this.send) return this.send.getId();

        let ret = "";
        for (const r of this.receive) {
            ret += r.getId();
        }
        return ret;
    }
}

/**
 * Key for a NRPN parameter
 */
class NRPNKey {
    constructor(data) {
        this.data = data;
    }

    getId() {
        return JSON.stringify({ data: this.data });
    }

    evaluateValue(value) {
        return value[0] * 128 + value[1];
    }
}

/**
 * Key for a CC parameter
 */
class CCKey {
    constructor(control) {
        this.control = control;
    }

    getId() {
        return JSON.stringify({ control: this.control });
    }

    evaluateValue(value) {
        return value;        
    }
}

/**
 * Key for a PC parameter
 */
class PCKey {
    getId() {
        return JSON.stringify({ program: true });
    }

    evaluateValue(value) {
        return value;        
    }
}