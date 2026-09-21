from enum import StrEnum


class ContractStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    TEXT_EXTRACTED = "text_extracted"
    INDEXED = "indexed"
    ANALYZED = "analyzed"
    COMPLETED = "completed"
    FAILED = "failed"