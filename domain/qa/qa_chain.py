from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from config import OPENAI_API_KEY

def get_recipe_chain() -> Runnable:
    prompt = PromptTemplate.from_template(
        "너는 요리 전문가야. 사용자의 냉장고에 있는 재료는 다음과 같아:\n\n"
        "{ingredients}\n\n"
        "사용자의 요청: {user_request}\n\n"
        "위 재료들과 사용자의 요청을 바탕으로 만들 수 있는 요리 3가지를 추천해줘. 레시피와와 간단한 설명도 함께 알려줘."
    )

    llm = ChatOpenAI(
        temperature=0.3,
        openai_api_key=OPENAI_API_KEY
    )

    chain = prompt | llm
    return chain
