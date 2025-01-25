 
class MockGC:
    def collect(self):
        pass

    def mem_free(self):
        return 1024 * 1024 * 1024

    def mem_alloc(self):
        return 0
        
        
class MockIO:
    class FileIO:
        def readinto(self, buffer):
            pass

