class CodeEditor extends Tab {

    #editor = null;
    #dirty = false;
    #editorElement = null;
    
    constructor(name) {
        let editorElement = null;
        super(
            $('<div class="code-editor-container" />').append(
                // Editor content
                 editorElement = $('<div class="code-editor" />')
            ), 
            name
        );

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
	 * Global key shortcuts
	 */
	#initGlobalShortcuts() {
		// const that = this;
		
		// // CTRL-S key to save
		// $(window).on('keydown', async function(event) {
		//     if (event.ctrlKey || event.metaKey) {
		//         switch (String.fromCharCode(event.which).toLowerCase()) {
        //             case 's':
        //                 event.preventDefault();
                        
        //                 // that.#ui.save();
                        
        //                 break;		        
		//         }
		//     }
		// });
	}

    #setDirty() {
        this.#dirty = true;
    }

    refresh() {
        const content = this.getContent();
        this.setContent(content);
    }

    isDirty() {
        return this.#dirty;
    }

    getContent() {
       return this.#editor.getValue();
    }

    setContent(content, dontUseTimeout = false) {
        if (dontUseTimeout) {
            this.#editor.setValue(content); 
            this.#dirty = false;           
        } else {
            const that = this;
            setTimeout(function() {
                that.setContent(content, true);
            }, 0);            
        }
    }
}