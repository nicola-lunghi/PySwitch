class VirtualKemperParameterDefault extends VirtualKemperParameter {
    
    /**
     * Parse a parameter request message. Must return if successful.
     */
    parse(message) {
        // Is it a request message for this parameter?
        if (!Tools.compareArrays(
            message.slice(0, 8),
            [240, 0, 32, 51, this.client.config.productType, 127, this.requestFunctionCode, 0]
        )) return false;

        // Send parameter value
        this.send(message.slice(8, 10));

        return true;
    }

    /**
     * Send a single parameter (numeric or string)
     */
    send(keyData) {
        const msg = [240, 0, 32, 51, 0, 0, this.returnFunctionCode, 0].concat(
            Array.from(keyData), 
            this.encodeValue(this.value), 
            [247]
        );
        
        this.client.queueMessage(msg);
    }
}