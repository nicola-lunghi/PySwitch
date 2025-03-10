import libcst
from ..misc.VisitorsWithStack import VisitorWithStack

class Arguments(VisitorWithStack):
    def __init__(self, action_name):
        super().__init__()
        self.action_name = action_name

        self.result = []
        
    def visit_Arg(self, node):
        if len(self.stack) != 2:
            return False

        if not node.keyword:
            return False

        self.result.append({
            "name": node.keyword.value,
            "value": self.__format_value(node.keyword.value, node.value)
        })

        return False

    # Parse incoming argument values from JS
    def parse_value(self, arg_name, arg_value):
        if self.action_name == "PagerAction" and arg_name == "pages":
            print(arg_value)
            return libcst.List(
                elements = [
                    libcst.Element(
                        value = libcst.Dict(
                            elements = [
                                libcst.DictElement(
                                    key = libcst.SimpleString(value = '"' + field + '"'),
                                    value = libcst.parse_expression(page[field]),
                                    comma = libcst.Comma(
                                        whitespace_before = libcst.SimpleWhitespace(
                                            value='',
                                        ),
                                        whitespace_after = libcst.ParenthesizedWhitespace(
                                            first_line = libcst.TrailingWhitespace(
                                                whitespace = libcst.SimpleWhitespace(
                                                    value=' ',
                                                ),
                                                newline = libcst.Newline(),
                                            ),
                                            last_line = libcst.SimpleWhitespace(
                                                value='                    ',
                                            ),
                                        ),
                                    ),
                                    whitespace_before_colon = libcst.SimpleWhitespace(value=''),
                                    whitespace_after_colon = libcst.SimpleWhitespace(value=' ')
                                )
                                for field in page
                            ],
                            lbrace = libcst.LeftCurlyBrace(
                                whitespace_after = libcst.ParenthesizedWhitespace(
                                    first_line = libcst.TrailingWhitespace(
                                        whitespace = libcst.SimpleWhitespace(value=''),
                                        newline = libcst.Newline(),
                                    ),
                                    last_line = libcst.SimpleWhitespace(
                                        value='                    ',
                                    )
                                ),
                            ),
                            rbrace = libcst.RightCurlyBrace(
                                whitespace_before = libcst.ParenthesizedWhitespace(
                                    first_line = libcst.TrailingWhitespace(
                                        whitespace = libcst.SimpleWhitespace(value=''),
                                        newline = libcst.Newline()
                                    ),
                                    last_line = libcst.SimpleWhitespace(
                                        value='                '
                                    )
                                )
                            )
                        ),
                        comma = libcst.Comma(
                            whitespace_before = libcst.SimpleWhitespace(value=''),
                            whitespace_after = libcst.ParenthesizedWhitespace(
                                first_line = libcst.TrailingWhitespace(
                                    whitespace = libcst.SimpleWhitespace(value=''),
                                    newline = libcst.Newline()
                                ),
                                last_line = libcst.SimpleWhitespace(
                                    value='                '
                                )
                            )
                        )
                    )
                    for page in arg_value.to_py()
                ]
            )

        return libcst.parse_expression(arg_value)

    # Format a value node, depending on its type
    def __format_value(self, arg_name, value_node):
        if self.action_name == "PagerAction" and arg_name == "pages":
            return self.__format_dict_list(value_node)

        elif isinstance(value_node, libcst.Name):
            return value_node.value
        
        elif isinstance(value_node, libcst.SimpleString):
            return value_node.value
        
        return libcst.parse_module("").code_for_node(value_node)

    # Format a list of dicts for JSON encoding
    def __format_dict_list(self, dict_list):
        ret = []
        for element in dict_list.elements:
            entry = {}
            for dict_element in element.value.elements:
                key = dict_element.key.value.strip('\"')
                value = libcst.parse_module("").code_for_node(dict_element.value)
                
                entry[key] = value

            ret.append(entry)

        return ret
