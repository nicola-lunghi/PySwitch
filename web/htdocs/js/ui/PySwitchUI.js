class PySwitchUI {

    #controller = null;

    constructor(controller) {
        this.#controller = controller;
    }

    async init() {
        const settings = document.getElementById("settings");

        this.#setupPortSelector(settings);
        this.#setupVersionDisplay(settings)
    }

    #setupPortSelector(settings) {
        const ports = this.#controller.bridge.getMatchingPortPairs();
        
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

    #setupVersionDisplay(settings) {
        const el = document.createElement("option");
        el.innerHTML = "PySwitchUI v" + this.#controller.VERSION;
        settings.appendChild(el);
    }
}