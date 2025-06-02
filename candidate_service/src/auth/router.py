from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session
from src.auth.schemas import UserCreate, UserRead, TokenResponse
from src.auth.service import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_admin,
    get_user_by_username
)
from src.auth.models import User
from src.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/register", response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        username=user_in.username,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserRead.model_validate(db_user)


@router.post("/login", response_model=TokenResponse)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=30)
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user=Depends(get_current_user)):
    access_token = create_access_token(
        data={"sub": current_user.username, "role": current_user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user=Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.get("/admin", response_model=UserRead)
async def read_admin_me(current_user=Depends(get_current_admin)):
    return UserRead.model_validate(current_user)
