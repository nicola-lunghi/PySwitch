
from .Condition import Condition, ConditionListener
from ..Updateable import Updater

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
    def __init__(self, subject, listener = None, allow_lists = True):
        if not isinstance(listener, ConditionListener):
            raise Exception("Invalid condition listener")

        self._entries = []                # Flat list of all data objects (no conditions)
        self._conditions = []             # List of conditions found
        self._allow_lists = allow_lists   # Allow lists of entries

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
            self._entries.append(subject)
            return subject

    # Must be called before usage to get the conditions updated periodically. 
    # Updater must be an Updater instance to which the conditions are added.
    def init(self, appl):
        if not isinstance(appl, Updater):
            raise Exception("Invalid appl for ConditionTree, must be an Updater")

        # Initialize conditions and add them to the updateable list
        for c in self._conditions:
            c.init(appl)            
            appl.add_updateable(c)

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
