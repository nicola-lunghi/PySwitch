/**
 * Manages local storage content
 */
class LocalState {

    #storageId = null;
    #stateObjectId = null;

    /**
     * storageId is the ID of the local storage cookie.
     * stateObjectId is the sub-object name.
     */
    constructor(storageId, stateObjectId) {
        this.#stateObjectId = stateObjectId;
        this.#storageId = storageId;
    }

    /**
     * Set a variable in local storage
     */
    set(key, value) {
        const data = JSON.parse(localStorage.getItem(this.#storageId) || "{}");
        
        if (!data.hasOwnProperty(this.#stateObjectId)) data[this.#stateObjectId] = {};
        data[this.#stateObjectId][key] = value;
        
        localStorage.setItem(this.#storageId, JSON.stringify(data));
    }

    /**
     * Read local storage
     */
    get(key) {
        const data = JSON.parse(localStorage.getItem(this.#storageId) || "{}");

        if (!data.hasOwnProperty(this.#stateObjectId) || 
            !data[this.#stateObjectId].hasOwnProperty(key)) return null;

        return data[this.#stateObjectId][key];
    }
}