
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
    # factory       can be used to replace the entries in the subject with something else.
    #               Must be instance of ConditionModelFactory.
    #
    # allow_lists   can be set to False if only singular entries shall be allowed (no lists, just entries
    #               or Conditions).
    #
    def __init__(self, subject, listener = None, factory = None, allow_lists = True):
        if not isinstance(listener, ConditionListener):
            raise Exception("Invalid condition listener")

        if not isinstance(factory, ConditionModelFactory):
            raise Exception("Invalid condition model factory")

        self._objects = []      # Flat list of data objects (no conditions)
        self._conditions = []   # List of conditions found

        self._tree = self._setup_tree(subject, listener, factory, allow_lists)
    
    # Setup the tree from the passed subject
    def _setup_tree(self, subject, listener, factory, allow_lists, enable = True):
        if subject == None:
            return None
        
        elif isinstance(subject, list):
            if allow_lists != True:
                raise Exception("No lists allowed for conditional parameter")
            
            ret = []
            for entry in subject:
                ret = ret + [self._setup_tree(
                    entry, 
                    listener,
                    factory,
                    allow_lists,
                    enable
                )]

            return ret

        elif isinstance(subject, Condition):
            # Condition based: Create both outcomes
            result_yes = self._setup_tree(
                subject.yes, 
                listener,
                factory,
                allow_lists,
                False if not enable else True
            )

            result_no = self._setup_tree(
                subject.no,
                listener,
                factory,
                allow_lists,
                False
            )

            subject.yes = result_yes
            subject.no = result_no
            
            # Add this instance as listener on condition changes
            if listener != None:
                subject.add_listener(listener)

            self._conditions.append(subject)

            return subject
        
        else:
            # Simple dict definition
            if factory != None:
                # Optional: Factory to create model objects. If not passed, 
                # the subjects themselves are collected in the condition models.
                object = factory.get_condition_instance(subject, enable)
                if object != None:
                    self._objects.append(object)
                    return object
            
            return subject

    # Must be called before usage to get the conditions updated. 
    # Updater must be an Updater instance to which the conditions are added.
    def init(self, appl):
        if not isinstance(appl, Updater):
            raise Exception("Invalid appl for ConditionTree, must be an Updateable")

        # Initialize conditions and add them to the updateable list
        for c in self._conditions:
            c.init(appl)            
            appl.add_updateable(c)

    # Returns a flat list of all data objects in the passed subject
    @property
    def objects(self):
        return self._objects

    @property
    def conditions(self):
        return self._conditions

    # Returns the currently active value from the tree if created 
    # with allow_lists = False (if not, returns the first value)
    @property   
    def value(self):
        v = self._tree_value(self._tree)
        if len(v) == 0:
            return None
        return v[0]
    
    # Returns the currently active value list (makes sense if 
    # allow_lists was True)
    @property   
    def values(self):
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

    # Representational string
    def __repr__(self):
        return self._get_entry_repr(self._tree)

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

        
############################################################################################################################


# Base class for evaluating customer data in Condition.parse()
class ConditionModelFactory:
    # data is the customer data in the condition configs, enabled signals if the
    # condition branch is active by default (assuming that all conditions are true by default).
    # Can return a model instance or something else which will be collected in the Condition models,
    # so the listeners can access them later (optional).
    def get_condition_instance(self, data, enabled):
        return None

