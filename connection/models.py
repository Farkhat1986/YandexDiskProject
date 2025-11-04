from typing import List, Literal

from pydantic import BaseModel, Field, HttpUrl


class DiskUser(BaseModel):
    login: str
    display_name: str


class DiskInfoResponse(BaseModel):
    user: DiskUser


class ErrorResponse(BaseModel):
    error: str | None = None
    description: str | None = None
    message: str | None = None


class ResourceLink(BaseModel):
    """Модель ссылки на ресурс"""

    href: HttpUrl
    method: str
    templated: bool


class CreateFolderResponse(BaseModel):
    """Модель ответа при создании папки"""

    href: HttpUrl
    method: Literal["GET"]
    templated: bool


class ResourceInfo(BaseModel):
    """Модель информации о ресурсе"""

    name: str
    type: Literal["file", "dir"] | None = None
    path: str
    created: str | None = None
    modified: str | None = None

    mime_type: str | None = None
    size: int | None = None
    md5: str | None = None


class UploadUrlResponse(BaseModel):
    """Модель ответа с URL для загрузки"""

    operation_id: str
    href: HttpUrl
    method: Literal["PUT"]
    templated: bool


class EmbeddedFiles(BaseModel):
    items: List[ResourceInfo]
    limit: int
    offset: int
    total: int


class FilesListResponse(BaseModel):
    """Модель ответа со списком файлов (папки с содержимым)"""

    type: Literal["dir"]
    path: str
    name: str
    embedded: EmbeddedFiles = Field(alias="_embedded")


class TrashResourceInfo(BaseModel):
    """Модель информации о ресурсе в корзине"""

    path: str
    type: str
    name: str
    origin_path: str
    resource_id: str


class CopyResourceResponse(BaseModel):
    """Модель ответа при успешном копировании ресурса"""

    href: HttpUrl
    method: Literal["GET"]
    templated: bool


class DownloadLinkResponse(BaseModel):
    """Модель ответа с ссылкой для скачивания"""

    href: HttpUrl
    method: Literal["GET"]
    templated: bool


class CopyResourceRequest(BaseModel):
    """Модель запроса для копирования ресурса"""

    from_path: str
    to_path: str
