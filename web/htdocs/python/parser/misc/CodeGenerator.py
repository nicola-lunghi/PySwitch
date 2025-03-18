import libcst

class CodeGenerator:

    def __init__(self, parser, file_id, insert_before_assign = None):
        self.parser = parser
        self.file_id = file_id
        self.insert_before_assign = insert_before_assign

    def generate(self, data):
        if isinstance(data, list):
            return self._generate_list_node(data)
        
        elif isinstance(data, dict):
            if "name" in data:
                return self._generate_call_node(data)
            else:
                if "assign" in data and "value" in data:
                    d = self.generate(data["value"])
                    return self._resolve_assign(d, data)
                else:
                    return self._generate_dict_node(data)

        return libcst.parse_expression(data)
        
    ############################################################################

    def _generate_list_node(self, data):
        return libcst.List(
            elements = [
                libcst.Element(
                    value = self.generate(item) 
                )
                for item in data
            ]
        )
    
    def _generate_dict_node(self, data):
        dic = libcst.Dict(
            elements = [
                libcst.DictElement(
                    key = libcst.parse_expression('"' + item["name"] + '"'),
                    value = self.generate(item["value"])
                )
                for item in data["arguments"]
            ]
        )
    
        return self._resolve_assign(dic, data)

    def _generate_call_node(self, data):
        args = data["arguments"] if "arguments" in data else []

        call = libcst.Call(
            func = libcst.parse_expression(data["name"]),
            args = [
                libcst.Arg(
                    keyword = libcst.parse_expression(arg["name"]) if "name" in arg else None,
                    value = self.generate(arg["value"])
                )
                for arg in args
            ]
        )

        return self._resolve_assign(call, data)       
        
    def _resolve_assign(self, node, data, insert_before_assign = None):
        if "assign" in data:
            if not insert_before_assign:
                insert_before_assign = self.insert_before_assign
            
            # if "value" in data and isinstance(data["value"], dict) and "assign" in data["value"]:
            #     new_node = self._resolve_assign(
            #         node, 
            #         data["value"], 
            #         insert_before_assign = data["assign"]
            #     )
            # else:
            new_node = node

            # if data["assign"] == "_ACTION_LABEL_LAYOUT":
            #     print(insert_before_assign)

            self.parser.set_assignment(
                data["assign"],
                new_node,
                self.file_id, 
                insert_before_assign = insert_before_assign
            )

            ass = libcst.Name(
                value = data["assign"]
            )

            return ass

        return node
