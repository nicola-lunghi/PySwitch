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
            //console.log("Selected " + sel.value);
            
            for (const port of ports) {
                if (port.name != sel.value) continue;

                that.#controller.pyswitch.setMidiWrapper(                    
                    new WebMidiWrapper(port.input, port.output)
                );

                return;
            }
        });
    }
}