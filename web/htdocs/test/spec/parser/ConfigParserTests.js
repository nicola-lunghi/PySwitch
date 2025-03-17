class ConfigParserTests extends TestBase {

    async minimal() {
        await this.init();
        const config = new MockConfiguration("", "");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        await expectAsync(parser.input(1)).toBeRejected();
        await expectAsync(parser.input(25)).toBeRejected();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async getInputSettings() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "data/test-presets/get-input-settings");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;
        
        await this.#testAction(parser, {
            port: 1,
            client: "kemper",
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
            }],
            holdTimeMillis: 555,
            holdRepeat: true
        });
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async getInputActionsDefault() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-default");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;
        
        await this.#testAction(parser, {
            port: 1,
            client: "kemper",
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
            client: "kemper",
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
            client: "kemper",
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
            client: "kemper",
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
        await this.init();
        const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-hold");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;
        
        await this.#testAction(parser, {
            port: 1,
            client: "kemper",
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
            client: "kemper",
            actionsHold: [{ 
                name: "TUNER_MODE",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_2"
                    }
                ]
            }], 
            actions: [
                { 
                    name: "BANK_UP",
                    arguments: [] 
                },
                {
                    name: "None"
                }
            ] 
        });

        await this.#testAction(parser, {
            port: 9,
            client: "kemper",
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
            client: "kemper",
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

    async getInputActionsDeferred() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-assign");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;
        
        await this.#testAction(parser, {
            port: 1,
            client: "kemper",
            actions: [{ 
                name: "RIG_UP",
                assign: "_deferred_2",
                arguments: [
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_1"
                    },
                    {
                        name: "text",
                        value: '"foo"'
                    },
                    {
                        name: "id",
                        value: "303"
                    }
                ] 
            }] 
        });

        await this.#testAction(parser, {
            port: 25,
            client: "kemper",
            actions: [
                { 
                    name: "BANK_UP",
                    arguments: [] 
                }
            ],
            actionsHold: [
                { 
                    name: "TUNER_MODE",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_2"
                        }
                    ]
                },
                {
                    name: "RIG_DOWN",
                    assign: "_deferred",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_FOO"
                        }
                    ]
                }
            ]
        });
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async replaceActions() {
        await this.#replaceActions(
            1, 
            [
                { 
                    name: "SOME_ACTION",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_5"
                        }
                    ] 
                },
                { 
                    name: "SOME_ACTION_2",
                    arguments: [
                        {
                            name: "useLeds",
                            value: "{3:4}"
                        }
                    ] 
                }
            ],
            "local"
        );

        await this.#replaceActions(
            9, 
            [
                { 
                    name: "SOME_ACTION",
                    arguments: [] 
                }
            ],
            "local"
        );

        await this.#replaceActions(
            9, 
            [],
            "local"
        );
    }

    async replaceActionsDeferred() {
        await this.#replaceActions(
            1, 
            [
                { 
                    name: "SOME_ACTION",
                    assign: "_foo",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_5"
                        }
                    ] 
                },
                { 
                    name: "SOME_ACTION_2",
                    assign: "_bar",
                    arguments: [
                        {
                            name: "useLeds",
                            value: "{3:4}"
                        }
                    ] 
                }
            ],
            "local"
        );

        await this.#replaceActions(
            9, 
            [
                { 
                    name: "SOME_ACTION",
                    assign: "_bar2",
                    arguments: [] 
                }
            ],
            "local"
        );

        await this.#replaceActions(
            9, 
            [],
            "local"
        );
    }

    async replaceActionsPaging() {
        await this.#replaceActions(
            1, 
            [
                { 
                    name: "PagerAction",
                    assign: "_pager",
                    arguments: [
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_5"
                        },
                        {
                            name: "pages",
                            value: [
                                {
                                    id: "10",
                                    color: "Colors.GREEN",
                                    text: '"sometext"'
                                },
                                {
                                    id: '"other"',
                                    color: "(3, 4, 5)",
                                    text: '"someothertext"'
                                }
                            ]
                        }
                    ] 
                }
            ],
            "local",
            // true
        );
    }

    async #replaceActions(port, actions, clientId, debug = false) {
        await this.init();
        const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-default");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input = await parser.input(port);
        
        // Replace actions
        input.set_actions(actions)

        if (debug) {
            console.log(actions);
            console.log((await config.get()).inputs_py);
        }

        await this.#testAction(parser, {
            port: port,
            client: clientId,
            actions: actions
        });

        // Replace actionsHold
        input.set_actions(actions, true)

        await this.#testAction(parser, {
            port: port,
            client: clientId,
            actions: actions,
            actionsHold: actions
        });
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////////

    async createNewInputs() {
        await this.init();

        const config = new WebConfiguration(new MockController(), "data/test-presets/empty");
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input1 = await parser.input(1);
        expect(input1).toEqual(undefined);

        const input2 = await parser.input(1, true);
        
        input2.set_actions(
            [
                {
                    name: "RIG_SELECT",
                    arguments: [
                        {
                            name: "rig",
                            value: "1"
                        },
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_2"
                        }
                    ]
                }
            ]
        );
        
        // console.log((await parser.config.get()).inputs_py);

        await this.#testAction(parser, {
            port: 1,
            client: "kemper",
            actions: [{
                name: "RIG_SELECT",
                arguments: [
                    {
                        name: "rig",
                        value: "1"
                    },
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_2"
                    }
                ]
            }]
        });
    }

    async createNewInputsWithSettings() {
        await this.init();

        const config = new WebConfiguration(new MockController(), "data/test-presets/empty");
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input = await parser.input(1, true);

        input.set_actions(
            [
                {
                    name: "RIG_SELECT",
                    arguments: []
                }
            ]
        );

        input.set_hold_time_millis(765)
        input.set_hold_repeat(true)

        expect(input.hold_time_millis()).toBe(765);
        expect(input.hold_repeat()).toBe(true);
                
        // console.log((await parser.config.get()).inputs_py);

        await this.#testAction(parser, {
            port: 1,
            client: "kemper",
            actions: [{
                name: "RIG_SELECT",
                arguments: []
            }],
            holdTimeMillis: 765,
            holdRepeat: true
        });
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////////

    async addOneImport() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "../templates/MIDICaptain Nano 4");
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input1 = await parser.input(1);
        
        // Add first actions available
        const clients = await parser.getAvailableActions();
        const action = clients[0].actions[0];
        const client = clients[0].client;

        input1.set_actions(
            [
                this.#composeAction(action, client)
            ]
        );
        
        // console.log((await parser.config.get()).inputs_py);

        // Test with PySwitch
        await this.runner.run(config);

        expect(1).toBe(1);
    }

    async addAllImports() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "../templates/MIDICaptain Nano 4");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input1 = await parser.input(1);
        
        // Add all actions available
        const clients = await parser.getAvailableActions();
        
        const actions = [];
        for (const client of clients) {
            for (const action of client.actions) {
                if (action.meta.data.target != "AdafruitSwitch") continue;

                actions.push(
                    this.#composeAction(action, client.client)
                )
            }
        }

        expect(actions.length).toBeGreaterThan(0);

        input1.set_actions(
            actions.filter((item) => item != null)
        );
        
        // console.log((await parser.config.get()).inputs_py);

        // Test with PySwitch
        await this.runner.run(config);

        expect(1).toBe(1);
    }

    async addDisplayImports() {
        await this.init();
        const config = new WebConfiguration(new MockController(), "../templates/MIDICaptain Nano 4");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input1 = await parser.input(1);
        
        input1.set_actions(
            [
                {
                    name: "RIG_SELECT",
                    arguments: [
                        {
                            name: "rig",
                            value: "1"
                        },
                        {
                            name: "display",
                            value: "DISPLAY_HEADER_2"
                        }
                    ]
                }
            ]
        );
        
        // console.log((await parser.config.get()).inputs_py);

        // Test with PySwitch
        await this.runner.run(config);

        expect(1).toBe(1);
    }

    /**
     * Helper for import tests: Returns an action definition for setting, 
     * from a given action definition loaded by the parser.
     */
    #composeAction(item, client) {
        return {
            name: (item.name == "PagerAction.proxy") ? "_pager.proxy" : item.name,
            assign: (item.name == "PagerAction") ? "_pager" : null,
            client: client,
            arguments: item.parameters.map(                
                function (param) {
                    if (item.name == "PagerAction" && param.name == "pages") {
                        return {
                            name: param.name,
                            value: []
                        }
                    }

                    if (item.name == "PagerAction.proxy" && param.name == "page_id") {
                        return {
                            name: param.name,
                            value: "1"
                        }
                    }

                    return {
                        name: param.name,
                        value: param.meta.getDefaultValue()
                    }
                }
            )
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async displayNameGeneric() {
        await this.#checkActionMeta(
            "BANK_UP",
            {
                name: "BANK_UP",
                client: "kemper",
                arguments: []
            },
            "Kemper: Bank Up",   // Default
            "Kemper: Bank Up"    // With actual value
        );

        await this.#checkActionMeta(
            "BANK_DOWN",
            {
                name: "BANK_DOWN",
                client: "kemper",
                arguments: []
            },
            "Kemper: Bank Down",   // Default
            "Kemper: Bank Down"    // With actual value
        );
    }

    async displayNameRigSelect() {
        await this.#checkActionMeta(
            "RIG_SELECT",
            {
                name: "RIG_SELECT",
                client: "kemper",
                arguments: [
                    {
                        name: "rig",
                        value: "2"
                    },
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_2"
                    }
                ]
            },
            "Kemper: Select Rig",   // Default
            "Kemper: Select Rig 2"    // With actual value
        )
    }

    async displayNameRigSelectToggle() {
        await this.#checkActionMeta(
            "RIG_SELECT",
            {
                name: "RIG_SELECT",
                client: "kemper",
                arguments: [
                    {
                        name: "rig",
                        value: "2"
                    },
                    {
                        name: "rig_off",
                        value: "4"
                    },
                    {
                        name: "display",
                        value: "DISPLAY_HEADER_2"
                    }
                ]
            },
            "Kemper: Select Rig",      // Default
            "Kemper: Toggle Rigs 2/4"    // With actual value
        )        
    }

    async displayNameBankSelect() {
        await this.#checkActionMeta(
            "BANK_SELECT",
            {
                name: "BANK_SELECT",
                client: "kemper",
                arguments: [
                    {
                        name: "bank",
                        value: "2"
                    }
                ]
            },
            "Kemper: Select Bank",   // Default
            "Kemper: Select Bank 2"    // With actual value
        );

        await this.#checkActionMeta(
            "BANK_SELECT",
            {
                name: "BANK_SELECT",
                client: "kemper",
                arguments: [
                    {
                        name: "bank",
                        value: "2"
                    },
                    {
                        name: "bank_off",
                        value: "4"
                    }
                ]
            },
            "Kemper: Select Bank",      // Default
            "Kemper: Toggle Banks 2/4"    // With actual value
        );

        await this.#checkActionMeta(
            "BANK_SELECT",
            {
                name: "BANK_SELECT",
                client: "kemper",
                arguments: [
                    {
                        name: "bank",
                        value: "3"
                    },
                    {
                        name: "preselect",
                        value: "True"
                    }
                ]
            },
            "Kemper: Select Bank",      // Default
            "Kemper: Preselect Bank 3"    // With actual value
        );

        await this.#checkActionMeta(
            "BANK_SELECT",
            {
                name: "BANK_SELECT",
                client: "kemper",
                arguments: [
                    {
                        name: "bank",
                        value: "3"
                    },
                    {
                        name: "preselect",
                        value: "False"
                    }
                ]
            },
            "Kemper: Select Bank",      // Default
            "Kemper: Select Bank 3"    // With actual value
        )
    }

    async #checkActionMeta(name, action, expNameDefault, expNameCurrent) {
        await this.#doCheckActionMeta(name, action, expNameDefault, expNameCurrent, false);
        await this.#doCheckActionMeta(name, action, expNameDefault, expNameCurrent, true);
    }

    async #doCheckActionMeta(name, action, expNameDefault, expNameCurrent, hold) {
        await this.init();
        const config = new WebConfiguration(new MockController(), "../templates/MIDICaptain Nano 4");
        
        await config.init(this.pyswitch, "../");
        const parser = config.parser;

        const input1 = await parser.input(1);
        input1.set_actions(
            [
                action
            ],
            hold
        );
        
        const clients = await parser.getAvailableActions();

        function searchAction(name) {
            for (const client of clients) {
                if (client.client != action.client) continue;
                for (const action2 of client.actions) {
                    if (action2.name == name) return action2;
                }
            }
            throw new Error();
        }

        const action2 = searchAction(name);

        const actions = await input1.actions(hold);
        const current = actions[0];
        
        const meta = action2.meta;

        expect(meta.getDisplayName()).toBe(expNameDefault);
        expect(meta.getDisplayName(current)).toBe(expNameCurrent);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    // async removeAction() {        
    //     await this.init();
    //     const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-default");
        
    //     const parser = await config.parser(this.pyswitch);
    //     expect(parser).toBeInstanceOf(KemperParser);

    //     // Remove from switch 2
    //     async function remove(index) {
    //         const input = await parser.input(25);
    //         const actions = await input.actions(false);
    //         await actions[index].remove();
    //     }

    //     await remove(1);

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [
    //             { 
    //                 name: "BANK_UP",
    //                 arguments: [
    //                     {
    //                         name: "display",
    //                         value: "DISPLAY_HEADER_2"
    //                     }
    //                 ] 
    //             },
    //             { 
    //                 name: "RIG_UP",
    //                 arguments: [
    //                     {
    //                         name: "some",
    //                         value: "val"
    //                     },
    //                     {
    //                         name: "numb",
    //                         value: '78'
    //                     },
    //                     {
    //                         name: "large",
    //                         value: '{"d":{"e":{"f":8}}}'
    //                     },
    //                     {
    //                         name: "arr",
    //                         value: '[{"f": 8, "j": [3, 5,6]}, None, "g"]'
    //                     }
    //                 ] 
    //             }
    //         ] 
    //     });

    //     await remove(0);

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [
    //             { 
    //                 name: "RIG_UP",
    //                 arguments: [
    //                     {
    //                         name: "some",
    //                         value: "val"
    //                     },
    //                     {
    //                         name: "numb",
    //                         value: '78'
    //                     },
    //                     {
    //                         name: "large",
    //                         value: '{"d":{"e":{"f":8}}}'
    //                     },
    //                     {
    //                         name: "arr",
    //                         value: '[{"f": 8, "j": [3, 5,6]}, None, "g"]'
    //                     }
    //                 ] 
    //             }
    //         ] 
    //     });

    //     await remove(0);

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [] 
    //     });

    //     // Check if everything else is still in place
    //     await this.#testAction(parser, {
    //         port: 1,
    //         actions: [{
    //             name: "RIG_UP",
    //             arguments: [
    //                 {
    //                     name: "display",
    //                     value: "DISPLAY_HEADER_1"
    //                 },
    //                 {
    //                     name: "text",
    //                     value: '"Rig up"'
    //                 }
    //             ]
    //         }]
    //     });

    //     await this.#testAction(parser, {
    //         port: 9,
    //         actions: [{ 
    //             name: "RIG_DOWN",
    //             arguments: [
    //                 {
    //                     name: "display",
    //                     value: "DISPLAY_FOOTER_1"
    //                 },
    //                 {
    //                     name: "text",
    //                     value: '"Rig dn"'
    //                 }
    //             ]
    //         }] 
    //     });

    //     await this.#testAction(parser, {
    //         port: 10,
    //         actions: [{ 
    //             name: "BANK_DOWN",
    //             arguments: [
    //                 {
    //                     name: "display",
    //                     value: "DISPLAY_FOOTER_2"
    //                 }
    //             ] 
    //         }] 
    //     });
    // }

    // async removeActionHold() {        
    //     await this.init();
    //     const config = new WebConfiguration(new MockController(), "data/test-presets/remove-actions-hold");
        
    //     const parser = await config.parser(this.pyswitch);
    //     expect(parser).toBeInstanceOf(KemperParser);

    //     // Remove from switch 2
    //     async function remove(index) {
    //         const input = await parser.input(25);
    //         const actions = await input.actions(true);
    //         await actions[index].remove();
    //     }

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [
    //             {
    //                 name: "BANK_UP",
    //                 arguments: []
    //             }
    //         ],
    //         actionsHold: [
    //             { 
    //                 name: "TUNER_MODE",
    //                 arguments: [
    //                     {
    //                         name: "display",
    //                         value: "DISPLAY_HEADER_2"
    //                     }
    //                 ] 
    //             },
    //             { 
    //                 name: "BANK_UP",
    //                 arguments: [] 
    //             },
    //             { 
    //                 name: "BANK_DOWN",
    //                 arguments: [] 
    //             }
    //         ] 
    //     });

    //     await remove(1);

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [
    //             {
    //                 name: "BANK_UP",
    //                 arguments: []
    //             }
    //         ],
    //         actionsHold: [
    //             { 
    //                 name: "TUNER_MODE",
    //                 arguments: [
    //                     {
    //                         name: "display",
    //                         value: "DISPLAY_HEADER_2"
    //                     }
    //                 ] 
    //             },
    //             { 
    //                 name: "BANK_DOWN",
    //                 arguments: [] 
    //             }
    //         ] 
    //     });

    //     await remove(0);

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [
    //             {
    //                 name: "BANK_UP",
    //                 arguments: []
    //             }
    //         ],
    //         actionsHold: [
    //             { 
    //                 name: "BANK_DOWN",
    //                 arguments: [] 
    //             }
    //         ] 
    //     });

    //     await remove(0);

    //     await this.#testAction(parser, {
    //         port: 25,
    //         actions: [
    //             {
    //                 name: "BANK_UP",
    //                 arguments: []
    //             }
    //         ],
    //         actionsHold: [] 
    //     });
    // }

    // async addActionNoIndex() {        
    //     await this.init();
    //     const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-default");
        
    //     const parser = await config.parser(this.pyswitch);
    //     expect(parser).toBeInstanceOf(KemperParser);

    //     // Add to switch 1
    //     async function add(action) {
    //         const input = await parser.input(1);
    //         await input.add_action(action, false);
    //     }

    //     await add({
    //         name: "FOO_ACTION",
    //         arguments: [
    //             {
    //                 name: "param1",
    //                 value: '"StringValue"'
    //             },
    //             {
    //                 name: "param2",
    //                 value: 'NameValue'
    //             },
    //             {
    //                 name: "param3",
    //                 value: '789'
    //             },
    //             {
    //                 name: "param4",
    //                 value: '{"ff":[{4:6}, "hk"]}'
    //             },
    //         ]
    //     });

    //     await this.#testAction(parser, {
    //         port: 1,
    //         actions: [
    //             {
    //                 name: "RIG_UP",
    //                 arguments: [
    //                     {
    //                         name: "display",
    //                         value: "DISPLAY_HEADER_1"
    //                     },
    //                     {
    //                         name: "text",
    //                         value: '"Rig up"'
    //                     }
    //                 ]
    //             },
    //             {
    //                 name: "FOO_ACTION",
    //                 arguments: [
    //                     {
    //                         name: "param1",
    //                         value: '"StringValue"'
    //                     },
    //                     {
    //                         name: "param2",
    //                         value: 'NameValue'
    //                     },
    //                     {
    //                         name: "param3",
    //                         value: '789'
    //                     },
    //                     {
    //                         name: "param4",
    //                         value: '{"ff":[{4:6}, "hk"]}'
    //                     },
    //                 ]
    //             }
    //         ]
    //     });
    // }

    // async addActionWithIndex() {        
    //     await this.init();
    //     const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-default");
        
    //     const parser = await config.parser(this.pyswitch);
    //     expect(parser).toBeInstanceOf(KemperParser);

    //     // Add to switch 1
    //     async function add(action, index) {
    //         const input = await parser.input(1);
    //         await input.add_action(action, false, index);

    //         // console.log((await parser.source()).get("inputs_py"));
    //     }

    //     await add({
    //         name: "FOO_ACTION",
    //         arguments: [
    //             {
    //                 name: "param1",
    //                 value: '"StringValue"'
    //             },
    //             {
    //                 name: "param2",
    //                 value: 'NameValue'
    //             },
    //             {
    //                 name: "param3",
    //                 value: '789'
    //             },
    //             {
    //                 name: "param4",
    //                 value: '{"ff":[{4:6}, "hk"]}'
    //             },
    //         ]
    //     }, 0);

    //     await this.#testAction(parser, {
    //         port: 1,
    //         actions: [                
    //             {
    //                 name: "FOO_ACTION",
    //                 arguments: [
    //                     {
    //                         name: "param1",
    //                         value: '"StringValue"'
    //                     },
    //                     {
    //                         name: "param2",
    //                         value: 'NameValue'
    //                     },
    //                     {
    //                         name: "param3",
    //                         value: '789'
    //                     },
    //                     {
    //                         name: "param4",
    //                         value: '{"ff":[{4:6}, "hk"]}'
    //                     },
    //                 ]
    //             },
    //             {
    //                 name: "RIG_UP",
    //                 arguments: [
    //                     {
    //                         name: "display",
    //                         value: "DISPLAY_HEADER_1"
    //                     },
    //                     {
    //                         name: "text",
    //                         value: '"Rig up"'
    //                     }
    //                 ]
    //             }
    //         ]
    //     });
    // }

    // async addActionHoldNoIndex() {        
    //     await this.init();
    //     const config = new WebConfiguration(new MockController(), "data/test-presets/get-inputs-default");
        
    //     const parser = await config.parser(this.pyswitch);
    //     expect(parser).toBeInstanceOf(KemperParser);

    //     // Add to switch 1
    //     async function add(action) {
    //         const input = await parser.input(1);
    //         await input.add_action(action, true);
    //     }

    //     await add({
    //         name: "FOO_ACTION",
    //         arguments: [
    //             {
    //                 name: "param1",
    //                 value: '"StringValue"'
    //             },
    //             {
    //                 name: "param2",
    //                 value: 'NameValue'
    //             },
    //             {
    //                 name: "param3",
    //                 value: '789'
    //             },
    //             {
    //                 name: "param4",
    //                 value: '{"ff":[{4:6}, "hk"]}'
    //             },
    //         ]
    //     });

    //     await this.#testAction(parser, {
    //         port: 1,
    //         actions: [
    //             {
    //                 name: "RIG_UP",
    //                 arguments: [
    //                     {
    //                         name: "display",
    //                         value: "DISPLAY_HEADER_1"
    //                     },
    //                     {
    //                         name: "text",
    //                         value: '"Rig up"'
    //                     }
    //                 ]
    //             }
    //         ],
    //         actionsHold: [
    //             {
    //                 name: "FOO_ACTION",
    //                 arguments: [
    //                     {
    //                         name: "param1",
    //                         value: '"StringValue"'
    //                     },
    //                     {
    //                         name: "param2",
    //                         value: 'NameValue'
    //                     },
    //                     {
    //                         name: "param3",
    //                         value: '789'
    //                     },
    //                     {
    //                         name: "param4",
    //                         value: '{"ff":[{4:6}, "hk"]}'
    //                     },
    //                 ]
    //             }
    //         ]
    //     });
    // }
    
    //////////////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////////////
        
    /**
     * Tests a single action, controlled by the config object:
     * {
     *      port,
     *      client,             // Client ID
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
     *      holdTimeMillis:
     *      holdRepeat:
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

                if (expAction.assign) {
                    expect(action.assign).toBe(expAction.assign);
                }
                
                if (action.client != "local") expect(action.client).toBe(config.client);

                if (expAction.arguments) {
                    expect(JSON.parse(action.arguments())).toEqual(expAction.arguments);
                }
            }
        }

        if (config.actions) {
            await test(false, config.actions);
        }
        if (config.actionsHold) {
            await test(true, config.actionsHold);
        }

        if (config.holdTimeMillis) {
            expect(input.hold_time_millis()).toBe(config.holdTimeMillis)
        }

        if (config.holdRepeat) {
            expect(input.hold_repeat()).toBe(config.holdRepeat)
        }
    }
}