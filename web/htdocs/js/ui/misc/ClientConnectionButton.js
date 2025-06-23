/**
 * Button showing client connection state
 */
class ClientConnectionButton {

    #element = null;
    #controller = null;
    #icon = null;

    #lastState = null;

    static STATE_NOT_CONNECTED = 10;
    static STATE_WAITING = 20;
    static STATE_CONNECTED = 100;

    constructor(controller, element) {
        this.#controller = controller;
        this.#element = element;

        this.#build();

        this.#setState(ClientConnectionButton.STATE_NOT_CONNECTED);
    }

    #build() {
        const that = this;

        this.#element.append(
            this.#icon = $('<div />')
        )
        .on("click", async function() {
            try {
                await that.#controller.ui.clientBrowser.browse();
                that.#controller.ui.clientBrowser.setSelectedValue(that.#controller.client.state.get("selectedClient"));
                that.#controller.ui.clientBrowser.showInfoPanel("This selects a device like a Kemper Profiler connected to the Computer via USB, to be controlled by the emulator. <br><br>To load/save configurations from/to your MIDI Controller, use the Load/Save buttons on the top of the screen.")

            } catch (e) {
                that.#controller.handle(e);
            }
        });

        // Schedule updates every 200ms
        setInterval(function() {
            that.#updateState();
        }, 200);
    }

    /**
     * Update button state
     */
    #updateState() {
        this.#setState(this.#getCurrentState());
    }

    /**
     * Determines the state to show currently
     */
    #getCurrentState() {
        if (!this.#controller.pyswitch.hasMidiWrapper()) return ClientConnectionButton.STATE_NOT_CONNECTED;

        if (this.#controller.pyswitch.getProtocolState() == -10) return ClientConnectionButton.STATE_CONNECTED;  // No protocol
        if (this.#controller.pyswitch.getProtocolState() == 20) return ClientConnectionButton.STATE_CONNECTED;   // Connected

        return ClientConnectionButton.STATE_WAITING;
    }

    /**
     * Set the button state
     */
    #setState(state) {
        if (state == this.#lastState) return;
        this.#lastState = state;

        this.#icon[0].className = "";
        this.#element[0].className = "client-select";
        this.#element.attr("title", "");

        switch(state) {
            case ClientConnectionButton.STATE_NOT_CONNECTED:
                this.#icon.addClass("fa fa-times");                
                this.#element.addClass("not-connected");
                this.#element.attr("title", "Not connected to any client device to control");
                break;
            
            case ClientConnectionButton.STATE_WAITING:
                this.#icon.addClass("fa fa-hourglass-half");                
                this.#element.addClass("waiting");
                this.#element.attr("title", "Connected MIDI to the client, waiting for the protocol to connect...");
                break;

            case ClientConnectionButton.STATE_CONNECTED:
                this.#icon.addClass("fa fa-check");                
                this.#element.addClass("connected");
                this.#element.attr("title", "Connected to client");
                break;
        }
    }
}