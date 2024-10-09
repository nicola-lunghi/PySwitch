#from .Client import ClientRequestListener
from ..misc import Tools, Updateable, Updater, EventEmitter

# Base condition to be filled with custom objects or lists (which can be or contain Conditions themselves).
# Compares the value of the mapping to the passed one, and notifies listeners when the value has changed.
class Condition(EventEmitter, Updateable):
    def __init__(self, yes = None, no = None):
        super().__init__() #ConditionListener)

        self.yes = yes    # Positive value
        self.no = no      # Negative value

        self.true = True  # Current state of the condition
        
        self.appl = None

    # Called when the UI is ready (some child classes need an appl reference, this is not used here)
    def init(self, appl):
        self.appl = appl

        
############################################################################################################################


# Base class for evaluating condition changes
#class ConditionListener:
#    # Called on condition changes. The changed condition is passed, however you may more
#    # likely use the ConditionTree value(s) instead.
#    def condition_changed(self, condition):
#        pass

    
############################################################################################################################


# Factory for replacing entries
#class ConditionTreeEntryReplacer:
#    # Returns the data to replace entry with.
#    def replace(self, entry):
#        return None


############################################################################################################################


# Tree of conditions. Supports generic entries.
class ConditionTree:

    # Parses the data in subject, which can be a single data object of any type, or a list of objects. Every object 
    # can hereby be a Condition, too, which is evaluated regularily via an Updater. On changes, the listener
    # will be informed and can get the currently valid entries (or single value) by using the value property.
    # The subject will be destroyed and the conditions reused.
    #
    # listener      is registered to all found conditions if passed. Must be instance of ConditionListener.
    #
    # allow_lists   can be set to False if only singular entries shall be allowed (no lists, just entries
    #               or Conditions).
    #
    # replacer      Optional instance of ConditionTreeEntryReplacer, used to replace the input entries.
    #
    def __init__(self, subject, listener = None, replacer = None, allow_lists = True):
        #if not isinstance(listener, ConditionListener):
        #    raise Exception("Invalid condition listener")

        self._entries = []                # Flat list of all data objects (no conditions)
        self._conditions = []             # List of conditions found
        self._allow_lists = allow_lists   # Allow lists of entries
        self._replacer = replacer         # Optional replacer for entries

        self._tree = self._setup_tree(subject, listener)
    
    # Representational string
    def __repr__(self):
        return self._get_entry_repr(self._tree)

    # Setup the tree from the passed subject
    def _setup_tree(self, subject, listener, enable = True):
        if subject == None:
            return None
        
        elif isinstance(subject, list):
            if not self._allow_lists:
                raise Exception("No lists allowed for conditional parameter")
            
            ret = []
            for entry in subject:
                ret = ret + [self._setup_tree(
                    entry, 
                    listener,
                    enable
                )]

            return ret

        elif isinstance(subject, Condition):
            # Condition based: Create both outcomes
            result_yes = self._setup_tree(
                subject.yes, 
                listener,
                False if not enable else True
            )

            result_no = self._setup_tree(
                subject.no,
                listener,
                False
            )

            subject.yes = result_yes
            subject.no = result_no
            
            # Add this instance as listener on condition changes
            if listener:
                subject.add_listener(listener)

            self._conditions.append(subject)

            return subject
        
        else:
            # Simple entry
            if self._replacer:
                new_entry = self._replacer.replace(subject)
                self._entries.append(new_entry)
                return new_entry

            self._entries.append(subject)
            return subject

    # Must be called before usage to get the conditions updated periodically. 
    # Updater must be an Updater instance to which the conditions are added.
    def init(self, updater):
        if not isinstance(updater, Updater):
            raise Exception("Invalid appl for ConditionTree, must be an Updater")

        # Initialize conditions and add them to the updateable list
        for c in self._conditions:
            c.init(updater)            
            updater.add_updateable(c)

    # Returns a flat list of all contained data entries
    @property
    def entries(self):
        return self._entries

    # Returns a flat list of all contained conditions
    @property
    def conditions(self):
        return self._conditions

    # Returns the currently active value from the tree if created 
    # with allow_lists = False. 
    @property   
    def value(self):
        if self._allow_lists:
            raise Exception("This tree is built with lists and only returns lists of entries, use .values instead")
        
        v = self._tree_value(self._tree)
        return v[0]
    
    # Returns the currently active value list (makes sense if 
    # allow_lists was True)
    @property   
    def values(self):
        if not self._allow_lists:
            raise Exception("This tree is built without list support and only returns a single entry, use .value instead")
        
        return self._tree_value(self._tree)

    # Returns a list of currently active values
    def _tree_value(self, tree):
        if tree == None:
            return []
        
        elif isinstance(tree, list):
            ret = []
            for entry in tree:
                ret = ret + self._tree_value(entry)

            return ret

        elif isinstance(tree, Condition):
            if tree.true:
                return self._tree_value(tree.yes)
            else:
                return self._tree_value(tree.no)
        
        else:
            return [tree]

    # Returns a representation of the passed subject
    def _get_entry_repr(self, subject, indent = 0):
        indent_str = "".join([" " for i in range(indent)])
        
        if subject == None:
            return indent_str + repr(None) + "\n"
        
        elif isinstance(subject, list):
            ret = indent_str + "[\n"

            for entry in subject:
                ret += self._get_entry_repr(entry, indent + 2)

            return ret + indent_str + "]\n"

        elif isinstance(subject, Condition):
            indent_str_p2 = "".join([" " for i in range(indent + 2)])

            ret = indent_str + subject.__class__.__name__ + "(\n"
            
            ret += indent_str_p2 + "yes: \n"
            ret +=  self._get_entry_repr(subject.yes, indent + 4)

            ret += indent_str_p2 + "no: \n"
            ret += self._get_entry_repr(subject.no, indent + 4)

            return ret + indent_str + ")\n"
        
        else:
            return indent_str + repr(subject) + "\n"


