# backend/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime

class OverlayItem(BaseModel):
    id: str
    type: Literal["text", "image"]
    content: str  # text content or image URL/path
    x: float = Field(ge=0, le=1)   # normalized position (0..1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)
    rotation: float = 0
    opacity: float = Field(default=1, ge=0, le=1)
    zIndex: int = 0
    style: Dict[str, str] = {}

class OverlayDoc(BaseModel):
    name: str
    streamId: Optional[str] = None
    userId: Optional[str] = None
    items: List[OverlayItem] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
