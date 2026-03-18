from pydantic import BaseModel


class AuditRequest(BaseModel):
    url: str


class AuditResponse(BaseModel):
    metrics: dict
    insights: dict
    recommendations: list
    prompt_logs: dict
