/**
 * MIDI Monitor tab
 */
class MidiMonitor extends Tab {

    #monitorElement = null;
    #maxNumMessages = 100;
    #run = false;
    #virtualClients = [];
    #controller = null;
    #runButton = null;
    
    #exclude = null;           // List of messages to ignore

    #hex = false;
    #showValues = true;
    #showBytes = false;

    #bytesButton = null;
    #valuesButton = null;
    #hexButton = null;
    #excludeDisplay = null;

    #state = null;
    
    constructor(controller, tabName) {
        let monitorContainer = null;
        super(
            monitorContainer = $('<div class="midi-monitor-container" />'), 
            tabName
        );

        this.#controller = controller;
        this.#state = new LocalState("midi-monitor");
        this.#run = !!this.#state.get("run");
        this.#hex = !!this.#state.get("hex");

        if (this.#state.has("bytes")) {
            this.#showBytes = !!this.#state.get("bytes");
        }

        if (this.#state.has("values")) {
            this.#showValues = !!this.#state.get("values");
        }

        const that = this;
        monitorContainer.append(
            $('<div class="midi-controls" />').append(
                this.#excludeDisplay = $('<div class="midi-exclude" />'),

                $('<div class="midi-buttons" />').append(
                    // Run/Pause monitor
                    this.#runButton = this.#generateButton({
                        onClick: function() {
                            if (that.#run) that.#stop();
                            else that.#resume();
                        },
                        classes: this.#run ? "fas fa-pause" : "fas fa-play",
                        tooltip: "Pause/resume the MIDI monitor",
                        active: true
                    }),

                    // Clear monitor
                    this.#generateButton({
                        onClick: function() {
                            that.#clear();
                        },
                        classes: "fas fa-ban",
                        tooltip: "Clear the MIDI monitor",
                        active: true
                    }),

                    // Bytes button
                    this.#bytesButton = this.#generateButton({
                        onClick: function() {
                            that.#setShowBytes(!that.#showBytes);
                        },
                        text: "bytes",
                        active: this.#showBytes,
                        tooltip: "Show/hide message raw bytes"
                    }),
                    
                    // Values button
                    this.#valuesButton = this.#generateButton({
                        onClick: function() {
                            that.#setShowValues(!that.#showValues);
                        },
                        text: "values",
                        active: this.#showValues,
                        tooltip: "Show/hide interpreted value"
                    }),

                    // Hex button
                    this.#hexButton = this.#generateButton({
                        onClick: function() {
                            that.#setHexMode(!that.#hex);
                        },
                        text: "hex",
                        active: this.#hex,
                        tooltip: "Toggle hexadecimal display"
                    })
                )
            ),

            $('<div class="midi-monitor" />').append(
                this.#run ? null :
                $('<div class="teaser" />')
                .text("Click here to start monitoring...")
                .on('click', function(e) {
                    e.stopPropagation();
                    that.#resume();
                    $(this).remove();
                }),

                $('<table />').append(
                    this.#monitorElement = $('<tbody />')
                )
            )
            .on('click', function() {
                try {
                    that.#stop();

                } catch (e) {
                    that.#controller.handle(e);
                }
            })
        )

        controller.pyswitch.setMidiMonitor({
            monitorInput: function(message) {
                that.addMessage({
                    message: message,
                    direction: "in"
                })
            },
            monitorOutput: function(message) {
                that.addMessage({
                    message: message,
                    direction: "out"
                })
            }
        });

        this.#exclude = this.#state.get("exclude") || [];
        this.#updateExcludeDisplay();
    }

    deactivate() {
        super.deactivate();
        this.#stop();
    }

    /**
     * Rebuilds the exclude messages display
     */
    #updateExcludeDisplay() {
        this.#excludeDisplay
            .empty()
            .append(
                $('<div />').text(this.#exclude.length ? "Ignored messages:" : "No ignored messages")
            )
            .append(
                $('<table />').append(
                    $('<tbody />').append(
                        this.#exclude.map((item) =>
                            $('<tr />').append(
                                $('<td />').append(
                                    this.#generateExcludeButtons(item)
                                ),

                                $('<td />').append(
                                    this.#generateExcludeMessage(item)
                                )
                            )
                        )
                    )
                )
            );
    }

    #generateExcludeButtons(ex) {
        const that = this;
        return $('<div class="message-button fas fa-trash" data-toggle="tooltip" title="Remove" />')
        .on('click', function() {
            try {
                that.#includeMessage(ex);

            } catch (e) {
                that.#controller.handle(e);
            }
        })
    }

    /**
     * Returns the DOM for an exclude message
     */
    #generateExcludeMessage(ex) {
        if (ex.props) {
            return ex.props.name;
        }

        if (ex.message) {
            return this.#formatMidiMessageBytes(ex.message, false);
        }

        console.warn("MIDI Monitor: Unknown exclude message spec: ", ex);
        return null;
    }

    /**
     * Generates a button with text
     * 
     * {
     *      text
     *      onClick
     *      tooltip
     *      active
     *      classes
     * }
     */
    #generateButton(options) {
        const that = this;
        return $('<span /data-toggle="tooltip" title="' + options.tooltip + '" />')
            .text(options.text ? options.text : null)
            .toggleClass("inactive", !options.active)
            .addClass(options.classes ? options.classes : null)
            .on('click', async function() {
                try {
                    await options.onClick(options);

                } catch (e) {
                    that.#controller.handle(e);
                }
            });
    }

    /**
     * Must be called before usage
     */
    async initMonitor() {
        const clients = await Client.getAvailable();

        for (const client of clients) {
            const virtualClient = await client.getVirtualClient();
            if (!virtualClient) continue;

            this.#virtualClients.push(virtualClient);
        }
    }

    destroy() {
        this.#monitorElement.empty();
    }

    /**
     * Resume showing messages
     */
    #resume() {   
        if (!this.#run) {
            this.addComment("resumed");
        }

        this.#run = true;
        
        this.#runButton.addClass('fa-pause');
        this.#runButton.removeClass('fa-play');

        this.#state.set("run", true);
    }

    /**
     * Stop showing messages
     */
    #stop() {
        if (this.#run) {
            this.addComment("stopped");
        }
    
        this.#run = false;
        
        this.#runButton.removeClass('fa-pause');
        this.#runButton.addClass('fa-play');

        this.#state.set("run", false);
    }

    /**
     * Show bytes
     */
    #setShowBytes(show) {
        this.#showBytes = show;
        this.#monitorElement.find('.message-bytes').toggle(show);
        this.#bytesButton.toggleClass("inactive", !show);

        this.#state.set("bytes", show);
    }

    /**
     * Show values
     */
    #setShowValues(show) {
        this.#showValues = show;
        this.#monitorElement.find('.message-values').toggle(show);
        this.#valuesButton.toggleClass("inactive", !show);

        this.#state.set("values", show);
    }

    /**
     * Set hex display on or off
     */
    #setHexMode(on) {
        this.#hex = on;
        this.#hexButton.toggleClass("inactive", !on);

        this.#state.set("hex", on);
    }

    /**
     * {
     *      direction: "in" or "out"
     *      message: Data of the MIDI message
     * }
     */
    addMessage(options) {
        if (!this.#run) return;

        if (!options.message) options.message = "NO MESSAGE";

        const props = this.#messageProperties(options.message);

        if (this.#doExclude({
            message: options.message, 
            props: props
        })) return;

        let tr = null;
        this.#monitorElement.append(
            tr = $('<tr class="midi-message midi-message-' + options.direction + '" />').append(
                // Exclude Button
                this.#generateExcludeButton({
                    message: Array.from(options.message),
                    props: props
                }),

                // Direction (in/out)
                $('<td />').append(
                    options.direction
                ),

                // Name, if any
                $('<td />').append(
                    props ? props.name : ""
                ),

                // Value
                $('<td />').append(
                    $('<span class="message-values" />').text(
                        this.#formatMidiMessageValue(props, options.message)
                    )
                    .toggle(this.#showValues),
                ),

                // Bytes
                $('<td />').append(
                    $('<span class="message-bytes" />').text(
                        this.#formatMidiMessageBytes(options.message)
                    )
                    .toggle(this.#showBytes),
                )
            )
        )

        tr[0].scrollIntoView(false);

        this.#cleanup();
    }

    /**
     * Add a comment
     */
    addComment(comment) {
        let tr = null;
        this.#monitorElement.append(
            tr = $('<tr class="comment" />').append(
                // Comment
                $('<td colspan="5"/>').text(comment)
            )
        )

        tr[0].scrollIntoView(false);

        this.#cleanup();
    }

    /**
     * Decide if the message or comment has to be excluded
     */
    #doExclude(data) {
        for (const e of this.#exclude) {
            // Name
            if (data.props && e.props) {
                if (e.props.name && e.props.name == data.props.name) return true;
            } else {
                // Bytes
                if (data.message && Tools.compareArrays(data.message.slice(0, e.message.length), e.message)) return true;
            }
        }
        return false;
    }

    /**
     * Generate the exclude button
     * 
     * {
     *      name,       // Only for messages
     *      message,    // Only for messages
     *      comment     // Only for comments
     * }
     */
    #generateExcludeButton(props) {
        const that = this;
        return $('<td />').append(
            $('<div class="message-button fas fa-ban" data-toggle="tooltip" title="Ignore message" />')
            .on('click', function() {
                try {
                    that.#excludeMessage(props)

                } catch (e) {
                    that.#controller.handle(e);
                }
            })
        )
    }

    /**
     * Exclude a message (options see #generateExcludeButton())
     */
    #excludeMessage(props) {
        for (const e of this.#exclude) {
            if (e.name == props.name && 
                Tools.compareArrays(e.message, props.message)) return;
        }
        this.#exclude.push(props);

        this.#state.set("exclude", this.#exclude);
        this.#updateExcludeDisplay();
    }

    /**
     * Include a message (options see #generateExcludeButton())
     */
    #includeMessage(props) {
        this.#exclude = this.#exclude.filter((e) => 
            e.name != props.name || 
            !Tools.compareArrays(e.message, props.message)
        );
        
        this.#state.set("exclude", this.#exclude);
        this.#updateExcludeDisplay();
    }

    /**
     * Output formatting for the raw data bytes
     */
    #formatMidiMessageBytes(message, pad = true) {
        const that = this;
        function convert(v) {
            if (!that.#hex) return v;
            return v.toString(16).padStart(2, "0");
        }
        return Array.from(message)
            .map((item) => pad ? ("" + convert(item)).padStart(3, " ") : ("" + convert(item)))
            .join(", ")
    }

    /**
     * Returns the parsed value of the message
     */
    #formatMidiMessageValue(props, message) {
        if (!props || !props.hasOwnProperty("value")) return this.#formatMidiMessageBytes(message);

        if (Array.isArray(props.value)) {
            return this.#formatMidiMessageBytes(props.value, false)
        }
        
        return props.value;
    }

    /**
     * Tries to determine a readable name for the message
     */
    #messageProperties(message) {
        // Try all virtual clients
        for (const client of this.#virtualClients) {
            const props = client.getMessageProperties(message);
            if (!props) continue;

            return props;
        }
    }

    /**
     * Clear all messages
     */
    #clear() {
        this.#monitorElement.empty();
    }

    /**
     * Remove old messages
     */
    #cleanup() {
        while (this.#monitorElement.children('tr').length > this.#maxNumMessages) {
            this.#monitorElement.children('tr').first().remove();
        }
    }
}