from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class createDocumentRequest(_message.Message):
    __slots__ = ("docName", "content")
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    docName: str
    content: str
    def __init__(self, docName: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class createDocumentResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class getDocumentRequest(_message.Message):
    __slots__ = ("docName",)
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    docName: str
    def __init__(self, docName: _Optional[str] = ...) -> None: ...

class getDocumentResponse(_message.Message):
    __slots__ = ("docName", "content")
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    docName: str
    content: str
    def __init__(self, docName: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class editDocumentRequest(_message.Message):
    __slots__ = ("docName", "content", "position")
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    docName: str
    content: str
    position: int
    def __init__(self, docName: _Optional[str] = ..., content: _Optional[str] = ..., position: _Optional[int] = ...) -> None: ...

class editDocumentResponse(_message.Message):
    __slots__ = ("docName", "content")
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    docName: str
    content: str
    def __init__(self, docName: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class updateRequest(_message.Message):
    __slots__ = ("docName",)
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    docName: str
    def __init__(self, docName: _Optional[str] = ...) -> None: ...

class documentUpdate(_message.Message):
    __slots__ = ("docName", "content")
    DOCNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    docName: str
    content: str
    def __init__(self, docName: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...
