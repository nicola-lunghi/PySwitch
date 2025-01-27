class PySwitchUI {

    #options = null;
    #pyswitch = null;
    #midiAccess = null;          // MIDIAccess instance
    midiPorts  = null;
    onmidimessage = null;
    messageQueue = [];

    constructor(options) {
        this.#options = options;
        this.#pyswitch = new PySwitchRunner(options);
    }

    async run() {
        await this.#initMidi();

        this.#setupPortSelector();

        await this.#pyswitch.init();
        await this.#pyswitch.run(this);
    }
  
    /**
     * Sets up MIDI communication
     */
    async #initMidi() {
        const that = this

        return new Promise(function(resolve, reject) {
            async function onMIDISuccess(midiAccess) {
                if (!midiAccess.sysexEnabled) {
                    reject({ message: "You must allow SystemExclusive messages" });
                }

                // Use a handler class for accessing the bridge and creating the connection
                that.#midiAccess = midiAccess;

                resolve();
            }

            async function onMIDIFailure(msg) {
                reject({ message: "Failed to get MIDI access: " + msg });
            }

            navigator.requestMIDIAccess({ sysex: true })
                .then(onMIDISuccess, onMIDIFailure);
        });
    }

    async send(message) {
        if (!this.midiPorts) {
            console.warn("Cannot send MIDI message, please select a port");
            //message.destroy();
            return;
        }
        //console.log("Send", message.toJs())
        await this.midiPorts.output.send(message.toJs());        
    }

    async receive(msg) {
        //console.log("Receive", msg)
        this.messageQueue.push(msg);
    }

    /**
     * Gets a port list, which is an array of objects like:
     * {
     *     input:
     *     output:
     * }
     */
    #getMatchingPortPairs() {
        const ret = [];

        // Inputs
        for (const input of this.#midiAccess.inputs) {
            const in_handler = input[1];

            // Get corresponding output
            for (const output of this.#midiAccess.outputs) {
                const out_handler = output[1];

                if ((out_handler.manufacturer == in_handler.manufacturer) && (out_handler.name == in_handler.name)) {
                    //this.console.log("Scan: Found matching ins/outs: " + out_handler.name);
                    ret.push({
                        name: out_handler.name,
                        input: in_handler,
                        output: out_handler
                    });
                }
            }
        }

        return ret;
    } 

    #setupPortSelector() {
        const ports = this.#getMatchingPortPairs();

        const settings = document.getElementById("settings");
        
        const sel = document.createElement("select");        
        settings.appendChild(sel);

        const option = document.createElement("option");
        option.value = "Not connected";
        option.innerHTML = "Not connected";
        sel.appendChild(option);

        for (const port of ports) {
            const option = document.createElement("option");
            option.value = port.name;
            option.innerHTML = port.name;
            sel.appendChild(option);
        }

        const that = this;
        sel.addEventListener("change", async function(e) {
            console.log("Selected " + sel.value);
            
            for (const port of ports) {
                if (port.name != sel.value) continue;

                if (that.midiPorts) {
                    that.midiPorts.input.onmidimessage = null;
                }
                that.midiPorts = port;

                port.input.onmidimessage = async function(event) {
                    await that.receive(event.data);                    
                }

                return;
            }
        });
    }
}