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
        }
        
        return this.underscoreToDisplayName(this.entity.name);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    /**
     * Special implementation for rig select
     */
    #getDisplayNameRigSelect(actionDefinition) {
        const rig_off = this.getArgument(actionDefinition, "rig_off");
        if (actionDefinition && !(rig_off == "None" || rig_off == null)) {
            return this.replaceParameterTokens(actionDefinition, "Toggle Rigs {rig}/{rig_off}");
        }

        return this.replaceParameterTokens(actionDefinition, "Select Rig {rig}");
    }
}