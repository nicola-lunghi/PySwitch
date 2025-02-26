import libcst
import json 

from .inputs.Input import Input
from .inputs.InputReplacer import InputReplacer
from .misc.RemoveUnusedImportTransformer import RemoveUnusedImportTransformer
from .misc.AddImportsTransformer import AddImportsTransformer
from .misc.AssignmentExtractor import AssignmentExtractor
from .misc.ImportExtractor import ImportExtractor
from .misc.ParameterValueExtractor import ParameterValueExtractor

class PySwitchParser:

    def __init__(self, hw_import_path, available_clients_json):
        self.__js_parser = None
        self.__hw_import_path = hw_import_path       
        self.__csts = None
        self.clients = json.loads(available_clients_json)

        self.__available_actions = None
        self.__available_mappings = None

        self.__displays = None
        # self.messages = []

    # Has to be called before usage
    def init(self, js_parser):
        self.__js_parser = js_parser.to_py()

    # Set the parser data from source code
    def from_source(self, inputs_py, display_py):
        self.__csts = {
            "inputs_py": libcst.parse_module(inputs_py),
            "display_py": libcst.parse_module(display_py)
        }

        self.__displays = None

        # self._check()

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
    
    # Returns a JSON encoded list of assignments in display.py
    def displays(self):
        if self.__displays:
            return self.__displays
            
        self.__displays = json.dumps(AssignmentExtractor().get(self.__csts["display_py"]))

        return self.__displays

    ########################################################################################

    # Update the CSTs from the passed input. Only called internally.
    def update_input(self, input, noUpdate = False):
        if not self.__csts:
            raise Exception("No data loaded")

        visitor = InputReplacer(input)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)

        # self._check()

        if not noUpdate:
            self.__js_parser.updateConfig()

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
            self.__available_actions = self._generate_action_imports()

        if not self.__available_mappings:
            self.__available_mappings = self._generate_mapping_imports()    
        
        display_assignments = [
            { 
                "name": assign, 
                "importPath": "display" 
            } 
            for assign in AssignmentExtractor().get(self.__csts["display_py"])
        ]

        # Add all imports
        visitor = AddImportsTransformer(self.__available_actions + self.__available_mappings + display_assignments)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)
            
    # Generates all imports for actions
    def _generate_action_imports(self):
        # Load actions definitions from file
        with open('definitions/actions.json') as f: available_actions_json = f.read()
        
        clients = json.loads(available_actions_json)
        actions = []

        for client in clients:
            actions = actions + client["actions"]

        # Add additional potentially needed imports besides the actions.
        return actions + [
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
            },

            # PushButtonAction
            {
                "name": "PushButtonAction",
                "importPath": "pyswitch.controller.actions"
            },

            # Effect slot definitions
            {
                "name": "KemperEffectSlot",
                "importPath": "pyswitch.clients.kemper"
            },
        ]
    
    # Generates all imports for mappings
    def _generate_mapping_imports(self):
        # Load actions definitions from file
        with open('definitions/mappings.json') as f: available_mappings_json = f.read()
        
        clients = json.loads(available_mappings_json)
        mappings = []

        for client in clients:
            mappings = mappings + client["mappings"]

        return mappings

    # Determine the client for an Action instance
    def determine_import_statement(self, action):
        visitor = ImportExtractor(action.name)
        self.__csts["inputs_py"].visit(visitor)
        return visitor.result

    #######################################################################################

    # # Checks the current CSTs and collects messages
    # def _check(self):
    #     pass
    #     self.messages = []

    #     self._check_double_displays()

    # # Check for DisplayLabels assigned twice
    # def _check_double_displays(self):
    #     displays = self.displays()

    #     for display in displays:
    #         visitor = ParameterValueExtractor(display)
    #         self.__csts["inputs_py"].visit(visitor)

    #         if len(visitor.result) > 1:
    #             self.messages.append(
    #                 {

    #                 }
    #             )

