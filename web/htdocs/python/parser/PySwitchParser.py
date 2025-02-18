import libcst
import json 

from .inputs.Input import Input
from .inputs.InputReplacer import InputReplacer
from .misc.RemoveUnusedImportTransformer import RemoveUnusedImportTransformer
from .misc.AddImportsTransformer import AddImportsTransformer

class PySwitchParser:

    def __init__(self, hw_import_path):
        self.__js_parser = None
        self.__hw_import_path = hw_import_path       
        self.__csts = None
        self.__available_actions = None

    # Has to be called before usage
    def init(self, js_parser):
        self.__js_parser = js_parser.to_py()

    # Set the parser data from source code
    def from_source(self, inputs_py, display_py):
        self.__csts = {
            "inputs_py": libcst.parse_module(inputs_py),
            "display_py": libcst.parse_module(display_py)
        }

    # Returns a dict holding the sources for the current configuration
    def to_source(self):
        if not self.__csts:
            raise Exception("No data loaded")
        
        self._add_all_possible_imports()

        self._remove_unused_imports()

        return {
            "inputs_py": self.__csts["inputs_py"].code,
            "display_py": self.__csts["display_py"].code
        }

    # Returns the visitor/handler of the input assigned to the port given
    def input(self, port):
        if not self.__csts:
            raise Exception("No data loaded")
        
        visitor = Input(self, self.__hw_import_path, port)
        self.__csts["inputs_py"].visit(visitor)
        return visitor if visitor.result != None else None
    
    ########################################################################################

    # Update the CSTs from the passed input. Only called internally.
    def update_input(self, input):
        if not self.__csts:
            raise Exception("No data loaded")

        visitor = InputReplacer(input)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)
        
        self.__js_parser.update_config()

    ########################################################################################
        
    # Remove unused imports on all files. Does no config update!
    def _remove_unused_imports(self):
        self._remove_unused_import_for_file("inputs_py")
        self._remove_unused_import_for_file("display_py")

    def _remove_unused_import_for_file(self, file):
        wrapper = libcst.metadata.MetadataWrapper(self.__csts[file])
        visitor = RemoveUnusedImportTransformer(wrapper)
        self.__csts[file] = wrapper.module.visit(visitor)

    ########################################################################################

    # Adds all possible imports (actions etc.) Does no config update!
    def _add_all_possible_imports(self):
        if not self.__available_actions:
            # Load actions definitions from file
            with open('definitions/actions.json') as f: available_actions_json = f.read()
            
            self.__available_actions = json.loads(available_actions_json) + [
                # Additional imports: Colors
                {
                    "name": "Colors",
                    "importPath": "pyswitch.misc"
                },
                {
                    "name": "DEFAULT_SWITCH_COLOR",
                    "importPath": "pyswitch.misc"
                },

                # RIG_SELECT display modes
                {
                    "name": "RIG_SELECT_DISPLAY_CURRENT_RIG",
                    "importPath": "pyswitch.clients.kemper.actions.rig_select"
                },
                {
                    "name": "RIG_SELECT_DISPLAY_TARGET_RIG",
                    "importPath": "pyswitch.clients.kemper.actions.rig_select"
                },

                # Callbacks
                {
                    "name": "BinaryParameterCallback",
                    "importPath": "pyswitch.controller.callbacks"
                }
            ]

        visitor = AddImportsTransformer(self.__available_actions)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)
            

