/**
 * Generates the icons for actions in the parser frontend.
 */
class ParserFrontendIcons {
 
    #pageColors = null;

    constructor() {
        this.#pageColors = new Map();
    }

    /**
     * Returns icon DOM for the passed action proxy
     */
    get(actionCallProxy) {
        const icons = [];

        // Page icon
        const page = actionCallProxy.page()
        if (page) {
            icons.push(
                $('<span />')
                .addClass('icon-page')
            )
        }
        

        return $('<span class="action-icons" />').append(icons)
    }
}