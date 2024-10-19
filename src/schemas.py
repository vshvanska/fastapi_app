from datetime import datetime
from pydantic import BaseModel


class BaseInstance(BaseModel):
    created_at: datetime
    updated_at: datetime
