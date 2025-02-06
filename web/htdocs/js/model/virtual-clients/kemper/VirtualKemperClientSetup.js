class VirtualKemperClientSetup {
    
    #client = null;

    constructor(client) {
        this.#client = client;
    }

    /**
     * Set up some data on parameters not contained in any parameter set
     */
    setup() {
        this.#setupParameters();
        this.#setupRigChange();
        this.#setupTempo();
        this.#setupTuner();
        this.#setupMorph();

        // Default values
        this.#client.parameters.initDefault({ value: 0 });         // Default for numeric parameters
        this.#client.parameters.initDefault({ value: "none" });    // Default for string parameters
    }

    /**
     * Set up all rig/bank change parameters
     */
    #setupRigChange() {
        const that = this;

        // Rig ID
        this.#client.parameters.init({ 
            keys: new VirtualKemperParameterKeys({ send: new CCKey(32) }),
            value: 0,
            parameterSets: [1, 2, 3, 4],
            noBuffer: true
        });
        this.#client.parameters.init({ 
            keys: new VirtualKemperParameterKeys({ send: new PCKey() }),
            value: 0,
            parameterSets: [1, 2, 3, 4],
            noBuffer: true
        });

        // Bank preselect
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(47) }) });
        
        // Rig select
        let lastRigId = null;

        function onRigIdChange(param, value) {
            const rig = param.config.keys.receive[0].control - 50;
            const bankPreselect = that.#client.parameters.get(new CCKey(47)).value;
            
            // Reset bank preselect
            that.#client.parameters.get(new CCKey(47)).setValue(null);

            const bank = (bankPreselect !== null) ? bankPreselect : Math.floor(that.#client.getRigId() / 5);
            const rigId = bank * 5 + rig;

            if (value == 1) {
                // Update rig
                that.#client.setRigId(rigId);

                if (that.#client.morph.rigBtnMorph && lastRigId == rigId) {
                    that.#client.morph.triggerButton();
                }
                
                lastRigId = rigId;
            }
        }

        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(50) }), callback: onRigIdChange });
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(51) }), callback: onRigIdChange });
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(52) }), callback: onRigIdChange });
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(53) }), callback: onRigIdChange });
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(54) }), callback: onRigIdChange });

        // Bank up/down
        function onBankChange(param, value) {
            if (value == 0) {
                let rigId = that.#client.getRigId();
                rigId += (param.config.keys.receive[0].control == 48) ? 5 : -5;
                if (rigId < 0) rigId = 125;
                if (rigId > 125) rigId -= 126;

                that.#client.setRigId(rigId);
            }
        }

        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(48) }), callback: onBankChange, noBuffer: true });  // Up
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(49) }), callback: onBankChange, noBuffer: true });  // Down
    }

    /**
     * Set up tempo related stuff
     */
    #setupTempo() {
        const that = this;

        // Tempo display
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([124, 0]) }), parameterSets: [1, 2, 3, 4] });

        // Tap tempo
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(30) }), callback: function(param, value) {
            that.#client.tempo.tap(value);
        } });
    }

    /**
     * Set up tuner related stuff
     */
    #setupTuner() {
        const that = this;

        // Tuner mode
        function onTunerModeChange(param, value) {
            that.#client.tuner.running = (value == 1);
        }
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([127, 126]), receive: new CCKey(31) }), parameterSets: [1, 2, 3, 4], callback: onTunerModeChange });

        // Tuner note
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([125, 84]) }), parameterSets: [1, 2, 3, 4] });

        // Tuner deviance
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([124, 15]) }), parameterSets: [1, 2, 3, 4], value: 8191 });
    }

    /**
     * Set up morph state
     */
    #setupMorph() {
        const that = this;

        // Morph state
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([0, 11]), receive: new CCKey(11) }) });

        // Morph button
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ receive: new CCKey(80) }), callback: function(param, value) {
            // Update morph state
            if (value == 1) {
                that.#client.morph.triggerButton();
            }
        } });
    }

    /**
     * Sets up all "normal" parameter stuff
     */
    #setupParameters() {
        // Amp comment
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([0, 16]) }), value: "Amp Comment" });

        // FX Slot DLY
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([60, 0]) }), value: 160 });  // DLY
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([60, 3]), receive: [new CCKey(26), new CCKey(27)] }), value: 1 });    // On

        // FX Slot REV
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([61, 0]) }), value: 180 });  // REV
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([61, 3]), receive: [new CCKey(28), new CCKey(29)] }), value: 1 });    // On

        // Parameter sets
        this.#setupParameterSet1();
        this.#setupParameterSet2();
    }
    
    /**
     * Add parameters for parameter set 1 with some foo values 
     */
    #setupParameterSet1() {
        // FX Slot A
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([50, 0]) }), value: 8, parameterSets: [1, 2, 3, 4] });  // Wah
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([50, 3]), receive: new CCKey(17) }), value: 1, parameterSets: [1, 2, 3, 4] });  // On
        
        // FX Slot B
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([51, 0]) }), value: 13, parameterSets: [1, 2, 3, 4] });  // Pitch
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([51, 3]), receive: new CCKey(18) }), value: 1, parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot C
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([52, 0]) }), value: 30, parameterSets: [1, 2, 3, 4] });  // Dist
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([52, 3]), receive: new CCKey(19) }), value: 0, parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot D
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([53, 0]) }), value: 50, parameterSets: [1, 2, 3, 4] });  // Comp
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([53, 3]), receive: new CCKey(20) }), value: 1, parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot X
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([56, 0]) }), value: 115, parameterSets: [1, 2, 3, 4] });  // EQ
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([56, 3]), receive: new CCKey(22) }), value: 1, parameterSets: [1, 2, 3, 4] });  // On

        // FX Slot MOD
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([58, 0]) }), value: 100, parameterSets: [1, 2, 3, 4] });  // Phaser
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([58, 3]), receive: new CCKey(24) }), value: 1, parameterSets: [1, 2, 3, 4] });  // On
    }

    /**
     * Add parameters for parameter set 2 with some foo values 
     */
    #setupParameterSet2() {
        // Rig name
        this.#client.parameters.init({ keys: new VirtualKemperParameterKeys({ send: new NRPNKey([0, 1]) }), value: "Rig Name", parameterSets: [2, 3, 4] });  // Rig Name
    }
}