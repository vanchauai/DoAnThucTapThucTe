from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.user import User
from app.db.models.user import User as UserModel

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> Any:
    """
    Lấy thông tin người dùng hiện tại
    """
    return current_user

@router.get("", response_model=List[User], include_in_schema=False)
@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_manager_or_admin),
) -> Any:
    """
    Lấy danh sách người dùng. Manager/Admin mới có quyền.
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

from pydantic import BaseModel
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException, status
from app.schemas.user import UserCreate, UserUpdate
from app.services import auth_service

@router.post("", response_model=User)
@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_admin)
) -> Any:
    """
    Tạo user mới (Chỉ admin)
    """
    user = auth_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email đã tồn tại trong hệ thống.",
        )
    return auth_service.create_user(db, user_in)

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_admin)
) -> Any:
    """
    Cập nhật thông tin user (Chỉ admin). Hỗ trợ đổi password nếu truyền lên.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_in.email is not None and user_in.email != user.email:
        existing = auth_service.get_user_by_email(db, email=user_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email đã tồn tại")
        user.email = user_in.email
        
    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.branch_id is not None:
        user.branch_id = user_in.branch_id
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
        
    db.commit()
    db.refresh(user)
    return user

class UserStatusUpdate(BaseModel):
    is_active: bool

@router.patch("/{user_id}/status", response_model=User)
def update_user_status(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    status_in: UserStatusUpdate,
    current_user: UserModel = Depends(deps.get_current_admin)
) -> Any:
    """
    Khóa/mở khóa tài khoản (Chỉ admin)
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản của chính mình")
        
    user.is_active = status_in.is_active
    db.commit()
    db.refresh(user)
    return user

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

@router.put("/me/change-password")
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    pwd_in: ChangePassword,
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> Any:
    """
    User tự đổi mật khẩu (Ai cũng dùng được)
    """
    if not verify_password(pwd_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
        
    current_user.hashed_password = get_password_hash(pwd_in.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}
