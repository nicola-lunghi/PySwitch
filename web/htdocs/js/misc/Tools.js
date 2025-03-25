class Tools {

    /**
     * Fetch text from an url, throwing if the response is not OK.
     */
    static async fetch(url) {
        const resp = await fetch(url);
        if (!resp.ok) {
            throw new Error("Error fetching " + decodeURI(url));
        }
        return resp.text();
    }

    /**
     * https://stackoverflow.com/questions/105034/how-do-i-create-a-guid-uuid
     */
    static uuid() {
        return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
            (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
        );
    }

    /**
	 * Shallow compare two arrays (i know, could be done more js-like but works)
	 */
	static compareArrays(a, b) {
		if (a.length != b.length) {
			return false;
		}
		 
		for (let i = 0; i < a.length; ++i) {
			if (a[i] != b[i]) {
				return false;
			} 
		}
		
		return true;
	}

    /**
     * Returns an array with [r, g, b] 8 bit values from a hex color string
     */
    static hexToRgb(color) {
        if (!color.startsWith("#")) return color;
        
        const r = parseInt(color.substr(1,2), 16)
        const g = parseInt(color.substr(3,2), 16)
        const b = parseInt(color.substr(5,2), 16)
        
        return [r, g, b];
    }

    /**
     * Convert a RGB color string to hex
     */
    static rgbToHex(rgb) {
        function componentToHex(c) {
            var hex = c.toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        }
            
        const comps = rgb.replace("(", "").replace(")", "").replace("rgba", "").replace("rgb", "").split(",");
        
        const r = parseInt(comps[0]);
        const g = parseInt(comps[1]);
        const b = parseInt(comps[2]);

        return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
    }

    /**
     * Remove all existing quotes and add new ones.
     */
    static autoQuote(str) {
        return "'" + Tools.stripQuotes(str) + "'";
    }

    /**
     * Removes all kinds of quotes
     */
    static stripQuotes(str) {
        return str.replaceAll('"', "").replaceAll("'", "");
    }

    /**
     * Returns the passed element with the passed comment on hover
     */
    static withComment(el, comment) {
        if (comment) {
            tippy(el[0], {
                content: comment,
                theme: "pyswitchtooltip",
                placement: "top-end",
                arrow: false,
                duration: 0
            });
        }

        return el;
    }
}