/**
 * Note taking app - Main application controller class.  
 * 
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

/**
 * Messages to the user
 */
class Notifications {
	
	#messageElement = null;
	
	constructor(messageElement) {
		this.#messageElement = messageElement;
	}
	
	build() {
		this.#messageElement.append(            
			$('<table />').append(
				$('<tbody />').append(
                    this.#messageElement
                )
            )
    	);
	}

	reset() {
		this.#messageElement.empty();
	}

	/**
	 * Show a message to the user. Default type is "E" for error, other supported types are I(nfo), W(arning), and S(uccess).
	 * 
	 * options = {
	 *    alwaysHideAtNewMessage: false,     <- alwaysHideAtNewMessage can be used if you like to have the message disappearing whenever a new one comes in.
	 *    callback: false                    <- callbackFunction is executed on clicking the message.
	 * }
	 */
	message(msgOrException, type, options) {
		if (!options) {
			options = {
				alwaysHideAtNewMessage: false, 
				callback: false
			}
		}
		
		if (!type) type = 'E';
		
		let msg = "";
		if (msgOrException instanceof Error) {
			msg = msgOrException.message;
		} else {
			msg = msgOrException;
		}
		
		const msgEl = $('<div />');
		const msgCont = $('<tr />').append($('<td />').append(msgEl));
		let fadeTime = 0;
		
		const errorFadeTimeMs = 0; //12000;
		const infoFadeTimeMs = 3000;

		switch (type) {
		case 'E':
			msgEl.addClass("message message-danger");
			console.log(msg)
			if (typeof msg == "string" && msg.includes("Traceback")) {
				msgEl.addClass("message-traceback")
				msg += "\n\n" + 'Please check if your PySwitch version matches ' + Controller.PYSWITCH_VERSION + '. If not, use the correct <a href="https://pyswitch.tunetown.de/versions" target="_blank">emulator version</a> for your controller.';
			}

			fadeTime = errorFadeTimeMs;   
			console.error(msgOrException);
			break;
		case 'W':
			msgEl.addClass("message message-warning");
			fadeTime = errorFadeTimeMs;
			console.warn(msgOrException);
			break;
		case 'S':
			msgEl.addClass("message message-success");
			fadeTime = infoFadeTimeMs;		
			console.info(msgOrException);	
			break;
		case 'I':
			msgEl.addClass("message message-info");
			fadeTime = infoFadeTimeMs;
			console.info(msgOrException);
			break;
		default:
			msgEl.addClass("message message-danger");
			fadeTime = errorFadeTimeMs; 
			console.error(msgOrException);
			break;
		}

		msgEl.html(msg);

		// Click to remove
		msgEl.click(function(event) {
			//event.stpPropagation(); 
			msgCont.remove();
			
			if (options.callback) {
				options.callback(msgCont, event);
			}
		});	

		// Add message at the top
		this.#messageElement.prepend(msgCont);

		// Fade out after a certain time
		if (fadeTime > 0) { 
			msgCont.msgTimeoutHandle = setTimeout(function() {
				if (msgCont && msgCont.fadeOut) msgCont.fadeOut();
			}, fadeTime);
		}
		
		// // Hide messages of the same thread
		// if (options.threadID) {
		// 	this.#messageElement.children().each(function(/*el*/) {
		// 		const tid = $(this).data("threadID");
		// 		if (tid == options.threadID) {
		// 			$(this).remove();
		// 		}
		// 	});
			
		// 	msgCont.data("threadID", options.threadID);
		// }
		
		// Hide messages which are not important
		this.#messageElement.children().each(function(/*el*/) {
			const flag = $(this).data("alwaysHideAtNewMessage");
			if (flag) {
				$(this).remove();
			}
		});
		
		if (options.alwaysHideAtNewMessage) {
			msgCont.data("alwaysHideAtNewMessage", true);
		}
	}
}