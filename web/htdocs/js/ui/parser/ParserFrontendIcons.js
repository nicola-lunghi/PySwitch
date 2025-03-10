/**
 * Generates the icons for actions in the parser frontend.
 */
class ParserFrontendIcons {
 
    #pageColors = null;
    #nextPageColorId = 0;

    constructor() {
        this.#pageColors = new Map();
    }

    /**
     * Returns icon DOM for the passed action proxy
     */
    async get(actionCallProxy, actionDefinition) {
        const icons = [];
        
        // Action using LEDs?        
        if (this.#usesLeds(actionCallProxy, actionDefinition)) {
            icons.push(
                $('<span data-toggle="tooltip" title="This action uses the switch LEDs" />')
                .addClass('fas fa-lightbulb action-icon icon-uses-leds')
            )
        }

        // Display assignment
        const display = actionCallProxy.argument('display');
        if (display && (display != 'None')) {
            icons.push(
                $('<span data-toggle="tooltip" title="This action is assigned to display ' + display + '" />')
                .addClass('fas fa-tv action-icon icon-has-display')
            )
        }

        // Page icon if involved in paging, if not: enable callback
        const page = actionCallProxy.page()
        const ec = actionCallProxy.argument('enable_callback');
        if (page) {            
            icons.push(
                $('<span data-toggle="tooltip" title="This action is part of page ' + page + '" />')
                .addClass('action-icon icon-page icon-page-' + this.#getPageColorId(page))
            )
        } else if (ec && (ec != 'None')) {
            icons.push(
                $('<span data-toggle="tooltip" title="This action has an Enable Callback not involved in a PagerAction" />')
                .addClass('fas fa-chevron-circle-right action-icon icon-enable-callback')
            )
        }

        // Deferred definitions
        if (actionCallProxy.assign) {
            icons.push(
                $('<span data-toggle="tooltip" title="This action is defined globally in an Assign statement" />')
                .addClass('fas fa-arrow-right action-icon icon-assign')
            )
        }

        return $('<span class="action-icons" />').append(icons)
    }

    /**
     * Returns a numeric color ID
     */
    #getPageColorId(page) {
        if (this.#pageColors.has(page)) return this.#pageColors.get(page);

        this.#pageColors.set(page, this.#nextPageColorId++);

        if (this.#nextPageColorId >= 5) {
            this.#nextPageColorId = 0;
        }

        return this.#pageColors.get(page);
    }

    /**
     * Does the action use LEDs?
     */
    #usesLeds(actionCallProxy, actionDefinition) {
        const useLedsVal = actionCallProxy.argument('use_leds');
        if (useLedsVal) {
            // Argument exists
            return useLedsVal == 'True';
        }
        
        if (!actionDefinition) {
            // No definition: No icon
            return false;
        }

        // Use default
        return this.#getParameterDefault(actionDefinition, 'use_leds') == 'True';
    }

    /**
     * Get the default value
     */
    #getParameterDefault(actionDefinition, name) {        
        for (const param of actionDefinition.parameters) {
            if (param.name == name) return param.meta.getDefaultValue();
        }
    }
}