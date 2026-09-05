"""Citations and references attached to a message."""

from __future__ import annotations


class MessageAnnotation:
    """A URL citation, file citation, or internal ref on a message span."""

    def __init__(
        self,
        kind: str,
        url: str | None = None,
        file_id: str | None = None,
        title: str | None = None,
        quote: str | None = None,
        start_index: int | None = None,
        end_index: int | None = None,
    ) -> None:
        if not kind or not str(kind).strip():
            raise ValueError("Annotation kind cannot be empty.")
        self.kind = kind.strip().lower()
        self.url = url
        self.file_id = file_id
        self.title = title
        self.quote = quote
        self.start_index = start_index
        self.end_index = end_index

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MessageAnnotation)
            and self.kind == other.kind
            and self.url == other.url
            and self.file_id == other.file_id
            and self.title == other.title
            and self.quote == other.quote
            and self.start_index == other.start_index
            and self.end_index == other.end_index
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.kind,
                self.url,
                self.file_id,
                self.title,
                self.quote,
                self.start_index,
                self.end_index,
            )
        )

    @classmethod
    def url_citation(
        cls,
        url: str,
        title: str | None = None,
        quote: str | None = None,
        start_index: int | None = None,
        end_index: int | None = None,
    ) -> MessageAnnotation:
        """Citation pointing at ``url``, optionally spanning character indexes."""
        return cls(
            "url_citation",
            url=url,
            title=title,
            quote=quote,
            start_index=start_index,
            end_index=end_index,
        )

    @classmethod
    def file_citation(
        cls,
        file_id: str,
        title: str | None = None,
        quote: str | None = None,
    ) -> MessageAnnotation:
        """Citation of an uploaded or retrieved file."""
        return cls("file_citation", file_id=file_id, title=title, quote=quote)

    @classmethod
    def internal_ref(cls, reference: str, title: str | None = None) -> MessageAnnotation:
        """Internal pointer stored in ``file_id``."""
        return cls("internal_ref", file_id=reference, title=title)
