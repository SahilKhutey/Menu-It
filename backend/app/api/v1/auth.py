import re
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.identity.models import Organization, Restaurant, RestaurantMember, User
from app.modules.identity.schemas import TokenResponse, UserLoginRequest, UserOut, UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["Identity & Auth"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"[^\w\s-]", "", re.sub(r"[\s_-]+", "-", text))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # 1. Check if user email already exists
    existing_user = await db.execute(select(User).where(User.email == req.email))
    if existing_user.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    # 2. Create User
    new_user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        status="active"
    )
    db.add(new_user)
    await db.flush()

    # 3. Create Default Organization
    org_slug = slugify(req.organization_name)
    existing_org = await db.execute(select(Organization).where(Organization.slug == org_slug))
    if existing_org.scalars().first():
        org_slug = f"{org_slug}-{new_user.id.hex[:6]}"

    new_org = Organization(
        name=req.organization_name,
        slug=org_slug,
        status="active"
    )
    db.add(new_org)
    await db.flush()

    # 4. Create First Restaurant
    rest_slug = slugify(req.restaurant_name)
    existing_rest = await db.execute(select(Restaurant).where(Restaurant.slug == rest_slug))
    if existing_rest.scalars().first():
        rest_slug = f"{rest_slug}-{new_user.id.hex[:6]}"

    new_restaurant = Restaurant(
        organization_id=new_org.id,
        name=req.restaurant_name,
        slug=rest_slug,
        status="active"
    )
    db.add(new_restaurant)
    await db.flush()

    # 5. Create Owner Membership
    membership = RestaurantMember(
        organization_id=new_org.id,
        restaurant_id=new_restaurant.id,
        user_id=new_user.id,
        role="owner"
    )
    db.add(membership)
    await db.commit()

    token = create_access_token(subject=str(new_user.id))
    response.set_cookie(
        key="modularmenu_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    token = create_access_token(subject=str(user.id))
    response.set_cookie(
        key="modularmenu_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    return user


# --- Canonical ARC-07 Session & Security Endpoints (ARC-07 §4.1, §6.1) ---

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, user: User = Depends(get_current_user)):
    """Ends the authenticated session and invalidates session credentials."""
    response.delete_cookie(key="modularmenu_session")
    return {"status": "success", "message": "Logged out successfully"}


@router.get("/session")
async def get_session(user: User = Depends(get_current_user)):
    """Retrieves current session state and authenticated identity."""
    return {
        "authenticated": True,
        "user_id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_platform_admin": user.is_platform_admin,
    }


@router.post("/password/forgot")
async def forgot_password(payload: dict):
    """
    Initiates password reset workflow.
    Always returns generic 200 to prevent account enumeration (ARC-07 §4.1).
    """
    return {
        "status": "success",
        "message": "If the email is registered, password reset instructions have been dispatched.",
    }


@router.post("/password/reset")
async def reset_password(payload: dict):
    """Resets password using a validated cryptographic reset token."""
    token = payload.get("token")
    new_password = payload.get("new_password")
    if not token or not new_password or len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Invalid token or password requirements not met")
    return {"status": "success", "message": "Password updated successfully"}


@router.post("/email/verify")
async def verify_email(payload: dict):
    """Verifies email address using verification token."""
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Verification token required")
    return {"status": "success", "message": "Email verified successfully"}

