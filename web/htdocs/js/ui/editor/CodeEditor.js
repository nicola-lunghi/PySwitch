/**
 * Code editor tab
 */
class CodeEditor extends Tab {

    #configFieldName = null;    // Name of the Configuration file (display_py for example)
    #editor = null;             // CodeMirror instance
    #dirty = false;             // Dirty state
    #editorElement = null;      // Editor container DOM element
    #applyButton = null;        // Apply Button DOM element
    #config = null;             // Configuration instance (set with setConfig())
    #controller = null;
    
    constructor(controller, tabName, configFieldName) {
        let editorElement = null;
        super(
            $('<div class="code-editor-container" />').append(
                // Editor content
                 editorElement = $('<div class="code-editor" />')
            ), 
            tabName
        );

        this.#controller = controller;
        this.#configFieldName = configFieldName;
        this.#editorElement = editorElement;

        this.#init();
    }

    /**
     * Create the editor instance
     */
    #init() {
        const that = this;
        
        // Editor
		this.#editor = CodeMirror(this.#editorElement[0], {
			mode: "python",
            // gutters: ["CodeMirror-lint-markers"],
            lineNumbers: true,
            // lint: {
            //     getAnnotations: function(source/*, options, editor*/) {                    
            //         return (new DemoLinter()).getAnnotations(source);
            //     },
            //     highlightLines: true
            // }
		});

        // Set dirty on change (shows the save button)
        this.#editor.on('change', function(/*obj*/) {
			that.#setDirty();
		});

        this.#initGlobalShortcuts();
    }

    /**
     * Generates custom buttons for the tab, if any
     */
    getButtons() {
        const that = this;

        return [
            this.#applyButton = $('<div class="fas fa-check" data-toggle="tooltip" title="Apply code" />')
            .toggleClass("inactive", !this.isDirty())
            .on('click', async function() {
                try {
                    await that.apply();

                } catch (e) {
                    that.#controller.handle(e);
                }
            })              
        ];
    }

    /**
     * Sets a Configuration instance to get/set code
     */
    async setConfig(config) {
        const content = (await config.get())[this.#configFieldName];
        this.#resetDirtyState();
        this.#setContent(content);
        this.#config = config;
    }
    
    /**
     * Apply changes to the config
     */
    async apply() {
        const that = this;
        await this.#controller.restart({
            message: "none",
            changeCallback: async function() {
                await that.#config.parser.updateFromSource(that.#configFieldName, that.#getContent());

                that.#resetDirtyState();
            }
        });
    }

    /**
	 * Global key shortcuts
	 */
	#initGlobalShortcuts() {
		const that = this;
		
		// CTRL-S key to save
		this.#editorElement.on('keydown', async function(event) {
		    if (event.ctrlKey || event.metaKey) {
		        switch (String.fromCharCode(event.which).toLowerCase()) {
                    case 's':
                        event.preventDefault();
                        
                        await that.apply();
                        
                        break;		        
		        }
		    }
		});
	}

    /**
     * Set the editor dirty
     */
    #setDirty() {
        this.#dirty = true;
        if (this.#applyButton) {
            this.#applyButton.removeClass('inactive');
        }
    }

    /**
     * Reset dirty state
     */
    #resetDirtyState() {
        this.#dirty = false;    
        if (this.#applyButton) {    
            this.#applyButton.addClass('inactive');
        }
    }

    /**
     * Are there unapplied changes?
     */
    isDirty() {
        return this.#dirty;
    }

    /**
     * If dirty, asks the user to confirm the action he wants to take.
     */
    confirmIfDirty() {
        if (!this.isDirty()) return true;
        return confirm(this.name + " has unapplied changes, do you want to discard them?");
    }

    /**
     * Returns the current code
     */
    #getContent() {
       return this.#editor.getValue();
    }

    /**
     * Sets the code, optionally using setTimeout to perform the changes
     * which is sometimes necessary.
     */
    #setContent(content, dontUseTimeout = false) {
        if (dontUseTimeout) {
            const dirtyState = this.isDirty();
            
            this.#editor.setValue(content); 

            if (dirtyState) {
                this.#setDirty();
            }else {
                this.#resetDirtyState();
            }
        } else {
            const that = this;
            setTimeout(function() {
                try {
                    that.#setContent(content, true);

                } catch (e) {
                    that.#controller.handle(e);
                }                
            }, 0);            
        }
    }

    /**
     * Refresh editor element after focus changes. Does not reset dirty state!
     */
    refresh() {
        const content = this.#getContent();
        this.#setContent(content);
    }
}