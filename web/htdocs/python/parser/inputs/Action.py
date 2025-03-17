from ..misc.ItemBase import ItemBase

class Action(ItemBase):
    def __init__(self, input, call_node):
        super().__init__(input.parser, call_node)
        
        self.input = input 
        self.client = self._determine_client()

    # Removes the action from the tree.
    def remove(self):
        self._arguments = None
        self.input.remove_action(self.node)

    # If the action is connected to a pager, this returns the page ID, or None if not.
    def page(self):
        if not self.pager():
            return None
        
        return self.argument("id")
    
    # Returns the pager name, if any
    def pager(self):
        ec = self.argument("enable_callback")
        if not ec:
            return None
        
        if not self.argument("id") or self.argument("id") == "None":
            return None
        
        splt = ec.split(".")
        if len(splt) != 2:
            return None
        
        return splt[0]

    # Determine the client
    def _determine_client(self):
        import_statement = self.input.parser.determine_import_statement(self)
        if not import_statement:
            # No import statement: Perhaps this is defined in inputs.py directly, so we have no client
            return "local"

        for client in self.input.parser.clients:
            if client in import_statement:
                 return client

        return "local"