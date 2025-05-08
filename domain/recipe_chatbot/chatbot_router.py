from fastapi import APIRouter
from langserve import add_routes
from .chains import ChatChain  # ChatChain 임포트
from .chatbot_schemas import InputChat

# from langserve.pydantic_v1 import BaseModel, Field
# from pydantic import BaseModel, Field
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from typing import List, Union  # List와 Union을 typing에서 임포트

router = APIRouter()

# 대화형 채팅 엔드포인트 설정
add_routes(
    router,
    ChatChain().create().with_types(input_type=InputChat),
    path="/chat",  # API 경로 설정
    enable_feedback_endpoint=False,
    enable_public_trace_link_endpoint=False,
    playground_type="chat",
)