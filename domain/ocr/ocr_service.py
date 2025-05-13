import json
import base64
import openai
import re
from datetime import date, timedelta, timezone, datetime

def _strip_code_fence(raw: str) -> str:
    """
    ```json
    [...]
    ```
    같은 코드펜스를 제거하고 순수 JSON 텍스트만 반환.
    """
    # 1) ```json ... ```
    m = re.search(r"```(?:json)?\s*(\[[\s\S]*\])\s*```", raw, re.IGNORECASE)
    if m:
        return m.group(1)
    # 2) ``` ... ```
    m = re.search(r"```\s*([\s\S]*?)\s*```", raw)
    if m:
        return m.group(1)
    # 3) 펜스 없으면 그대로
    return raw

def extract_names_from_image(img_bytes: bytes) -> list[str]:
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    user_prompt = """
너는 식재료 및 요리 전문가야.
이 영수증(주문목록, 결제내역 등) 이미지에서 **상품명** 텍스트만 OCR로 추출하고,
추출된 상품명을 “일반 재료명”으로 정규화해줘.
예시: 찌개두부 → 두부, 바나나우유 → 우유, 애호박 → 호박, 포카칩 → 과자, 꿀사과 → 사과
최종적으로 JSON 배열(문자열 리스트) 형태로만 반환해.
""".strip()

    resp = openai.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role":"system","content":"You are a helpful assistant."},
            {
              "role":"user",
              "content":[
                 {"type":"text","text":user_prompt},
                 {"type":"image_url",
                   "image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
              ]
            }
        ]
    )

    raw = resp.choices[0].message.content or ""
    payload = _strip_code_fence(raw).strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        raise RuntimeError(f"OCR JSON 파싱 실패:\n{payload}")

def classify_names(names: list[str]) -> list[dict]:
    system = """
너는 식재료 및 요리 전문가야.  
아래의 다섯 가지 **대분류** 중 하나로 `category_major_name` 를,  
각 대분류에 속하는 **소분류** 중 하나로 `category_sub_name` 를 정확히 매핑하고,  
유통기한은 **무조건 “n일”** 형식(예: 1달 - “30일”, 1년 - “365일”)으로만 `expiry_text`에 텍스트로 제시해.
단, 유통기한이 없는 무기한 식품에 대해서는 `expiry_text`에 "무기한"이라고 제시해.

대분류 목록(category_major_name):
  1. 식물성
  2. 동물성 
  3. 조미료·양념
  4. 가공·저장식품
  5. 기타

소분류 목록(category_sub_name):
1. 식물성
- 곡류·서류(ex. 쌀, 현미, 보리, 잡곡, 밀가루, 감자, 고구마, 토란 등)
- 두류·견과(ex. 콩, 두부, 팥, 땅콩, 참깨, 호두 등)
- 채소류(ex. 뿌리채소, 잎·줄기채소, 열매채소, 기타채소 등)
- 버섯류(ex. 표고, 새송이, 느타리, 팽이 등)
- 과일류(ex. 사과, 배, 감, 포도, 딸기, 수박, 참외, 귤, 바나나, 오렌지, 키위 등)
- 해조류(ex. 김, 미역, 다시마, 파래 등)

2. 동물성  
- 육류(ex. 소고기, 돼지고기, 닭고기, 오리고기 등)
- 알류(ex. 달걀, 메추리알 등)
- 유제품(ex. 우유, 치즈 등)
- 해산물(ex. 생선류, 갑각류, 연체류 등)  

3. 조미료·양념    
- 기본 조미료(ex. 소금, 설탕, 식초, 후추 등)
- 한식 양념(ex. 간장, 된장, 고추장, 고춧가루, 참기름, 들기름 등)   

4. 가공·저장식품 
- 가공식품(ex. 어묵, 햄, 소시지, 라면, 만두, 떡 등)
- 저장식품/반찬(ex. 김치, 장아찌, 젓갈 등) 

5. 기타 
- 스낵/과자

반환 형식(JSON 배열):  
  [  
    {  
      "item_name": "사과",  
      "category_major_name": "식물성",  
      "category_sub_name": "과일류",  
      "expiry_text": "1주"  
    },  
    …  
  ]  
절대로 추가 설명 없이, 순수 JSON만 리턴하세요.
""".strip()

    resp = openai.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
           {"role":"system","content":system},
           {"role":"user","content": json.dumps(names, ensure_ascii=False)}
        ]
    )

    raw = resp.choices[0].message.content or ""
    # ```code fences``` 제거
    payload = _strip_code_fence(raw).strip()
    try:
        items = json.loads(payload)
    except json.JSONDecodeError:
        raise RuntimeError(f"분류 JSON 파싱 실패:\n{payload}")

    # 모델이 "category"/"shelf_life"로 내려줄 수 있으므로
    # Pydantic 스키마에 맞게 키 이름을 통일해 줍니다.
    standardized = []
    for it in items:
        standardized.append({
            "item_name":      it.get("item_name")   or it.get("base_name"),
            "category_major_name": it.get("category_major_name") or it.get("category"),
            # sub_category가 None일 경우 빈 문자열로
            "category_sub_name":   it.get("category_sub_name") or "",
            "expiry_text":    it.get("expiry_text")  or it.get("shelf_life") or "",
        })
    return standardized

def parse_expiry(expiry_text: str) -> date | None:
    """
    expiry_text가 "무기한"이면 None을 반환 (DB에는 NULL로 저장)
    그렇지 않으면 n일 후 날짜를 반환
    """
    today = date.today()
    if expiry_text == "무기한":
        return None

    # 텍스트에서 숫자만 뽑아 int로 변환
    num = int(''.join(filter(str.isdigit, expiry_text)) or 0)
    return today + timedelta(days=num)

