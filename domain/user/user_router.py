# domain/user/user_router.py

import os

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from auth import get_current_user
from jwt_utils import create_access_token

from database import get_db
from models import User
from domain.user import user_schema, user_crud
from domain.user.user_crud import (
    pwd_context,
    delete_user,
    get_user_by_login_id,
    get_user_by_user_id,
    get_user_by_username,
    update_user_username,
    update_user_password,
)

router = APIRouter(
    prefix="/user",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# 회원가입
@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(
    _user_create: user_schema.UserCreate,
    db: Session = Depends(get_db),
):
    # 닉네임·아이디 중복 확인
    if user_crud.get_existing_username(db, user_create=_user_create):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 닉네임입니다.")
    if user_crud.get_existing_login_id(db, user_create=_user_create):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 아이디입니다.")
    user_crud.create_user(db, user_create=_user_create)


# 회원탈퇴
@router.delete("/{user_id}/delete")
def delete_my_account(
    user_id: int,
    password: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="계정을 탈퇴할 권한이 없습니다.")
    try:
        delete_user(db, user_id=user_id, password=password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"detail": "회원 탈퇴가 완료되었습니다."}


# 로그인
@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(
    form_data: user_schema.LoginRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_login_id(db, form_data.login_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다.")
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="비밀번호가 잘못되었습니다.")
    access_token = create_access_token(data={"sub": user.user_id})
    return user_schema.Token(
        access_token=access_token,
        token_type="bearer",
        login_id=user.login_id,
        user_id=user.user_id,
        username=user.username,
    )


# FCM 토큰 등록/업데이트
@router.post(
    "/me/token",
    summary="FCM 토큰 등록/업데이트",
    description="클라이언트에서 전달한 FCM 토큰을 현재 로그인된 사용자에 저장합니다.",
    status_code=status.HTTP_200_OK,
)
def save_fcm_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 알림 설정 꺼져 있으면 저장 금지
    if not current_user.notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="알림이 비활성화된 사용자입니다.",
        )
    current_user.fcm_token = token
    db.add(current_user)
    db.commit()
    return {"message": "FCM token saved successfully."}


# 알림 켜기/끄기
@router.patch(
    "/me/notification",
    summary="알림 켜기/끄기",
    description="사용자가 푸시 알림을 켜거나 끕니다.",
    status_code=status.HTTP_200_OK,
)
def toggle_notification(
    enabled: bool = Query(..., description="true이면 켜기, false이면 끄기"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.notification = enabled
    # 끌 때는 토큰도 제거
    if not enabled:
        current_user.fcm_token = None
    db.add(current_user)
    db.commit()
    return {"message": "Notification setting updated", "enabled": enabled}


# FCM 토큰 삭제 (구독 해제)
@router.delete(
    "/me/token",
    summary="FCM 토큰 삭제(구독 해제)",
    description="사용자가 푸시 구독을 해제할 때 호출합니다.",
    status_code=status.HTTP_200_OK,
)
def delete_fcm_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.fcm_token = None
    db.add(current_user)
    db.commit()
    return {"message": "FCM token removed"}


# 닉네임 변경
@router.patch("/{user_id}/username")
def update_username(
    user_id: int,
    request: user_schema.UpdateNicknameRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_user_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="비밀번호를 확인하세요.")
    if get_user_by_username(db, username=request.new_username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 사용 중인 닉네임입니다.")
    updated_username = update_user_username(db, user_id=user_id, new_username=request.new_username)
    return {"message": "닉네임이 성공적으로 변경되었습니다.", "username": updated_username}


# 비밀번호 변경
@router.patch("/{user_id}/password", status_code=status.HTTP_200_OK)
def update_password(
    user_id: int,
    request: user_schema.UpdatePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호를 변경할 권한이 없습니다.")
    user = get_user_by_user_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="비밀번호를 확인하세요.")
    update_user_password(db, user_id=user_id, new_password=request.new_password)
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
