class Tools {

    /**
     * Fetch text from an url, throwing if the response is not OK.
     */
    static async fetch(url) {
        const resp = await fetch(url);
        if (!resp.ok) {
            throw new Error("Error fetching " + url);
        }
        return resp.text();
    }
}