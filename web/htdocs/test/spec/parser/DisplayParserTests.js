class DisplayParserTests extends TestBase {

    async getDisplaysDefault() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "data/test-display/get-displays-default");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        await this.#testDisplay(parser, {
            splashes: {
                name: "TunerDisplayCallback",
                elements: [
                    {
                        name: "DisplayLabel",
                        assign: "DISPLAY_HEADER_1",
                        arguments: [
                            {
                                name: "layout",
                                value: "_ACTION_LABEL_LAYOUT"
                            },
                            {
                                name: "bounds",
                                value: "DisplayBounds(_SLOT_WIDTH, 0, _SLOT_WIDTH, _SLOT_HEIGHT)"
                            }
                        ]
                    },
                    {
                        name: "DisplayLabel",
                        assign: "DISPLAY_HEADER_2",
                        arguments: [
                            {
                                name: "layout",
                                value: "_ACTION_LABEL_LAYOUT"
                            },
                            {
                                name: "bounds",
                                value: "DisplayBounds(_SLOT_WIDTH, 0, _SLOT_WIDTH, _SLOT_HEIGHT)"
                            }
                        ]
                    },

                    {
                        name: "DisplayLabel",
                        assign: "DISPLAY_FOOTER_1",
                        arguments: [
                            {
                                name: "layout",
                                value: "_ACTION_LABEL_LAYOUT"
                            },
                            {
                                name: "bounds",
                                value: "DisplayBounds(0, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)"
                            }
                        ]
                    },
                    {
                        name: "DisplayLabel",
                        assign: "DISPLAY_FOOTER_2",
                        arguments: [
                            {
                                name: "layout",
                                value: "_ACTION_LABEL_LAYOUT"
                            },
                            {
                                name: "bounds",
                                value: "DisplayBounds(_SLOT_WIDTH, _FOOTER_Y, _SLOT_WIDTH, _SLOT_HEIGHT)"
                            }
                        ]
                    },
                    {
                        name: "DisplayLabel",
                        arguments: [
                            {
                                name: "layout",
                                value: "TODO"
                            },
                            {
                                name: "bounds",
                                value: "TODO"
                            },
                            {
                                name: "callback",
                                value: "TODO"
                            }
                        ]
                    },
                    {
                        name: "BidirectionalProtocolState",
                        arguments: []
                    }
                ]
            }
        });
    }

    /**
     * {
     *      splashes: {
     *           name,
     *           elements: [
     *                  {
     *                      name,
     *                      assign,
     *                      arguments,
     *                  }
     *           ]
     *      }
     * }
     */
    async #testDisplay(parser, config) {
        const splashes = await parser.splashes();        
        expect(splashes.name).toBe(config.splashes.name);

        const elements = splashes.elements();
        expect(elements.length).toBe(config.splashes.elements.length);

        for (let i = 0; i < config.splashes.elements.length; ++i) {
            const element = elements[i];
            const expElement = config.splashes.elements[i];

            expect(element.name).toBe(expElement.name);

            if (expElement.assign) {
                expect(element.assign).toBe(expElement.assign);
            }
            
            if (action.client != "local") expect(action.client).toBe(config.client);

            if (expElement.arguments) {
                expect(JSON.parse(element.arguments())).toEqual(expElement.arguments);
            } else {
                expect(JSON.parse(element.arguments())).toEqual([]);
            }
        }
    }
}