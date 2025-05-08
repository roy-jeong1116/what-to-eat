import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from auth import get_current_user
from jwt_utils import create_access_token

from database import get_db
from models import User
from domain.user import user_schema, user_crud
from domain.user.user_crud import pwd_context, delete_user, get_user_by_login_id
from domain.user.user_schema import UserDelete, LoginRequest, Token

router = APIRouter(
    prefix="/user",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# 회원가입
@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    username = user_crud.get_existing_username(db, user_create=_user_create)
    login_id = user_crud.get_existing_login_id(db, user_create=_user_create)

    if username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 닉네임입니다.")

    if login_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다.")

    user_crud.create_user(db, user_create=_user_create)

# 회원탈퇴
@router.delete("/{user_id}/delete")
def delete_my_account(
        user_id: int,
        form: UserDelete,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    if user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="계정을 탈퇴할 권한이 없습니다.")

    try:
        delete_user(db, user_id=user_id, password=form.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"detail": "회원 탈퇴가 완료되었습니다."}

# 로그인
@router.post("/login", response_model=Token)
def login_for_access_token(
        form_data: LoginRequest, db: Session = Depends(get_db)
):
    user = get_user_by_login_id(db, form_data.login_id)

    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="비밀번호가 잘못되었습니다.")

    access_token = create_access_token(data={"sub": str(user.user_id)})

    return Token(access_token=access_token, token_type="bearer", login_id=user.login_id, user_id=user.user_id)

# 유통기한 알림
@router.post(
    "/me/token",
    summary="FCM 토큰 등록/업데이트",
    description="클라이언트에서 전달한 FCM 토큰을 현재 로그인된 사용자에 저장합니다.",
    status_code=status.HTTP_200_OK
)
def save_fcm_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 사용자 설정에서 푸시 알림이 꺼져 있으면 에러
    if not current_user.notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="알림이 비활성화된 사용자입니다."
        )

    # 토큰 저장
    current_user.fcm_token = token
    db.add(current_user)
    db.commit()

    return {"message": "FCM token saved successfully."}

@router.patch(
    "/me/notification",
    summary="알림 켜기/끄기",
    description="사용자가 알림을 켜거나 끕니다.",
    status_code=status.HTTP_200_OK
)
def toggle_notification(
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.notification = enabled
    # 알림 끌 때는 토큰도 제거
    if not enabled:
        current_user.fcm_token = None
    db.add(current_user)
    db.commit()
    return {"message": "Notification setting updated", "enabled": enabled}


@router.delete(
    "/me/token",
    summary="FCM 토큰 삭제(구독 해제)",
    description="사용자가 푸시 구독을 해제할 때 호출합니다.",
    status_code=status.HTTP_200_OK
)
def delete_fcm_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.fcm_token = None
    db.add(current_user)
    db.commit()
    return {"message": "FCM token removed"}