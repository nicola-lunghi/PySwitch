class VirtualKemperParameterDefault extends VirtualKemperParameter {
    
    /**
     * Parse a parameter request message. Must return if successful.
     */
    parse(message) {
        // Is it a request message for this parameter?
        if (!Tools.compareArrays(
            message.slice(0, 8),
            [240, 0, 32, 51, this.client.options.productType, 127, this.requestFunctionCode, 0]
        )) return false;

        // Requested an unknown parameter: Create it
        const newParam = this.client.parameters.get(new NRPNKey(message.slice(8, 10)));

        // Send parameter value
        newParam.send();

        return true;
    }

    /**
     * Send a single parameter (numeric or string)
     */
    send() {
        throw new Error("This shall not be called");
    }

    /**
     * Name for display
     */
    getDisplayName() {
        return "Default: " + (typeof this.value);
    }
}