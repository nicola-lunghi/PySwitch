/**
 * Manages local storage content
 */
class LocalState {

    #storageId = null;
    
    /**
     * storageId is the ID of the local storage cookie (will be prefixed with "pyswitch-X.X.X-").
     * stateObjectId is the sub-object name. If not set, the keys will be placed in the root object.
     */
    constructor(controller, storageId, noVersion = false) {
        this.#storageId = noVersion ? "pyswitch" : ("pyswitch-" + controller.VERSION + "-" + storageId);
    }

    /**
     * Set a variable in local storage
     */
    set(key, value) {
        const data = JSON.parse(localStorage.getItem(this.#storageId) || "{}");
        
        data[key] = value;
        
        localStorage.setItem(this.#storageId, JSON.stringify(data));
    }

    /**
     * Read local storage
     */
    get(key) {
        const data = JSON.parse(localStorage.getItem(this.#storageId) || "{}");

        if (!data.hasOwnProperty(key)) return null;
            
        return data[key];
    }
}