class CodeEditor extends Tab {

    #editor = null;
    #dirty = false;
    
    constructor(name, content = "") {
        super($('<div class="code-editor" />'), name);
        this.#init();

        this.setContent(content);
    }

    /**
     * Create the editor instance
     */
    #init() {
        const that = this;

        // Editor
		this.#editor = CodeMirror(this.container[0], {
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
                        
        //                 that.#ui.save();
                        
        //                 break;		        
		//         }
		//     }
		// });
	}

    #setDirty() {
        this.#dirty = true;
    }

    isDirty() {
        return this.#dirty;
    }

    getContent() {
       return this.#editor.getValue();
    }

    setContent(content) {
        this.#editor.setValue(content); 
        this.#dirty = false;       
    }
}