from typing import Union, IO
from pathlib import Path

FilePath = Union[str, Path]
Buffer = IO
FilePathOrBuffer = Union[FilePath, Buffer]
