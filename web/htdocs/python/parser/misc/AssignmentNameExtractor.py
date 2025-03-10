import libcst

class AssignmentNameExtractor:
        
    # Returns a list of all public assignments defined on module level
    def get(self, cst):
        ret = []

        # Check all statements for function definitions
        for statement in cst.body:
            if not isinstance(statement, libcst.SimpleStatementLine):
                continue

            if not isinstance(statement.body[0], libcst.Assign):
                continue

            assign = statement.body[0]

            for target in assign.targets:
                if target.target.value.startswith("_"):
                    continue

                ret.append(target.target.value)

        return ret
