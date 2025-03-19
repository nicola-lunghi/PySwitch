import libcst

class CodeGenerator:

    def __init__(self, parser = None, file_id = None, insert_before_assign = None):
        self.parser = parser
        self.file_id = file_id
        self.insert_before_assign = insert_before_assign

    # Generate libcst nodes from the passed specification data.
    def generate(self, data):   
        # Remove first assign as this will lead to endless recursion
        if "assign" in data: 
            data["assign"] = None

        return self._generate(data)

    ####################################################################################################################

    # Implementation for generate()
    def _generate(self, data):
        if isinstance(data, list):
            return self._generate_list_node(data)
        
        elif isinstance(data, dict):
            if "code" in data:
                return libcst.parse_expression(data["code"])
            
            if "name" in data:
                return self._generate_call_node(data)
            else:
                if "assign" in data and data["assign"] and "value" in data and data["value"]:
                    d = self._generate(data["value"])
                    return self._resolve_assign(d, data)
                else:
                    return self._generate_dict_node(data)

        return libcst.parse_expression(data)
        
    ####################################################################################################################

    # Generate libcst node from th passed list representation
    def _generate_list_node(self, data):
        return libcst.List(
            elements = [
                libcst.Element(
                    value = self._generate(item) 
                )
                for item in data
            ]
        )
    
    # Generate libcst node from the passed dict representation
    def _generate_dict_node(self, data):
        if "arguments" not in data:
            raise Exception("No arguments in dict: " + repr(data))

        dic = libcst.Dict(
            elements = [
                libcst.DictElement(
                    key = libcst.parse_expression('"' + item["name"] + '"'),
                    value = self._element_value(item)
                )
                for item in data["arguments"]
            ]
        )
    
        return self._resolve_assign(dic, data)

    # Generate libcst node from the passed call representation
    def _generate_call_node(self, data):
        args = data["arguments"] if "arguments" in data else []
        
        

        call = libcst.Call(
            func = libcst.parse_expression(data["name"]),
            args = [
                libcst.Arg(
                    keyword = libcst.parse_expression(arg["name"]) if ("name" in arg and arg["name"]) else None,
                    value = self._element_value(arg)
                )
                for arg in args
            ]
        )

        return self._resolve_assign(call, data)       
        
    # Resolve assigns. Not recursive: Assigns to assigns are realized with separate nodes.
    def _resolve_assign(self, node, data):
        if "assign" in data and data["assign"]:
            if not self.file_id:
                raise Exception("No file id for adding assignments")
            if not self.parser:
                raise Exception("No parser for adding assignments")
            
            self.parser.set_assignment(
                data["assign"],
                node,
                self.file_id, 
                insert_before_assign = self.insert_before_assign
            )

            ass = libcst.Name(
                value = data["assign"]
            )

            return ass

        return node

    # Returns the value of an element
    def _element_value(self, element):
        if "value" in element and element["value"] != None:
            return self._generate(element["value"])  
        else:
            if "code" in element and element["code"]:
                return libcst.parse_expression(element["code"])
            
            raise Exception("Invalid node: " + repr(element))