from pydantic import BaseModel


class AiRsp(BaseModel):
    ai_model: str
    ip: str


class IpInfo(BaseModel):
    source_ip_query: str
    source_character_query: str
    ai_rsp: dict
