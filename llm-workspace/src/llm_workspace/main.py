import dagger
from dagger import function, object_type


@object_type
class LlmWorkspace:
    file: dagger.File

    @function
    def readFile(self) -> str:
        """Returns the contents of a file"""
        return self.file.contents()
