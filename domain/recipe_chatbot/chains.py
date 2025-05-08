from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .base import BaseChain
from .prompt_config import DEFAULT_SYSTEM_PROMPT


class ChatChain(BaseChain):
    """대화형 체인 클래스"""

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT, **kwargs):
        super().__init__(**kwargs)
        self.system_prompt = system_prompt

    def setup(self):
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = prompt | llm | StrOutputParser()
        return chain


class LLM(BaseChain):
    """단일 LLM 객체 반환"""

    def setup(self):
        return ChatOpenAI(model=self.model, temperature=self.temperature)