########################################################################################################################################


# Comparison modes for ParameterCondition
class ParameterConditionModes:    
    # Numeric
    MODE_EQUAL = 0                   # Reference value must be a numeric value
    
    MODE_GREATER = 10                # Reference value must be a numeric value
    MODE_GREATER_EQUAL = 21          # Reference value must be a numeric value
    
    MODE_LESS = 20                   # Reference value must be a numeric value
    MODE_LESS_EQUAL = 21             # Reference value must be a numeric value
    
    MODE_IN_RANGE = 90               # Reference value must be a tuple with lower / higher borders (inclusive). For example: (0, 1.2)

    # Strings
    MODE_STRING_CONTAINS = 500       # Reference value must be a string
    MODE_STRING_NOT_CONTAINS = 501   # Reference value must be a string
    MODE_STRING_STARTS_WITH = 510    # Reference value must be a string
    MODE_STRING_ENDS_WITH = 520      # Reference value must be a string


########################################################################################################################################


# Condition to be filled with action specifications.
# Compares the value of the mapping to the passed one, and enables the action or action_not.
class ParameterCondition(Condition): #, ClientRequestListener):
    def __init__(self, mapping, ref_value, mode = ParameterConditionModes.MODE_GREATER_EQUAL, yes = None, no = None):
        super().__init__(yes = yes, no = no)

        self._mapping = mapping
        self._ref_value = ref_value
        self._mode = mode

        self._current_raw_value = None

    # Used internally: Set the model instances for the two values.
    def init(self, appl):
        super().init(appl)

        self._debug = Tools.get_option(self.appl.config, "debugConditions")

    # Used internally: Updates the condition on every update tick
    def update(self):
        if not self.appl:
            raise Exception("Condition not initialized")

        if self._debug:
            self._print("Requesting value")

        self.appl.client.request(self._mapping, self)

    # Evaluate a received value and return True or False (heart of the condition)
    def _evaluate_value(self, value):
        if self._mode == ParameterConditionModes.MODE_GREATER:
            return value > self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_GREATER_EQUAL:
            return value >= self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_LESS:
            return value < self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_LESS_EQUAL:
            return value <= self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_EQUAL:
            return value == self._ref_value            
            
        elif self._mode == ParameterConditionModes.MODE_IN_RANGE:
            return value >= self._ref_value[0] and value <= self._ref_value[1]
            
        elif self._mode == ParameterConditionModes.MODE_STRING_CONTAINS:
            return self._ref_value in value
        
        elif self._mode == ParameterConditionModes.MODE_STRING_NOT_CONTAINS:
            return self._ref_value not in value
        
        elif self._mode == ParameterConditionModes.MODE_STRING_STARTS_WITH:
            return value.startswith(self._ref_value)
        
        elif self._mode == ParameterConditionModes.MODE_STRING_ENDS_WITH:
            return value.endswith(self._ref_value)
        
        else:
            raise Exception("Invalid condition mode: " + repr(self._mode))

    # Called by the Client class when a parameter request has been answered.
    # The value received is already set on the mapping.
    def parameter_changed(self, mapping):
        if mapping != self._mapping:
            return
        
        if mapping.value == self._current_raw_value:
            return

        self._current_raw_value = mapping.value

        bool_value = self._evaluate_value(mapping.value)
            
        if self.true == bool_value:
            return

        self.true = bool_value

        if self._debug:
            self._print(" -> Received value " + repr(mapping.value) + ", evaluated to " + repr(self.true))

        for listener in self.listeners:
            listener.condition_changed(self)        

    # Called when the client is offline (requests took too long)
    def request_terminated(self, mapping):
        if mapping != self._mapping:
            return
        
        self.true = True

    # Debug console output
    def _print(self, msg):
        if not self._debug:
            return
        
        Tools.print("Condition for " + self._mapping.name + ": " + msg)
        

######################################################################################################


# Condition to be filled with action specifications.
# Listens to another action (which must be a PushButtonAction).
class PushButtonCondition(Condition):
    def __init__(self, id, enabled = None, disabled = None):
        super().__init__(yes = enabled, no = disabled)
        
        self._id = id

    # Used internally: Set the model instances for the two values.
    def init(self, appl):
        super().init(appl)
        
        self._action = self._determine_action(self._id)

    # Used internally: Updates the condition on every update tick
    def update(self):
        bool_value = self._action.state

        if self.true == bool_value:
            return

        self.true = bool_value

        for listener in self.listeners:
            listener.condition_changed(self)   

    # Determine the action by ID
    def _determine_action(self, id):
        if not self.appl:
            raise Exception("Condition not initialized")
        
        for switch in self.appl.switches:
            for action in switch.actions:
                if action.id == id:
                    return action
                
        raise Exception("Action with ID " + repr(id) + " not defined")

