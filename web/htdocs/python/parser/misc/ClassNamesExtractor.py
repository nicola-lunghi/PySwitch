# import libcst
from .ClassNameExtractor import ClassNameExtractor

# Version of ClassNameExtractor running for multiple files 
class ClassNamesExtractor:

    def __init__(self, import_paths):
        self.import_paths = import_paths        

    # Returns a list of all public classes defined on module level
    def get(self):
        ret = []

        for path in self.import_paths:
            extractor = ClassNameExtractor(
                file = path,
                import_path = path.replace("/", ".").removesuffix(".py")
            )

            ret += extractor.get()

        return ret