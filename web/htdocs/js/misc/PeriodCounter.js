class PeriodCounter {

    interval = null;

    #lastReset = 0;

    constructor(intervalMillis, reset = true) {
        this.interval = intervalMillis;

        if (reset) this.reset();
    }
    
    /**
     * Resets the period counter to the current time
     */
    reset() {
        this.#lastReset = Date.now();
    }

    /**
     * Returns the amount of milliseconds passed since the last reset
     */
    passed() {
        return Date.now() - this.#lastReset;
    }

    /**
     * Returns if the period has been exceeded. If yes, it lso resets 
     * the period to the current time.
     */
    exceeded() {
        const currentTime = Date.now();
        if (this.#lastReset + this.interval < currentTime) {
            this.#lastReset = currentTime;
            return true;
        }
        return false;
    }
}