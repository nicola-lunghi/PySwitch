/**
 * Manages local storage content
 */
class LocalState {

    #storageId = null;
    #subObjectId = null;

    /**
     * storageId is the ID of the local storage cookie.
     * stateObjectId is the sub-object name. If not set, the keys will be placed in the root object.
     */
    constructor(storageId, subObjectId = null) {
        this.#storageId = storageId;
        this.#subObjectId = subObjectId;
    }

    /**
     * Set a variable in local storage
     */
    set(key, value) {
        const data = JSON.parse(localStorage.getItem(this.#storageId) || "{}");
        
        if (this.#subObjectId) {
            if (!data.hasOwnProperty(this.#subObjectId)) data[this.#subObjectId] = {};
            data[this.#subObjectId][key] = value;
        } else {
            data[key] = value;
        }
        
        localStorage.setItem(this.#storageId, JSON.stringify(data));
    }

    /**
     * Read local storage
     */
    get(key) {
        const data = JSON.parse(localStorage.getItem(this.#storageId) || "{}");

        if (this.#subObjectId) {
            if (!data.hasOwnProperty(this.#subObjectId) || 
                !data[this.#subObjectId].hasOwnProperty(key)) return null;

            return data[this.#subObjectId][key];
        } else {
            if (!data.hasOwnProperty(key)) return null;
            
            return data[key];
        }
    }
}