/**
 * MIDI Monitor tab
 */
class MidiMonitor extends Tab {

    #monitorElement = null;
    #maxNumMessages = 100;
    #run = true
    #virtualClients = [];
    
    constructor(controller, tabName) {
        let monitorElement = null;
        let monitorContainer = null;

        super(
            monitorContainer = $('<div class="midi-monitor-container" />').append(
                // Editor content
                $('<table class="midi-monitor" />').append(
                    monitorElement = $('<tbody />')
                )
            ), 
            tabName
        );

        this.#monitorElement = monitorElement;
        
        const that = this;
        monitorContainer.on('click', function() {
            if (that.#run) {
                that.addComment("stopped");
            }

            that.#run = !that.#run;
        });

        controller.pyswitch.setMidiMonitor({
            monitorInput: function(message) {
                that.addMessage({
                    message: message,
                    direction: "in"
                })
            },
            monitorOutput: function(message) {
                that.addMessage({
                    message: message,
                    direction: "out"
                })
            }
        });
    }

    async initMonitor() {
        const clients = await Client.getAvailable();

        for (const client of clients) {
            const virtualClient = await client.getVirtualClient();
            if (!virtualClient) continue;

            this.#virtualClients.push(virtualClient);
        }
    }

    destroy() {
        this.#monitorElement.empty();
    }

    // /**
    //  * Called from python, to monitor an incoming message
    //  */
    // monitorInput(message) {
    //     this.addMessage({
    //         message: message.toJs ? message.toJs() : message,
    //         direction: "in"
    //     })
    // }

    // /**
    //  * Called from python, to monitor an outgoing message
    //  */
    // monitorOutput(message) {
    //     this.addMessage({
    //         message: message.toJs ? message.toJs() : message,
    //         direction: "out"
    //     })
    // }

    /**
     * {
     *      direction: "in" or "out"
     *      message: Data of the MIDI message
     * }
     */
    addMessage(options) {
        if (!this.#run) return;

        if (!options.message) options.message = "NO MESSAGE";

        let tr = null;
        this.#monitorElement.append(
            tr = $('<tr class="midi-message midi-message-' + options.direction + '" />').append(
                $('<td />').append(
                    options.direction
                ),
                $('<td />').append(
                    this.#messageName(options.message)
                ),
                $('<td />').append(
                    this.#formatMidiMessage(options.message)
                )
            )
        )

        tr[0].scrollIntoView(false);

        this.#cleanup();
    }

    /**
     * Add a comment
     */
    addComment(comment) {
        // if (!this.#run) return;

        let tr = null;
        this.#monitorElement.append(
            tr = $('<tr class="comment" />').append(
                $('<td colspan="3"/>').text(comment)
            )
        )

        tr[0].scrollIntoView(false);

        this.#cleanup();
    }

    /**
     * Output formatting for the raw data bytes
     */
    #formatMidiMessage(message) {
        return Array.from(message)
            .map((item) => ("" + item).padStart(3, " "))
            .join(", ")
    }

    /**
     * Tries to determine a readable name for the message
     */
    #messageName(message) {
        // Try all virtual clients
        for (const client of this.#virtualClients) {
            const name = client.getMessageName(message);
            if (!name) continue;

            return name;
        }
    }

    /**
     * Remove old messages
     */
    #cleanup() {
        while (this.#monitorElement.children('tr').length > this.#maxNumMessages) {
            this.#monitorElement.children('tr').first().remove();
        }
    }

    // /**
    //  * Generates custom buttons for the tab, if any
    //  */
    // getButtons() {
    //     const that = this;

    //     return [
    //         this.#applyButton = $('<div class="fas fa-check" data-toggle="tooltip" title="Apply code" />')
    //         .toggleClass("inactive", !this.isDirty())
    //         .on('click', async function() {
    //             try {
    //                 await that.apply();

    //             } catch (e) {
    //                 that.#controller.handle(e);
    //             }
    //         })              
    //     ];
    // }
}