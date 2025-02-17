/**
 * (C) Thomas Weber 2024 tom-vibrant@gmx.de
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>. 
 */
class Routing {

    #queue = null;
    #controller = null;

    constructor(controller) {
        this.#queue = new CallbackQueue();
        this.#controller = controller;

        this.#setup();
    }

    /**
	 * Set up routing
	 */
    #setup() {
        const that = this;
        
        // Initialze sammy.js routing. Here, all routes are defined:
        this.sammy = $.sammy('body', function() {

            // Scan routes
            this.get("#", that.#queue.add(that.#executeRoute(async function() {
                await that.#controller.scanControllers();
            })));

            this.get("#/", that.#queue.add(that.#executeRoute(async function() {
                await that.#controller.scanControllers();
            })));

            // Load controller config
            this.get(/\#controller\/(.*)/, that.#queue.add(that.#executeRoute(async function() {
                const portName = decodeURI(this.params['splat'][0]);
                
                if (portName != "pyswitch-default") {
                    await that.#controller.loadConfiguration(
                        new ControllerConfiguration(that.#controller, portName)
                    );
                } else {
                    await that.#controller.loadConfiguration(
                        new WebConfiguration("circuitpy", "PySwitch Default")
                    );
                }
            })));

            // Load/browse example configs
            this.get(/\#example\/(.*)/, that.#queue.add(that.#executeRoute(async function() {
                const path = decodeURI(this.params['splat'][0]);                    
                await that.#controller.loadConfiguration(
                    new WebConfiguration("examples/" + encodeURI(path))
                );
            })));

            // Load/browse template configs
            this.get(/\#template\/(.*)/, that.#queue.add(that.#executeRoute(async function() {
                const path = decodeURI(this.params['splat'][0]);                    
                await that.#controller.loadConfiguration(
                    new WebConfiguration("templates/" + encodeURI(path))
                );
            })));
        });

        // Error handling
        this.sammy.error = function(e) {
            that.#controller.handle(e);
        }
    }

    /**
     * Returns a wrapped routing callback including error handling etc. Every route goes through this.
     */
    #executeRoute(callback) {
        const that = this;

        return async function() {
            try {
                await that.#controller.ui.reset();

                await callback.bind(this)();

            } catch (e) {
                that.#controller.handle(e);
            }
        }
    }
    
    /**
	 * Start routing
	 */
	run() {
		this.sammy.run('#/');
	}
	
	/**
	 * Refresh
	 */
	refresh() {
		this.sammy.refresh();
	}

    /**
     * Redirect to home (root).
     */
    home() {
        location.href = location.protocol +'//'+ location.host + (location.pathname ? location.pathname : '');
    }

    /**
     * Calls the passed uri path
     */
    call(path) {
        location.href = location.protocol +'//'+ location.host + (location.pathname ? location.pathname : '') + '#' + encodeURI(path);
    }
}