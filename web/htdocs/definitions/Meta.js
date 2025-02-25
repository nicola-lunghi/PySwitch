/**
 * This class defines the action/mapping specific meta information. For new actions/mappings, 
 * add stuff here, too, to get good looking output.
 */
class Meta extends MetaBase {

    /**
     * Returns the display name for specific actions
     */
    getDisplayName(actionDefinition) {
        // All actions/mappings not handled here will show with their technical function names.
        switch (this.entity.name) {
            case "RIG_SELECT": return this.#getDisplayNameRigSelect(actionDefinition)
            case "RIG_SELECT_AND_MORPH_STATE": return this.#getDisplayNameRigSelectAndMorphState(actionDefinition)
            case "BANK_SELECT": return this.#getDisplayNameBankSelect(actionDefinition)
            case "EFFECT_BUTTON": return this.#getDisplayNameEffectButton(actionDefinition)
            case "EFFECT_STATE": return this.#getDisplayNameEffectState(actionDefinition)
            case "BINARY_SWITCH": return "Other"
        }
        
        return this.underscoreToDisplayName(this.entity.name);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Special implementation for rig select
     */
    #getDisplayNameRigSelect(actionDefinition) {
        const rig_off = this.getArgument(actionDefinition, "rig_off");
        if (actionDefinition && !(rig_off == null || rig_off.value == "None")) {
            return this.replaceParameterTokens(actionDefinition, "Toggle Rigs {rig}/{rig_off}");
        }

        if (!actionDefinition) {
            return "Select Rig";  
        }

        return this.replaceParameterTokens(actionDefinition, "Select Rig {rig}");
    }

    /**
     * Special implementation for rig select and morph state
     */
    #getDisplayNameRigSelectAndMorphState(actionDefinition) {
        const rig_off = this.getArgument(actionDefinition, "rig_off");
        if (actionDefinition && !(rig_off == null || rig_off.value == "None")) {
            return this.replaceParameterTokens(actionDefinition, "Toggle Rigs {rig}/{rig_off} & Morph Display");
        }

        if (!actionDefinition) {
            return "Select Rig & Morph Display";  
        }

        return this.replaceParameterTokens(actionDefinition, "Select Rig {rig} & Morph Display");
    }

    /**
     * Special implementation for bank select
     */
    #getDisplayNameBankSelect(actionDefinition) {
        const bank_off = this.getArgument(actionDefinition, "bank_off");
        const preselect = this.getArgument(actionDefinition, "preselect");
        
        if (!actionDefinition) {
            return "Select Bank";  
        }

        if (!(bank_off == null || bank_off.value == "None")) {
            return this.replaceParameterTokens(actionDefinition, "Toggle Banks {bank}/{bank_off}");
        }

        if (preselect && (preselect.value == "True")) {
            return this.replaceParameterTokens(actionDefinition, "Preselect Bank {bank}");
        }

        return this.replaceParameterTokens(actionDefinition, "Select Bank {bank}");
    }

    /**
     * Special implementation for effect buttons
     */
    #getDisplayNameEffectButton(actionDefinition) {
        const num = this.getArgument(actionDefinition, "num");
        if (actionDefinition && num) {
            return this.replaceParameterTokens(actionDefinition, "Effect Button {num}");
        }

        return "Effect Button";
    }

    /**
     * Special implementation for effect state
     */
    #getDisplayNameEffectState(actionDefinition) {
        const slot_id = this.getArgument(actionDefinition, "slot_id");
        if (actionDefinition && slot_id) {
            function getSlotName(id) {
                switch (id) {
                    case "KemperEffectSlot.EFFECT_SLOT_ID_A": return "A";
                    case "KemperEffectSlot.EFFECT_SLOT_ID_B": return "B";
                    case "KemperEffectSlot.EFFECT_SLOT_ID_C": return "C";
                    case "KemperEffectSlot.EFFECT_SLOT_ID_D": return "D";

                    case "KemperEffectSlot.EFFECT_SLOT_ID_X": return "X";
                    case "KemperEffectSlot.EFFECT_SLOT_ID_MOD": return "MOD";
                    case "KemperEffectSlot.EFFECT_SLOT_ID_DLY": return "DLY";
                    case "KemperEffectSlot.EFFECT_SLOT_ID_REV": return "REV";
                }
                return "?";
            }

            return "Effect State " + getSlotName(slot_id.value);
        }

        return "Effect State";
    }
}