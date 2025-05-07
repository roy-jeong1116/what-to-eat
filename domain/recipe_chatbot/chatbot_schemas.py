from typing import List, Union
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class InputChat(BaseModel):
    """채팅 입력을 위한 기본 모델 정의"""
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]] = Field(
        ..., description="The chat messages representing the current conversation."
    )

    class Config:
        arbitrary_types_allowed = True