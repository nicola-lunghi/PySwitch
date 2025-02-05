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
        function createSlot(text, addressPage, addresses) {
            return $('<div class="slot" />').append(
                // Slot title
                $('<div class="title" />')
                .text(text),

                // State
                $('<div class="label" />')
                .text("State"),

                $('<input type="checkbox">')
                .attr('checked', that.#client.parameters.value([addressPage, addresses.state] != 0))
                .on('change', function() {
                    that.#client.parameters.set([addressPage, addresses.state], this.checked ? 1 : 0)
                }),

                // Type
                $('<div class="label" />')
                .text("Type"),

                $('<input type="text">')
                .val(that.#client.parameters.value([addressPage, addresses.type]))
                .on('change', function() {
                    that.#client.parameters.set([addressPage, addresses.type], parseInt($(this).val()));
                })
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
    }

    destroy() {
        this.#container.empty();
    }
}