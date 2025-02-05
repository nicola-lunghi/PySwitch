class VirtualKemperClientUI {

    #container = null;
    #client = null;

    constructor(container, client) {
        this.#container = container;
        this.#client = client;

        this.#build();
    }

    #build() {
        this.destroy();

        this.#buildEffectSlots();
    }

    #buildEffectSlots() {
        const that = this;

        // Effect slots
        function createSlot(text, addressPage, addresses) {
            const paramState = that.#client.parameters.get(new NRPNKey([addressPage, addresses.state]));
            const paramType = that.#client.parameters.get(new NRPNKey([addressPage, addresses.type]));

            const inputState = $('<input type="checkbox" autocomplete="off">');
            const inputType = $('<input type="text" autocomplete="off">');

            paramState.addChangeCallback(function(param, value) {
                inputState.prop("checked", value != 0);                
            });

            paramType.addChangeCallback(function(param, value) {
                inputType.val(value);
            });

            return $('<div class="box slot" />').append(
                // Slot title
                $('<div class="title" />')
                .text(text),

                // State
                $('<div class="label" />')
                .text("State"),

                inputState
                .prop('checked', paramState.value != 0)
                .on('change', function() {
                    paramState.setValue(this.checked ? 1 : 0)
                }),

                // Type
                $('<div class="label" />')
                .text("Type"),

                inputType
                .val(paramType.value)
                .on('change', function() {
                    paramType.setValue(parseInt($(this).val()));
                })
            )
        }

        function createBox(title, content) {
            that.#container.append(
                $('<div class="box" />').append(
                    // Box title
                    $('<div class="title" />')
                    .text(title),

                    content
                )
            )
        }

        this.#container.append(createSlot("A",   50, { state: 3, type: 0 }));
        this.#container.append(createSlot("B",   51, { state: 3, type: 0 }));
        this.#container.append(createSlot("C",   52, { state: 3, type: 0 }));
        this.#container.append(createSlot("D",   53, { state: 3, type: 0 }));

        this.#container.append(createSlot("X",   56, { state: 3, type: 0 }));
        this.#container.append(createSlot("MOD", 58, { state: 3, type: 0 }));
        this.#container.append(createSlot("DLY", 60, { state: 3, type: 0 }));
        this.#container.append(createSlot("REV", 61, { state: 3, type: 0 }));

        // Rig ID input
        let rigIdInput = null;
        let tempoInput = null;
        createBox(
            "Rig",
            [
                // Rig ID
                $('<div class="label" />')
                .text("Rig ID"),

                rigIdInput = $('<input type="text" autocomplete="off">')
                .val(that.#client.getRigId())
                .on('change', function() {
                    const rigId = parseInt($(this).val());
                    that.#client.setRigId(rigId);
                }),

                // Tempo (BPM)
                $('<div class="label" />')
                .text("Tempo"),

                tempoInput = $('<input type="text" autocomplete="off">')
                .val(that.#client.tempo.bpm())
                .on('change', function() {
                    const tempo = parseInt($(this).val());
                    that.#client.tempo.set(tempo);
                })
            ]
        );

        function onRigChange(param, value) {
            rigIdInput.val(that.#client.getRigId());
        }

        this.#client.parameters.get(new CCKey(50)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(51)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(52)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(53)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(54)).addChangeCallback(onRigChange);

        this.#client.parameters.get(new CCKey(48)).addChangeCallback(onRigChange);  // Bank up
        this.#client.parameters.get(new CCKey(49)).addChangeCallback(onRigChange);  // Bank down

        this.#client.tempo.addChangeCallback(function(bpm) {
            tempoInput.val(bpm);
        })
    }

    destroy() {
        this.#container.empty();
    }
}