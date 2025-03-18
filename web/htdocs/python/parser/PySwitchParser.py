import libcst
import json 

from .inputs.Input import Input
from .inputs.InputReplacer import InputReplacer
from .inputs.CreateInputTransformer import CreateInputTransformer

from .display.SplashesExtractor import SplashesExtractor

from .misc.CodeGenerator import CodeGenerator
from .misc.RemoveUnusedImportTransformer import RemoveUnusedImportTransformer
from .misc.AddImportsTransformer import AddImportsTransformer
from .misc.AssignmentNameExtractor import AssignmentNameExtractor
from .misc.AssignmentExtractor import AssignmentExtractor
from .misc.ImportExtractor import ImportExtractor
from .misc.RemoveAssignmentTransformer import RemoveAssignmentTransformer
from .misc.AddAssignmentTransformer import AddAssignmentTransformer
from .misc.ClassNameExtractor import ClassNameExtractor

class PySwitchParser:

    def __init__(self, hw_import_path, available_clients_json):
        self.hw_import_path = hw_import_path       
        self.__js_parser = None
        self.__csts = None
        
        self.clients = json.loads(available_clients_json)

        # Buffers
        self.__available_actions = None
        self.__available_mappings = None
        self.__available_display_imports = None
        
        # self.__pager = None
        # self.__pager_buffer_active = False
        
        self.reset_buffers()

    # Has to be called before usage
    def init(self, js_parser):
        self.__js_parser = js_parser.to_py()

    # Reset buffers
    def reset_buffers(self):
        self.__displays = None
        self.__inputs = {}
        self.__splashes = None

    # Set the parser data from source code
    def from_source(self, inputs_py, display_py):
        self.__csts = {
            "inputs_py": libcst.parse_module(inputs_py),
            "display_py": libcst.parse_module(display_py)
        }

        self.reset_buffers()

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
    def input(self, port, create_if_not_existent = False):
        if not self.__csts:
            raise Exception("No data loaded")
        
        if not create_if_not_existent and port in self.__inputs:
            return self.__inputs[port]
        
        # Try to find the input
        visitor = Input(self, self.hw_import_path, port)
        self.__csts["inputs_py"].visit(visitor)
        ret = visitor if visitor.result != None else None

        if create_if_not_existent and not ret:
            # Create input
            visitor = CreateInputTransformer(self.hw_import_path, port)
            self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)
            
            # Scan again for the input
            visitor = Input(self, self.hw_import_path, port)
            self.__csts["inputs_py"].visit(visitor)
            
            if not visitor.result:
                raise Exception("Error creating input " + repr(port))

            ret = visitor

            
        self.__inputs[port] = ret

        return ret
    
    # Searches for an Assign with the given name and returns its node, or None if not found
    def get_assignment(self, name, file_id):
        assignments = AssignmentExtractor().get(self.__csts[file_id])
        
        for a in assignments:
            if a["name"] == name:
                return a["node"]
            
        return None

    # Adds or replaces the given assignment by name.
    def set_assignment(self, name, call_node, file_id, insert_before_assign = None):
        remover = RemoveAssignmentTransformer(name)
        self.__csts[file_id] = self.__csts[file_id].visit(remover)

        adder = AddAssignmentTransformer(
            name, 
            call_node, 
            insert_before_assign = insert_before_assign, 
            cst = self.__csts[file_id] if not insert_before_assign else None
        )

        self.__csts[file_id] = self.__csts[file_id].visit(adder)

    #######################################################################################

    # Returns a JSON encoded list of assignments in display.py
    def displays(self):
        if self.__displays:
            return self.__displays
            
        if not self.__csts:
            raise Exception("No data loaded")
        
        self.__displays = json.dumps(AssignmentNameExtractor().get(self.__csts["display_py"]))

        return self.__displays
    
    # Returns a proxy to the splashes in display.py
    def splashes(self):
        if self.__splashes:
            return self.__splashes
        
        if not self.__csts:
            raise Exception("No data loaded")
                
        splashes = SplashesExtractor(self, self.__csts["display_py"]).get("Splashes")
        self.__splashes = json.dumps(splashes)
        
        return self.__splashes

    # Replace the splashes in display.py
    def set_splashes(self, splashes):
        if not self.__csts:
            raise Exception("No data loaded")
        
        self.__splashes = None
        self.__displays = None
        
        splashes_node = CodeGenerator(self, "display_py", insert_before_assign = "Splashes").generate(splashes.to_py())
        
        self.set_assignment("Splashes", splashes_node, "display_py")
        
        self.__js_parser.updateConfig()

    ########################################################################################

    # Update the CSTs from the passed input. Only called internally.
    def update_input(self, input, noUpdate = False):
        if not self.__csts:
            raise Exception("No data loaded")

        visitor = InputReplacer(input)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)

        # Reset buffer
        self.__inputs = {}

        if not noUpdate:
            self.__js_parser.updateConfig()

    ########################################################################################
        
    # Remove unused imports on all files. Does no config update!
    def _remove_unused_imports(self):
        self._remove_unused_import_for_file("inputs_py")
        self._remove_unused_import_for_file("display_py")

    def _remove_unused_import_for_file(self, file_id):
        wrapper = libcst.metadata.MetadataWrapper(self.__csts[file_id])
        visitor = RemoveUnusedImportTransformer(wrapper)
        self.__csts[file_id] = wrapper.module.visit(visitor)

    ########################################################################################

    # Adds all possible imports (actions etc.) Does no config update!
    def _add_all_possible_imports(self):
        self._add_all_possible_imports_inputs()
        self._add_all_possible_imports_display()

    def _add_all_possible_imports_inputs(self):
        if not self.__available_actions:
            self.__available_actions = self._generate_action_imports()

        if not self.__available_mappings:
            self.__available_mappings = self._generate_mapping_imports()    
        
        display_assignments = [
            { 
                "name": assign, 
                "importPath": "display" 
            } 
            for assign in AssignmentNameExtractor().get(self.__csts["display_py"])
        ]

        # Add all imports
        visitor = AddImportsTransformer(self.__available_actions + self.__available_mappings + display_assignments)
        self.__csts["inputs_py"] = self.__csts["inputs_py"].visit(visitor)

    def _add_all_possible_imports_display(self):
        if not self.__available_display_imports:
            self.__available_display_imports = self._generate_display_imports()

        # Add all imports
        visitor = AddImportsTransformer(self.__available_display_imports)
        self.__csts["display_py"] = self.__csts["display_py"].visit(visitor)
            
    # Generates all client specific display assigns (everything from the client's __init__.py file)
    def _generate_display_imports(self):
        ret = []
        for client in self.clients:
            ret += ClassNameExtractor(
                file = "pyswitch/clients/" + client + "/__init__.py", 
                import_path = "pyswitch.clients." + client
            ).get()
        
        return ret + [
            {
                "name": "const",
                "importPath": "micropython"
            },
            {
                "name": "Colors",
                "importPath": "pyswitch.misc"
            },
            {
                "name": "DisplayElement",
                "importPath": "pyswitch.ui.ui"
            },
            {
                "name": "DisplayBounds",
                "importPath": "pyswitch.ui.ui"
            },
            {
                "name": "DisplayLabel",
                "importPath": "pyswitch.ui.elements"
            },
            {
                "name": "BidirectionalProtocolState",
                "importPath": "pyswitch.ui.elements"
            }
        ]
    
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
    
    ##############################################################################################

    # Determine the client for an Action instance
    def _determine_import_statement(self, name, cst):
        visitor = ImportExtractor(name)
        cst.visit(visitor)
        return visitor.result

    # Determine the client for a type name. You must pass either cst or file_id.
    def determine_client(self, name, file_id = None, cst = None):
        import_statement = self._determine_import_statement(name, self.__csts[file_id] if file_id else cst)
        
        if not import_statement:
            # No import statement: Perhaps this is defined in inputs.py directly, so we have no client
            return "local"

        for client in self.clients:
            if client in import_statement:
                 return client

        return "local"