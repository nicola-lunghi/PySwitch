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
	 * Compare two arrays (i know, could be done more js-like but works)
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
}