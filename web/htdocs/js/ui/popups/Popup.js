/**
 * Generic popup
 */
class Popup {

    element = null;        // Content element
    #container = null;  
    config = null;

    #id = null;            // Only used for handlers

    /**
     * config: {
     *      container:                Container DOM element
     *      additionalClasses:        Optional CSS classes for the popup element
     *      onReturnKey:              Callback when the user hits the Return key
     *      onClose:                  Called on hide
     * }
     */
    constructor(config) {
        this.config = config || {};

        this.#id = Tools.uuid();
    }

    /**
     * Hide: Remove all closing event handlers
     */
    hide() {
        if (this.#container) {
            this.#container.remove();
        }        

        this.#container = null;
        this.element = null;

        $(window).off('.' + this.#id);
    }

    /**
     * Show the browser: Also adds some event handlers to close it on ESC and clicking outside
     */
    show(content, headline = null) {
        this.hide();

        this.config.container.append(
            this.#container = $('<div class="list-block" />').append(
                this.element = $('<div class="list-browser"/>')
                    .toggleClass("wide", !!this.config.wide)
                    .toggleClass("fullscreen", !!this.config.fullscreen)                    
                    .append(
                        $('<div class="content" />').append(
                            // Headline
                            !headline ? null :
                            $('<div class="headline"/>')
                            .text(headline),
            
                            // Content
                            content,
                            
                            // Close button
                            $('<span class="fa fa-times close-button"/>')
                            .on('click', async function() {
                                if (that.config.onClose) {
                                    await that.config.onClose();
                                }
                        
                                that.hide();
                            })
                        )
                    )
            )
        );

        if (this.config.additionalClasses) {
            this.element.addClass(this.config.additionalClasses);
        }

        // ESC to close
        const that = this;
        $(window).on('keydown.' + this.#id, async function(event) {
            if (event.key === "Escape") {
                event.preventDefault();
                that.hide();
            }
            
            if (event.key === "Enter") {
                if (that.config.onReturnKey) {
                    await that.config.onReturnKey();
                }
            }
        });

        this.element.on('click.' + this.#id, function(event) {
            event.stopPropagation();
        })

        setTimeout(function() {
            $(window).on('click.' + that.#id, async function() {
                that.hide();
            });    
        }, 0)
    }
}