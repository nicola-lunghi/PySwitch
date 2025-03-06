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
        const page = actionCallProxy.page()
        console.log(page)
    }
}