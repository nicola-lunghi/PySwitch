class VirtualKemperClientSetup {
    
    #parameters = null;

    constructor(parameters) {
        this.#parameters = parameters;
    }

    /**
     * Set up some data on parameters not contained in any parameter set
     */
    setup() {
        // Amp comment
        this.#parameters.init({ key: NRPNKey([0, 16]), value: "Amp Comment" });

        // FX Slot DLY
        this.#parameters.init({ key: NRPNKey([60, 0]), value: 160 });  // DLY
        this.#parameters.init({ key: NRPNKey([60, 3]), receiveKey: [CCKey(26), CCKey(27)], value: 1 });    // On

        // FX Slot REV
        this.#parameters.init({ key: NRPNKey([61, 0]), value: 180 });  // REV
        this.#parameters.init({ key: NRPNKey([61, 3]), receiveKey: [CCKey(28), CCKey(29)], value: 1 });    // On

        // Default values
        this.#parameters.initDefault({ value: 0 });         // Default for numeric parameters
        this.#parameters.initDefault({ value: "none" });    // Default for string parameters

        // Parameter sets
        this.#setupParameterSet1();
        this.#setupParameterSet2();
    }

    /**
     * Add parameters for parameter set 1 with some foo values 
     */
    #setupParameterSet1() {
        // FX Slot A
        this.#parameters.init({ key: NRPNKey([50, 0]), value: 8, parameterSets: [1, 2, 3, 4] });  // Wah
        this.#parameters.init({ key: NRPNKey([50, 3]), value: 1, receiveKey: CCKey(17), parameterSets: [1, 2, 3, 4] });  // On
        
        // FX Slot B
        this.#parameters.init({ key: NRPNKey([51, 0]), value: 13, parameterSets: [1, 2, 3, 4] });  // Pitch
        this.#parameters.init({ key: NRPNKey([51, 3]), value: 1, receiveKey: CCKey(18), parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot C
        this.#parameters.init({ key: NRPNKey([52, 0]), value: 30, parameterSets: [1, 2, 3, 4] });  // Dist
        this.#parameters.init({ key: NRPNKey([52, 3]), value: 1, receiveKey: CCKey(19), parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot D
        this.#parameters.init({ key: NRPNKey([53, 0]), value: 50, parameterSets: [1, 2, 3, 4] });  // Comp
        this.#parameters.init({ key: NRPNKey([53, 3]), value: 1, receiveKey: CCKey(20), parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot X
        this.#parameters.init({ key: NRPNKey([56, 0]), value: 115, parameterSets: [1, 2, 3, 4] });  // EQ
        this.#parameters.init({ key: NRPNKey([56, 3]), value: 1, receiveKey: CCKey(22), parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot MOD
        this.#parameters.init({ key: NRPNKey([58, 0]), value: 100, parameterSets: [1, 2, 3, 4] });  // Phaser
        this.#parameters.init({ key: NRPNKey([58, 3]), value: 1, receiveKey: CCKey(24), parameterSets: [1, 2, 3, 4] });  // On
    }

    /**
     * Add parameters for parameter set 2 with some foo values 
     */
    #setupParameterSet2() {
        // Rig name
        this.#parameters.init({ key: NRPNKey([0, 1]), value: "Rig Name", parameterSets: [2, 3, 4] });  // Rig Name
    }
}