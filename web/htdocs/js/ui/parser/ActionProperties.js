class ActionProperties {
    
    #model = null;

    constructor(model) {
        this.#model = model;
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        console.log(this.#model)

        return $('<div class="action-properties" />').append(
            $('<div class="action-comment" />')
            .text(this.#model.comment ? this.#model.comment : "No information available")
        )
    }
}