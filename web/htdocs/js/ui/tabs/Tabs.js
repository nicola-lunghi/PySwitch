class Tabs {

    #controller = null;
    #container = null;
    #showTabsButton = null;
    
    #content = null;
    #header = null;
    
    #tabs = [];
    active = null;               // Active Tab instance

    constructor(controller, container, showTabsButton) {
        this.#controller = controller;
        this.#container = container;
        this.#showTabsButton = showTabsButton;

        this.init();
    }

    /**
     * Set up DOM, handlers etc.
     */
    init() {
        // DOM
        this.#container.append(
            this.#header = $('<div class="header" />').append(
                // Show/hide tabs (only visible in mobile mode)
                $('<div class="header-item close-tabs fas fa-times"/>')
                .on('click', async function() {
                    try {
                        that.hide();
                    
                    } catch (e) {
                        that.#controller.handle(e);
                    }
                })
            ),
            this.#content = $('<div class="content" />'),
        )

        // Make tabs resizable (using jquery UI)
        const that = this;
        this.#container.resizable({ 
            handles: "e",
            stop: function() {
                that.#setState('width', that.#container.width());
            }
        });

        // Set state according to local storage (defaults to hidden)
        if (this.#getState('show')) {
            this.show();
        } else {
            this.hide();
        }
    }

    /**
     * Add a new Tab instance
     */
    add(tab) {        
        if (!tab) return;
        
        this.#content.append(tab.container);

        this.#header.append(
            tab.getHeader()
        )

        this.#tabs.push(tab);
        this.#update();
    }

    /**
     * Remove a Tab instance
     */
    remove(tab) {
        if (!tab) return;
        tab.container.remove();
        
        const index = this.#tabs.indexOf(tab);
        if (index > -1) { 
            this.#tabs.splice(index, 1); 
        }
    }

    /**
     * Show tabs
     */
    show() {
        const width = this.#getState('width');
        if (width) {
            this.#container.width(width);
        }

        this.#container.show();
        this.#showTabsButton.hide();

        this.#setState('show', true);
    }

    /**
     * Hide tabs
     */
    hide() {
        this.#container.hide();
        this.#showTabsButton.show();

        this.#setState('show', false);
    }

    /**
     * Is the tabs panel visible?
     */
    visible() {
        return !!this.#container.is(":visible");
    }

    /**
     * Toggle tabs panel visibility
     */
    toggle() {
        if (this.visible()) {
            this.hide();
        } else {
            this.show();
        }
    }

    /**
     * Sets a specific tab active
     */
    setActive(tab) {
        if (this.active) {
            this.active.deactivate();
        }

        this.active = tab;
        this.#updateActive();
    }

    /**
     * Updates the tabs to the current active tab
     */
    #updateActive() {
        for (const tab of this.#tabs) {
            if (tab == this.active) {
                tab.activate();
            } else {
                tab.activate();
            }
        }
    }

    /**
     * Update after tab changes
     */
    #update() {
        if (this.#tabs.length > 0 && !this.active) {
            this.setActive(this.#tabs[0]);
        }
    }

    /**
     * Set value on the tabs state object in local storage
     */
    #setState(name, value) {
        const state = this.#controller.getState('tabs') || {};
        state[name] = value;
        this.#controller.setState('tabs', state);
    }

    /**
     * Get a value from the tabs state object in local storage
     */
    #getState(name) {
        const state = this.#controller.getState('tabs') || {};        
        return state[name]
    }    
}