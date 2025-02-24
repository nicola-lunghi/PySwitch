class BrowserProvider {
    
    /**
     * Must return a hierarchical TOC
     */
    async getToc() {
        throw new Error("Must be implemented in child classes");
    }    
}