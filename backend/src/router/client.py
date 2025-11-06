from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.session import get_session_dep
from src.db.model.client import ClientCreate, ClientRead, ClientUpdate
from src.db.crud import ClientCRUD as Database
from src.utils.auth import get_current_active_user, verify_password, create_access_token
from src.config import settings
from src.db.model.user import User

router = APIRouter()


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Create a new client. Only authenticated admin users can create clients."""
    return await Database.create(session, client, current_user.id)


@router.get("/", response_model=list[ClientRead], status_code=status.HTTP_200_OK)
async def get_all_clients(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Get all clients. Returns all clients for admin users."""
    return await Database.get_all(session)


@router.get("/my-clients", response_model=list[ClientRead], status_code=status.HTTP_200_OK)
async def get_my_clients(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Get all clients created by the current admin user."""
    return await Database.get_clients_by_user_id(session, current_user.id)


@router.get("/{client_id}", response_model=ClientRead, status_code=status.HTTP_200_OK)
async def get_client(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Get a specific client by ID."""
    client = await Database.get(session, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientRead, status_code=status.HTTP_200_OK)
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Update a client."""
    return await Database.update(session, client_id, client_update)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Delete a client (soft delete)."""
    from src.db.model.client import Client
    await Database.delete(session, client_id, Client, ClientUpdate)


@router.post("/login")
async def client_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """Login endpoint for clients."""
    # Get client by email
    client = await Database.get_client_by_email(session, form_data.username)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, client.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if client is disabled
    if client.disabled:
        raise HTTPException(status_code=400, detail="Client account is disabled")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": client.email, "type": "client"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "client": {
            "id": client.id,
            "name": client.name,
            "email": client.email
        }
    }
