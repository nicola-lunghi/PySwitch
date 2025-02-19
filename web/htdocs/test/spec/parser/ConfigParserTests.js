class ConfigParserTests extends TestBase {

    async minimal() {
        await this.init();
        const config = new MockConfiguration("", "");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        await expectAsync(parser.input(1)).toBeRejected();
        await expectAsync(parser.input(25)).toBeRejected();
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    async getInputActionsDefault() {
        await this.init();
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
        await this.init();
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
            ]
        );

        await this.#replaceActions(
            9, 
            [
                { 
                    name: "SOME_ACTION",
                    arguments: [] 
                }
            ]
        );

        await this.#replaceActions(
            9, 
            []
        );
    }

    async #replaceActions(port, actions) {
        await this.init();
        const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        const input = await parser.input(port);
        
        // Replace actions
        await input.set_actions(actions)

        // console.log((await parser.source()).get("inputs_py"));
        // expect(1).toBe(2)

        await this.#testAction(parser, {
            port: port,
            actions: actions
        });

        // Replace actionsHold
        await input.set_actions(actions, true)

        await this.#testAction(parser, {
            port: port,
            actions: actions,
            actionsHold: actions
        });
    }
    
    ///////////////////////////////////////////////////////////////////////////////////////////

    async addOneImport() {
        await this.init();
        const config = new WebConfiguration("../templates/MIDI Captain Nano 4");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        const input1 = await parser.input(1);
        
        // Add first actions available
        const actions = await parser.getAvailableActions("../");

        await input1.set_actions(
            [
                this.#composeAction(actions[0])
            ]
        );
        
        // console.log((await parser.config.get()).inputs_py);

        // Test with PySwitch
        await this.runner.run(config)
    }

    async addAllImports() {
        await this.init();
        const config = new WebConfiguration("../templates/MIDI Captain Nano 4");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        const input1 = await parser.input(1);
        
        // Add all actions available
        const actions = await parser.getAvailableActions("../");

        const that = this;
        await input1.set_actions(
            actions.map(
                function (item) { 
                    return that.#composeAction(item)
                }
            ).filter((item) => item != null)
        );
        
        // console.log((await parser.config.get()).inputs_py);

        // Test with PySwitch
        await this.runner.run(config)
    }

    async addDisplayImports() {
        await this.init();
        const config = new WebConfiguration("../templates/MIDI Captain Nano 4");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        const input1 = await parser.input(1);
        
        await input1.set_actions(
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
        await this.runner.run(config)
    }

    /**
     * Helper for import tests: Returns an action definition for setting, 
     * from a given action definition loaded by the parser.
     */
    #composeAction(item) {
        return {
            name: item.name,
            arguments: item.parameters.map(
                function (param) {
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
                arguments: []
            },
            "Bank Up",   // Default
            "Bank Up"    // With actual value
        );

        await this.#checkActionMeta(
            "BANK_DOWN",
            {
                name: "BANK_DOWN",
                arguments: []
            },
            "Bank Down",   // Default
            "Bank Down"    // With actual value
        );
    }

    async displayNameRigSelect() {
        await this.#checkActionMeta(
            "RIG_SELECT",
            {
                name: "RIG_SELECT",
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
            "Select Rig 1",   // Default
            "Select Rig 2"    // With actual value
        )
    }

    async displayNameRigSelectToggle() {
        await this.#checkActionMeta(
            "RIG_SELECT",
            {
                name: "RIG_SELECT",
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
            "Select Rig 1",      // Default
            "Toggle Rigs 2/4"    // With actual value
        )        
    }

    async #checkActionMeta(name, action, expNameDefault, expNameCurrent) {
        await this.#doCheckActionMeta(name, action, expNameDefault, expNameCurrent, false);
        await this.#doCheckActionMeta(name, action, expNameDefault, expNameCurrent, true);
    }

    async #doCheckActionMeta(name, action, expNameDefault, expNameCurrent, hold) {
        await this.init();
        const config = new WebConfiguration("../templates/MIDI Captain Nano 4");
        
        const parser = await config.parser(this.pyswitch);
        expect(parser).toBeInstanceOf(KemperParser);

        const input1 = await parser.input(1);
        
        await input1.set_actions(
            [
                action
            ],
            hold
        );
        
        const available = await parser.getAvailableActions("../");

        function searchAction(name) {
            for (const action of available) {
                if (action.name == name) return action;
            }
        }

        const action2 = searchAction(name);

        const actions = await input1.actions(hold);
        const current = {
            name: actions[0].name,
            arguments: JSON.parse(actions[0].arguments())
        };
        
        const meta = new Meta(action2);

        expect(meta.getDisplayName()).toBe(expNameDefault);
        expect(meta.getDisplayName(current)).toBe(expNameCurrent);
    }

    ///////////////////////////////////////////////////////////////////////////////////////////

    // async removeAction() {        
    //     await this.init();
    //     const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
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
    //     const config = new WebConfiguration("data/test-presets/remove-actions-hold");
        
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
    //     const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
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
    //     const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
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
    //     const config = new WebConfiguration("data/test-presets/get-inputs-default");
        
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
}