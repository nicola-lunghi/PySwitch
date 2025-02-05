/**
 * Key for a NRPN parameter
 */
class NRPNKey {
    constructor(data) {
        this.data = data;
    }

    getId() {
        return JSON.stringify(this.data);
    }
}

/**
 * Key for a CC parameter
 */
class CCKey {
    constructor(control) {
        this.control = control;
    }

    getId() {
        return JSON.stringify({ control: this.control });
    }
}