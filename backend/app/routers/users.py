from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin
from app.security import hash_password, verify_password
from app.dependencies import get_current_user, require_role

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_id": user.id,
    "role": user.role,
}
@router.post("/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }

@router.get("/admin-only")
def admin_only(
    current_user: User = Depends(require_role("ADMIN")),
):
    return {
        "message": "Welcome Admin",
        "user_id": current_user.id,
        "role": current_user.role,
    }
    
@router.get("/{user_id}")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own user profile"
        )
    
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active
    }