class ResizeHandler {

    #resizeObserver = null;
    #doUpdateSize = false;    // Flag to update the width on next mouse up event

    constructor(element) {
        this.#setupResizeObserver(element);
    }

    /**
	 * Sets up the resize observer
	 */
	#setupResizeObserver(element) {
		const that = this;
		this.#resizeObserver = new ResizeObserver(function(/*entries*/) {
			// Tell the mouseup handler to update width next time
			that.#doUpdateSize = true;
		});
		
		// Set the new width on mouse up
		$(window).on('mouseup', function() {
			if (!that.#doUpdateSize) return;
			
            const height = element.height();
            console.log(height)

			that.#doUpdateSize = false;				
		});
		
		this.#resizeObserver.observe(element[0]);
	}
}