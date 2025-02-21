class CodeEditor {

    #editorElement = null;
    #editor = null;
    #dirty = false;
    
    constructor(editorElement) {
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
            gutters: ["CodeMirror-lint-markers"],
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
                        
        //                 that.#ui.save();
                        
        //                 break;		        
		//         }
		//     }
		// });
	}

    #setDirty() {
        //this.#ui.setDirty();
        this.#dirty = true;
    }

    isDirty() {
        return this.#dirty;
    }

    show() {
        $(this.#editorElement).show();
    }

    hide() {
        $(this.#editorElement).hide();
    }

    getContent() {
       return this.#editor.getValue();
    }

    setContent(content) {
        this.#editor.setValue(content); 
        this.#dirty = false;       
    }
}