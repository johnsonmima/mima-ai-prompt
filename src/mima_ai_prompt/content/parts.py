"""Text and image parts used to construct multimodal message bodies."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ContentPart(Protocol):
    """Serializable fragment of a message body."""

    @property
    def type(self) -> str: ...


class TextPart:
    """A text segment in a structured message body."""

    type = "text"

    def __init__(self, text: str) -> None:
        if text is None:
            raise TypeError("text cannot be None")
        self.text = text

    @classmethod
    def create(cls, text: str) -> TextPart:
        """Create a ``TextPart`` (same as the constructor)."""
        return cls(text)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TextPart) and self.text == other.text

    def __hash__(self) -> int:
        return hash((self.type, self.text))


class ImagePart:
    """A remote image URL or inline base64 image."""

    type = "image"

    def __init__(
        self,
        url: str | None = None,
        base64_data: str | None = None,
        media_type: str | None = None,
        detail: str | None = None,
    ) -> None:
        if (url is None or not str(url).strip()) and (
            base64_data is None or not str(base64_data).strip()
        ):
            raise ValueError("Image part requires a URL or base64 data.")
        self.url = url
        self.base64_data = base64_data
        self.media_type = media_type
        self.detail = detail

    @classmethod
    def from_url(cls, url: str, detail: str | None = None) -> ImagePart:
        """Image referenced by HTTP(S) URL; optional vision ``detail``."""
        if url is None:
            raise TypeError("url cannot be None")
        return cls(url=url, detail=detail)

    @classmethod
    def from_base64(
        cls, base64_data: str, media_type: str, detail: str | None = None
    ) -> ImagePart:
        """Inline image; ``media_type`` is required (for example ``image/png``)."""
        if media_type is None or not str(media_type).strip():
            raise ValueError("Media type is required for base64 images.")
        return cls(base64_data=base64_data, media_type=media_type, detail=detail)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ImagePart)
            and self.url == other.url
            and self.base64_data == other.base64_data
            and self.media_type == other.media_type
            and self.detail == other.detail
        )

    def __hash__(self) -> int:
        return hash((self.type, self.url, self.base64_data, self.media_type, self.detail))
