class PySwitchUI {

    #controller = null;

    constructor(controller) {
        this.#controller = controller;
    }

    async init() {
        this.#setupPortSelector();
    }

    #setupPortSelector() {
        const ports = this.#controller.getMatchingPortPairs();
        const settings = document.getElementById("settings");
        
        const sel = document.createElement("select");        
        settings.appendChild(sel);

        const prefix = "Client Device: ";
        const option = document.createElement("option");
        option.value = "None";
        option.innerHTML = prefix + "None";
        sel.appendChild(option);

        for (const port of ports) {
            const option = document.createElement("option");
            option.value = port.name;
            option.innerHTML = prefix + port.name;
            sel.appendChild(option);
        }

        const that = this;
        sel.addEventListener("change", async function(e) {
            for (const port of ports) {
                if (port.name != sel.value) continue;

                that.#controller.pyswitch.setMidiWrapper(                    
                    new WebMidiWrapper(port.input, port.output)
                );

                console.log("Connected to " + port.name);
            
            return;
            }
        });
    }
}