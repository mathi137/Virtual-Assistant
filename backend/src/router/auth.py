from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from src.schemas.auth import Token
from src.utils.auth import authenticate_user, create_access_token
from src.db.session import get_session_dep

router = APIRouter()


@router.post("/token", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session_dep)],
) -> Token:
    # Authenticate user (uses form_data.username as email)
    user = await authenticate_user(session, form_data.username, form_data.password)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")