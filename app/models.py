from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class ValidationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ts: datetime = Field(default_factory=lambda: datetime.utcnow())
    account_hash: str
    ip_hash: str
    score: int
    source: str
    latency_ms: int