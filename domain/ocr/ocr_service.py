import os
import openai
import uuid
import base64
import cv2
import numpy as np
import json

from fastapi import UploadFile, HTTPException
from datetime import date, timedelta
from typing import List, Dict, Optional

from domain.ocr.ocr_schema import ReceiptItem, OCRExtractResponse, BoundingBox, NewItemRequest, FoodInfo
from domain.item import item_crud
from domain.item.item_schema import ItemCreate

from sqlalchemy.orm import Session

# 임시 저장소
OCR_RESULTS = {}

# OpenAI API 설정
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

async def get_food_info_from_llm(food_name: str) -> FoodInfo:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "아래 형식에 맞춰 식품명에 대한 카테고리와 일반적인 소비기한(일 단위)을 알려주세요.\n"
                    "응답 예시:\n"
                    "{\n"
                    "  \"category\": \"유제품\",\n"
                    "  \"shelf_life_days\": 7,\n"
                    "  \"description\": \"우유는 개봉 후 냉장보관 시 7일 정도 보관 가능합니다.\"n"
                    "}"
                )
            },
            {
                "role": "user",
                "content": f"다음 식품의 카테고리와 유통기한 정보를 알려줘: {food_name}"
            }
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=500
        )
        result = json.loads(response.choices[0].message.content)
        return FoodInfo(
            category=result.get("category", "기타"),
            shelf_life_days=result.get("shelf_life_days", 7),  # 기타 카테고리로 분류했을 때, Default 값 논의
            description=result.get("description")
        )
    except Exception:  # noqa
        return FoodInfo(category="기타", shelf_life_days=)