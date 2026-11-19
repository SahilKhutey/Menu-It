import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.identity.models import Organization, Restaurant, RestaurantMember, User
from app.modules.identity.schemas import TokenResponse, UserLoginRequest, UserOut, UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["Identity & Auth"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"[^\w\s-]", "", re.sub(r"[\s_-]+", "-", text))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
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
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
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
