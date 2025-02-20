class Tabs {

    #controller = null;
    #container = null;
    #showTabsButton = null;

    constructor(controller, container, showTabsButton) {
        this.#controller = controller;
        this.#container = container;
        this.#showTabsButton = showTabsButton;

        // Make tabs resizable (using jquery UI)
        const that = this;
        this.#container.resizable({ 
            handles: "e",
            stop: function() {
                that.#setState('width', that.#container.width());
            }
        });

        if (this.#getState('show')) {
            this.show();
        } else {
            this.hide();
        }
    }

    show() {
        const width = this.#getState('width');
        if (width) {
            this.#container.width(width);
        }

        this.#container.show();
        this.#showTabsButton.hide();

        this.#setState('show', true);
    }

    hide() {
        this.#container.hide();
        this.#showTabsButton.show();

        this.#setState('show', false);
    }

    visible() {
        return !!this.#container.is(":visible");
    }

    toggle() {
        if (this.visible()) {
            this.hide();
        } else {
            this.show();
        }
    }

    #setState(name, value) {
        const state = this.#controller.getState('tabs') || {};
        state[name] = value;
        this.#controller.setState('tabs', state);
    }

    #getState(name) {
        const state = this.#controller.getState('tabs') || {};        
        return state[name]
    }    
}