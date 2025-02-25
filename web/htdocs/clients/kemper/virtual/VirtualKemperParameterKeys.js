class VirtualKemperParameterKeys {
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

        if (this.send && !(this.send instanceof ParameterKey)) throw new Error("Invalid send key");
        
        for (const r of this.receive) {
            if (!(r instanceof ParameterKey)) throw new Error("Invalid receive key");
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

    /**
     * Name to display
     */
    getDisplayName() {
        if (this.send) return this.send.getDisplayName();

        const ret = [];
        for (const r of this.receive) {
            ret.push(r.getDisplayName());
        }
        return ret.join(", ");
    }

    // /**
    //  * Returns if the keys are mixed type
    //  */
    // mixed() {
    //     let sendNRPN = (this.send instanceof NRPNKey);
    //     let receiveHasNRPN = false;
    //     let receiveHasOthers = false;

    //     for (const r of this.receive) {
    //         if (r instanceof NRPNKey) {
    //             receiveHasNRPN = true;
    //         } else {
    //             receiveHasOthers = true;
    //         }
    //     }

    //     return ((sendNRPN && receiveHasOthers) || (!sendNRPN && receiveHasNRPN))
    // }
}

/**************************************************************/

class ParameterKey {

    /**
     * Must return a unique ID from the key
     */
    getId() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Name to display
     */
    getDisplayName() {
        throw new Error("Must be implemented in child classes");
    }

    /**
     * Returns a byte array containing the value
     */
    encodeValue(value) {
        throw new Error("Not supported for this type");
    }
}

/**
 * Key for a NRPN parameter
 */
class NRPNKey extends ParameterKey {
    constructor(data) {
        super();

        if (!(Array.isArray(data) || (data instanceof Uint8Array))) throw new Error("Invalid NRPN data")
        this.data = Array.from(data);
    }

    getId() {
        return JSON.stringify({ data: this.data });
    }

    getDisplayName() {
        return this.data.join("|");
    }

    evaluateValue(value) {
        return value[0] * 128 + value[1];
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

/**
 * Key for a CC parameter
 */
class CCKey extends ParameterKey {
    constructor(control) {
        super();

        if (typeof control != "number") throw new Error("Invalid CC control")

        this.control = control;
    }

    getId() {
        return JSON.stringify({ control: this.control });
    }

    getDisplayName() {
        return "" + this.control;
    }

    evaluateValue(value) {
        return value;        
    }
}

/**
 * Key for a PC parameter
 */
class PCKey extends ParameterKey {
    getId() {
        return JSON.stringify({ program: true });
    }

    getDisplayName() {
        return "PC";
    }
}