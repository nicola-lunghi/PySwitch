class KemperParserTests {

    pyswitch = null;    // Shared python runner

    ///////////////////////////////////////////////////////////////////////////////////////////

    async minimal() {
        await this.#init();
        const config = new MockConfiguration("", "");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        await expectAsync(parser.input(1)).toBeRejected();
        await expectAsync(parser.input(25)).toBeRejected();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async removeAction() {        
        await this.#init();
        const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        // Remove from switch 2
        async function remove(index, hold = false) {
            const input = await parser.input(25);
            await input.remove_action(index, hold);
        }

        await expectAsync(remove(-1)).toBeRejected();
        await expectAsync(remove(3)).toBeRejected();

        await remove(1);

        await this.#testAction(parser, {
            port: 25,
            actions: [
                { 
                    name: "BANK_UP",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_2"
                        }
                    ] 
                },
                { 
                    name: "RIG_UP",
                    arguments: [
                        {
                            name: "some",
                            value: "val"
                        },
                        {
                            name: "numb",
                            value: '78'
                        }
                    ] 
                }
            ] 
        });

        await remove(0);

        await this.#testAction(parser, {
            port: 25,
            actions: [
                { 
                    name: "RIG_UP",
                    arguments: [
                        {
                            name: "some",
                            value: "val"
                        },
                        {
                            name: "numb",
                            value: '78'
                        }
                    ] 
                }
            ] 
        });

        await remove(0);

        await this.#testAction(parser, {
            port: 25,
            actions: [] 
        });

        // Check if everything else is still in place
        await this.#testAction(parser, {
            port: 1,
            actions: [{
                name: "RIG_UP",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_1"
                    },
                    {
                        name: "text",
                        value: '"Rig up"'
                    }
                ]
            }]
        });

        await this.#testAction(parser, {
            port: 9,
            actions: [{ 
                name: "RIG_DOWN",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_FOOTER_1"
                    },
                    {
                        name: "text",
                        value: '"Rig dn"'
                    }
                ]
            }] 
        });

        await this.#testAction(parser, {
            port: 10,
            actions: [{ 
                name: "BANK_DOWN",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_FOOTER_2"
                    }
                ] 
            }] 
        });
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async getInputActionsDefault() {
        await this.#init();
        const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);
        
        await this.#testAction(parser, {
            port: 1,
            actions: [{
                name: "RIG_UP",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_1"
                    },
                    {
                        name: "text",
                        value: '"Rig up"'
                    }
                ]
            }]
        });

        await this.#testAction(parser, {
            port: 25,
            actions: [
                { 
                    name: "BANK_UP",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_2"
                        }
                    ] 
                },
                { 
                    name: "RIG_DOWN",
                    arguments: [] 
                },
                { 
                    name: "RIG_UP",
                    arguments: [
                        {
                            name: "some",
                            value: "val"
                        },
                        {
                            name: "numb",
                            value: '78'
                        },
                        {
                            name: "large",
                            value: '{"d":{"e":{"f":8}}}'
                        },
                        {
                            name: "arr",
                            value: '[{"f": 8, "j": [3, 5,6]}, None, "g"]'
                        }
                    ] 
                }
            ] 
        });

        await this.#testAction(parser, {
            port: 9,
            actions: [{ 
                name: "RIG_DOWN",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_FOOTER_1"
                    },
                    {
                        name: "text",
                        value: '"Rig dn"'
                    }
                ]
            }] 
        });

        await this.#testAction(parser, {
            port: 10,
            actions: [{ 
                name: "BANK_DOWN",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_FOOTER_2"
                    }
                ] 
            }] 
        });
    }

    async getInputActionsHold() {
        await this.#init();
        const config = new WebConfiguration("data/test-presets/get-inputs-hold");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);
        
        await this.#testAction(parser, {
            port: 1,
            actions: [{ 
                name: "RIG_UP",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_1"
                    },
                    {
                        name: "text",
                        value: '"Rig up"'
                    },
                    {
                        name: "calculated_arg",
                        value: "value != None"
                    }
                ] 
            }] 
        });

        await this.#testAction(parser, {
            port: 25,
            actionsHold: [{ 
                name: "TUNER_MODE",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_2"
                    }
                ]
            }], 
            actions: [{ 
                name: "BANK_UP",
                arguments: [] 
            }] 
        });

        await this.#testAction(parser, {
            port: 9,
            actions: [{ 
                name: "RIG_DOWN",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_FOOTER_1"
                    },
                    {
                        name: "text",
                        value: '"Rig dn"'
                    }
                ]
            }] 
        });

        await this.#testAction(parser, {
            port: 10,
            actions: [{ 
                name: "BANK_DOWN",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_FOOTER_2"
                    }
                ] 
            }] 
        });
    }

    //////////////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////////////
        
    /**
     * Tests a single action, controlled by the config object:
     * {
     *      port,
     *      actions: [
     *          {
     *              name: "name",
     *              arguments: [
     *                  {
     *                      name: "name",
     *                      value: value
     *                  }
     *              ]
     *          }
     *      ],
     *      actionsHold: [...]
     * }
     */
    async #testAction(parser, config) {
        const input = await parser.input(config.port);

        async function test(hold, expActions) {
            const actions = await input.actions(hold);

            expect(actions.length).toBe(expActions.length);
    
            for (let i = 0; i < expActions.length; ++i) {
                const action = actions[i];
                const expAction = expActions[i];
    
                expect(action.name).toBe(expAction.name);
                expect(JSON.parse(action.arguments())).toEqual(expAction.arguments);
            }
        }

        if (config.actions) {
            await test(false, config.actions);
        }
        if (config.actionsHold) {
            await test(true, config.actionsHold);
        }
    }

    /**
     * Must be called before any of the tests can be run
     */
    async #init() {
        if (this.pyswitch) return;

        this.pyswitch = new PySwitchRunner(
            {
                domNamespace: "pyswitch",
                updateIntervalMillis: 10
            }, 
            "test-pyswitch-example"
        );

        await this.pyswitch.init("../");
    }
}