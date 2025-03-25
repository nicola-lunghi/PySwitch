class ActionPropertiesEncoder {

    #props = null;

    constructor(props) {
        this.#props = props;
    }

    async setup() {
        if (this.#props.actionDefinition.name != "ENCODER_BUTTON") return;

        this.#props.showParameter("assign");
        this.#props.inputs.get("assign").val(await this.#getNextEncoderAssign());
    }

    /**
     * Returns an unused encoder assign target name
     */
    async #getNextEncoderAssign() {
        const encoderActions = await this.#props.parserFrontend.parser.actions("ENCODER_BUTTON");

        function buttonExists(assign) {
            for (const button of encoderActions) {
                if (button.assign == assign) return true;
            }
            return false;
        }

        let ret = "_encoder_button";
        let cnt = 2;
        while (buttonExists(ret)) {
            ret = "_encoder_button" + cnt++;
        }
        return ret;
    }
}