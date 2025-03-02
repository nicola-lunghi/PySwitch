/**
 * Metadata for functions (kemper overrides)
 */
class KemperFunctionMeta extends FunctionMeta {

    /**
     * Returns the display name for specific actions
     */
    getDisplayName(actionCallProxy = null) {
        switch (this.functionDefinition.name) {
            case "RIG_SELECT_AND_MORPH_STATE": return this.client.getDisplayName() + ": " + this.#getDisplayNameRigSelectAndMorphState(actionCallProxy)
        }

        return this.client.getDisplayName() + ": " + this.getShortDisplayName(actionCallProxy);
    }

    /**
     * Returns the display name for specific actions
     */
    getShortDisplayName(actionCallProxy = null) {
        switch (this.functionDefinition.name) {
            case "RIG_SELECT": return this.#getDisplayNameRigSelect(actionCallProxy)
            case "RIG_SELECT_AND_MORPH_STATE": return this.#getDisplayNameRigSelectAndMorphStateShort(actionCallProxy)
            case "BANK_SELECT": return this.#getDisplayNameBankSelect(actionCallProxy)
            case "EFFECT_BUTTON": return this.#getDisplayNameEffectButton(actionCallProxy)
            case "EFFECT_STATE": return this.#getDisplayNameEffectState(actionCallProxy)
            case "BINARY_SWITCH": return this.#getDisplayNameBinarySwitch(actionCallProxy)
        }
        
        return super.getShortDisplayName(actionCallProxy);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Special implementation for rig select
     */
    #getDisplayNameRigSelect(actionCallProxy = null) {
        const rig_off = this.#getArgument(actionCallProxy, "rig_off");
        if (actionCallProxy && !(rig_off == null || rig_off.value == "None")) {
            return this.#replaceParameterTokens(actionCallProxy, "Toggle Rigs {rig}/{rig_off}");
        }

        if (!actionCallProxy) {
            return "Select Rig";  
        }

        return this.#replaceParameterTokens(actionCallProxy, "Select Rig {rig}");
    }

    /**
     * Special implementation for rig select and morph state
     */
    #getDisplayNameRigSelectAndMorphState(actionCallProxy = null) {
        const rig_off = this.#getArgument(actionCallProxy, "rig_off");

        if (actionCallProxy && !(rig_off == null || rig_off.value == "None")) {
            return this.#replaceParameterTokens(actionCallProxy, "Toggle Rigs {rig}/{rig_off} & Morph Display");
        }

        if (!actionCallProxy) {
            return "Select Rig & Morph Display";  
        }

        return this.#replaceParameterTokens(actionCallProxy, "Select Rig {rig} & Morph Display");
    }

    /**
     * Special implementation for rig select and morph state (short version)
     */
    #getDisplayNameRigSelectAndMorphStateShort(actionCallProxy = null) {
        const rig_off = this.#getArgument(actionCallProxy, "rig_off");
        
        if (actionCallProxy && !(rig_off == null || rig_off.value == "None")) {
            return this.#replaceParameterTokens(actionCallProxy, "Rigs {rig}/{rig_off} & Morph");
        }

        if (!actionCallProxy) {
            return "Rig & Morph";
        }

        return this.#replaceParameterTokens(actionCallProxy, "Rig {rig} & Morph");
    }

    /**
     * Special implementation for bank select
     */
    #getDisplayNameBankSelect(actionCallProxy = null) {
        const bank_off = this.#getArgument(actionCallProxy, "bank_off");
        const preselect = this.#getArgument(actionCallProxy, "preselect");
        
        if (!actionCallProxy) {
            return "Select Bank";  
        }

        if (!(bank_off == null || bank_off.value == "None")) {
            return this.#replaceParameterTokens(actionCallProxy, "Toggle Banks {bank}/{bank_off}");
        }

        if (preselect && (preselect.value == "True")) {
            return this.#replaceParameterTokens(actionCallProxy, "Preselect Bank {bank}");
        }

        return this.#replaceParameterTokens(actionCallProxy, "Select Bank {bank}");
    }

    /**
     * Special implementation for effect buttons
     */
    #getDisplayNameEffectButton(actionCallProxy = null) {
        const num = this.#getArgument(actionCallProxy, "num");
        if (actionCallProxy && num) {
            return this.#replaceParameterTokens(actionCallProxy, "Effect Button {num}");
        }

        return "Effect Button";
    }

    /**
     * Special implementation for effect state
     */
    #getDisplayNameEffectState(actionCallProxy = null) {
        const slot_id = this.#getArgument(actionCallProxy, "slot_id");
        if (actionCallProxy && slot_id) {
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

    /**
     * Special implementation for Binary Switch action
     */
    #getDisplayNameBinarySwitch(actionCallProxy = null) {
        if (!actionCallProxy) return "Other";

        const mapping = this.#getArgument(actionCallProxy, "mapping");

        if (!(mapping == null || mapping.value == "None")) {
            return this.underscoreToDisplayName(
                mapping.value
                .replace("MAPPING_", "")
                .replace("KemperMappings.", "")
                .replace(/\((.+?)*\)/g, "")
            );
        }

        return "Other";
    }   

    /////////////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Gets the name of a argument in the given definition
     */
    #getArgument(actionCallProxy = null, name) {
        if (!actionCallProxy) return null;
        
        const args = JSON.parse(actionCallProxy.arguments());

        for (const arg of args) {
            if (arg.name == name) return arg;
        }
        return null;
    }

    /**
     * Replaces all tokens for parameters
     */
    #replaceParameterTokens(actionCallProxy = null, str) {
        function getReplaceValue(param) {
            for (const def of (actionCallProxy ? (JSON.parse(actionCallProxy.arguments()) || []) : [])) {
                if (def.name == param.name) {
                    return def.value;
                }
            }

            return param.meta.getDefaultValue();
        }

        function replaceToken(str, token, value) {
            return str.replace("{" + token + "}", "" + value);
        }

        for (const param of this.functionDefinition.parameters) {
            str = replaceToken(str, param.name, getReplaceValue(param))
        }

        return str;
    }
}