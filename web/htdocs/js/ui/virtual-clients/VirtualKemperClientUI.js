class VirtualKemperClientUI {

    #container = null;
    #client = null;

    constructor(container, client) {
        this.#container = container;
        this.#client = client;

        this.#build();
    }

    #build() {
        this.#container.empty();

        this.#buildEffectSlots();
        this.#buildRig();
        this.#buildTuner();

        // Use a callback to show auto generated parameters
        const that = this;
        this.#client.parameters.addInitCallback(async function(param) {
            that.#addGeneratedParameter(param);
        });
    }

    #buildEffectSlots() {
        const that = this;

        // Effect slots
        function createSlot(text, addressPage, addresses) {
            const paramState = that.#client.parameters.get(new NRPNKey([addressPage, addresses.state]));
            const paramType = that.#client.parameters.get(new NRPNKey([addressPage, addresses.type]));

            const inputState = $('<input type="checkbox" autocomplete="off">');
            const inputType = $('<input type="text" autocomplete="off">');

            paramState.addChangeCallback(async function(param, value) {
                inputState.prop("checked", value != 0);                
            });

            paramType.addChangeCallback(async function(param, value) {
                inputType.val(value);
            });

            that.#createBox(
                text,
                [
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
                ]
            )
            .addClass("slot");
        }

        this.#container.append(createSlot("A",   50, { state: 3, type: 0 }));
        this.#container.append(createSlot("B",   51, { state: 3, type: 0 }));
        this.#container.append(createSlot("C",   52, { state: 3, type: 0 }));
        this.#container.append(createSlot("D",   53, { state: 3, type: 0 }));

        this.#container.append(createSlot("X",   56, { state: 3, type: 0 }));
        this.#container.append(createSlot("MOD", 58, { state: 3, type: 0 }));
        this.#container.append(createSlot("DLY", 60, { state: 3, type: 0 }));
        this.#container.append(createSlot("REV", 61, { state: 3, type: 0 }));
    }

    /**
     * Build rig controls
     */
    #buildRig() {
        const that = this;

        // Rig ID input
        let rigIdInput = null;
        let tempoInput = null;
        let morphInput = null;
        let rigBtnMorhInput = null;

        this.#createBox(
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
                    that.#client.tempo.set(tempo ? tempo : null);
                }),

                // Morph state
                $('<div class="label" />')
                .text("Morph"),

                morphInput = $('<input type="range" min="0" max="16383">')
                .val(that.#client.parameters.get(new NRPNKey([0, 11])).value)
                .on('input', function() {
                    const value = parseInt($(this).val());
                    that.#client.parameters.get(new NRPNKey([0, 11])).setValue(value);
                }),

                // Rig Btn Morph
                $('<div class="label" />')
                .text("Rig Btn Morph"),

                rigBtnMorhInput = $('<input type="checkbox" autocomplete="off">')
                .prop("checked", that.#client.morph.rigBtnMorh)
                .on('change', function() {
                    that.#client.morph.rigBtnMorph = this.checked;
                })
            ]
        );

        // Rig select
        async function onRigChange(param, value) {
            rigIdInput.val(that.#client.getRigId());
        }

        this.#client.parameters.get(new CCKey(50)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(51)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(52)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(53)).addChangeCallback(onRigChange);
        this.#client.parameters.get(new CCKey(54)).addChangeCallback(onRigChange);

        // Bank change
        this.#client.parameters.get(new CCKey(48)).addChangeCallback(onRigChange);  // Bank up
        this.#client.parameters.get(new CCKey(49)).addChangeCallback(onRigChange);  // Bank down

        // Tempo
        this.#client.tempo.addChangeCallback(async function(bpm) {
            tempoInput.val(bpm);
        });

        // Morph state
        this.#client.parameters.get(new NRPNKey([0, 11])).addChangeCallback(async function(param, value) {
            morphInput.val(value);
        });
    }

    /**
     * BUild the tuner controls
     */
    #buildTuner() {
        const that = this;

        // Rig ID input
        let noteInput = null;
        let devianceInput = null;
        let enableInput = null;

        // Contains alternatives. The first row is used for output.
        const notes = [
            ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
            ['C', 'C#', 'D', 'D#', 'Fb', 'E#', 'F#', 'G', 'G#', 'A', 'A#', 'H']
        ]
        
        function detectNote(text) {
            if (parseInt(text)) return parseInt(text);

            text = text.toUpperCase();

            for (const n of notes) {
                const ind = n.indexOf(text);
                if (ind >= 0) {
                    return ind;
                }                
            }
            return 0;
        }

        this.#createBox(
            "Tuner",
            [
                // Enable
                $('<div class="label" />')
                .text("Enable"),

                enableInput = $('<input type="checkbox" autocomplete="off">')
                .prop('checked', that.#client.parameters.get(new NRPNKey([127, 126])).value == 1)
                .on('change', function() {
                    that.#client.parameters.get(new NRPNKey([127, 126])).setValue(this.checked ? 1 : 3)
                }),

                // Note
                $('<div class="label" />')
                .text("Note"),

                noteInput = $('<input type="text" autocomplete="off">')
                .val(notes[0][this.#client.parameters.get(new NRPNKey([127, 126])).value % 12])
                .on('change', function() {
                    const value = $(this).val();
                    const noteCode = detectNote(value);
                    that.#client.parameters.get(new NRPNKey([125, 84])).setValue(noteCode);
                }),

                // Deviance
                $('<div class="label" />')
                .text("Deviance"),

                devianceInput = $('<input type="range" min="0" max="16383">')
                .val(that.#client.parameters.get(new NRPNKey([124, 15])).value)
                .on('input', function() {
                    const value = parseInt($(this).val());
                    that.#client.parameters.get(new NRPNKey([124, 15])).setValue(value);
                })
            ]
        );

        // Tuner mode
        this.#client.parameters.get(new NRPNKey([127, 126])).addChangeCallback(async function(param, value) {            
            enableInput.prop('checked', (value == 1));
        });
        
        // Tuner note
        this.#client.parameters.get(new NRPNKey([125, 84])).addChangeCallback(async function(param, value) {            
            noteInput.val(notes[0][value % 12]);
        });

        // Tuner deviance
        this.#client.parameters.get(new NRPNKey([124, 15])).addChangeCallback(async function(param, value) {            
            devianceInput.val(value);
        });
    }

    /**
     * Adds an auto generated parameter
     */
    #addGeneratedParameter(param) {
        let valueInput = null;

        this.#createBox(
            param.getDisplayName(),
            [
                // Value
                $('<div class="label" />')
                .text("Value"),

                valueInput = $('<input type="text" autocomplete="off">')
                .val(param.value)
                .on('change', function() {
                    const value = $(this).val();

                    switch (param.valueType) {
                        case "number":
                            param.setValue(parseInt(value));
                            break;
                        case "string":
                            param.setValue(value);
                            break;

                        default:
                            throw new Error("Invalid value type: " + param.valueType);
                    }
                })
            ]
        );

        param.addChangeCallback(async function(param, value) {          
            valueInput.val(value);
        });
    }

    /**
     * Used by all parts to create their boxes.
     */
    #createBox(title, content) {
        const box = $('<div class="box" />').append(
            // Box title
            $('<div class="title" />')
            .text(title),

            content
        )
        this.#container.append(box);
        return box;
    }

    /**
     * Destroy the UI
     */
    destroy() {
        this.#container.empty();
    }
}