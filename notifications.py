import os
import json
from datetime import date, timedelta
from firebase_admin import credentials, initialize_app, messaging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Item
import config
import logging

# 1) Firebase Admin SDK 초기화
cred_path = config.GOOGLE_APPLICATION_CREDENTIALS
cred = credentials.Certificate(cred_path)
initialize_app(cred)

logger = logging.getLogger(__name__)

def send_push_to_user(user: User, title: str, body: str, data: dict = None):
    """
    한 사용자당 하나의 token이므로 messaging.Message 사용
    """
    token = user.fcm_token
    if not token or not user.notification:
        return

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {}
    )
    try:
        messaging.send(message)
    except Exception as e:
        # 에러 로깅
        logger.error(f"Failed to send FCM to user {user.user_id}: {e}")

        # 토큰 무효화 처리
        db: Session = SessionLocal()
        try:
            usr = db.query(User).get(user.user_id)
            usr.fcm_token = None
            db.add(usr)
            db.commit()
            logger.info(f"Cleared invalid token for user {user.user_id}")
        finally:
            db.close()





def notify_expiring_items():
    db = SessionLocal()
    try:
        today = date.today()
        for days in (3):
            target = today + timedelta(days=days)
            items = db.query(Item).filter(Item.expiry_date == target).all()
            for item in items:
                user = item.user
                if not user.notification or not user.fcm_token:
                    continue
                title = f"🗓 {days}일 후 유통기한 임박"
                body  = f"{item.item_name}의 유통기한이 {target}까지 {days}일 남았습니다."
                # FCM 전송 함수 호출
                send_push_to_user(user, title, body, {"item_id": str(item.item_id), "days": str(days)})
    finally:
        db.close()
