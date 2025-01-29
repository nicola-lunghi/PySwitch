/**
 * (C) Thomas Weber 2021 tom-vibrant@gmx.de
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
class CallbackQueue {  

	#queue = [];         // Queue of callback functions
	#running = false;    // Is there a callback currently running?

	/**
	 * Queues the callback until all ealier callbacks have been finished. Returns a new
	 * callback function to be called instead of the passed one (no arguments).
	 */
	add(callback) {
		const that = this;
		
		return async function() {
			// Add callback to the queue
			that.#enqueue(callback, this);

			// Trigger queue to execute the next callback if not running
			that.#trigger();
		}
	}
	
	/**
	 * Add callback to the queue
	 */
	#enqueue(callback, context) {
		const that = this;
		
		this.#queue.push({
			callback: async function(context) {
				that.#running = true;
				await callback.call(context);
				that.#running = false;
				
				that.#trigger();
			},
			context: context
		});
	}
	
	/**
	 * Trigger queue to execute the next callback if not running
	 */
	#trigger() {
		if (this.#running) return;
		if (this.#queue.length == 0) return;
		
		const next = this.#queue.shift();
		if (!next) return;
		
		// This is called without await on purpose: This function should only trigger but not block! 
		next.callback(next.context);
	}
}