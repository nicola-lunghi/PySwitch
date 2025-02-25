/**
 * Implements tabs handling
 */
class Tabs {

    #controller = null;
    #container = null;
    #showTabsButton = null;
    
    #content = null;
    #header = null;
    #headerButtons = null;
    
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
            $('<div class="header" />').append(
                // Header (tab headers)
                this.#header = $('<div class="header-tabs" />'),

                // Header buttons
                $('<div class="header-buttons" />').append(
                    // Tab specific buttons
                    this.#headerButtons = $('<span />'),

                    $('<span />').append(
                        // Show/hide tabs button
                        $('<div class="close-tabs fas fa-times"/>')
                        .on('click', async function() {
                            try {
                                that.hide();
                            
                            } catch (e) {
                                that.#controller.handle(e);
                            }
                        })
                    )
                )
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
    add(tab, index = null) {          // TODO
        if (!tab) return;
        
        tab.init(this);
        
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
        if (!tab.confirmIfDirty()) return;

        tab.destroy();

        if (tab == self.active) self.active = null;
        
        const index = this.#tabs.indexOf(tab);
        if (index > -1) { 
            this.#tabs.splice(index, 1); 
        }

        this.#update();
    }

    /**
     * Get a tab by name, or null if not found
     */
    getTabByName(name) {
        for (const tab of this.#tabs) {
            if (tab.name == name) return tab;
        }
        return null;
    }

    confirmIfDirty() {
        for (const tab of this.#tabs) {
            if (!tab.confirmIfDirty()) return false;
        }
        return true;
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
        
        // When a tab is shown, the editors need refreshing
        if (this.active) {
            this.active.refresh();
        }
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
        if (!tab) throw new Error('No tab passed');

        this.active = tab;
        this.#updateActive();

        this.#setState('current', tab.name);

        // When a tab is shown, the editors need refreshing
        this.active.refresh();

        // Replace buttons
        this.#headerButtons.empty();
        this.#headerButtons.append(
            this.active.getButtons()
        )
    }

    /**
     * Updates the tabs to the current active tab
     */
    #updateActive() {
        for (const tab of this.#tabs) {
            if (tab == this.active) {
                tab.activate();
            } else {
                tab.deactivate();
            }
        }
    }

    /**
     * Update after tab changes
     */
    #update() {
        if (this.#tabs.length > 0 && !this.active) {
            const current = this.#getState('current');
            if (current) {
                const tab = this.getTabByName(current);

                if (tab) {
                    this.setActive(tab);
                    return;
                }

            } else {
                this.setActive(this.#tabs[0]);
                return;
            }            
        }

        this.#updateActive();        
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