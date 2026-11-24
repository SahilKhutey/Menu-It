"""Authentication endpoints for user registration, login, and token rotation (FCD-05 §18)."""

import contextlib
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from menu_it.auth.dependencies import get_current_principal
from menu_it.auth.principal import AuthenticatedPrincipal
from menu_it.authentication.exceptions import (
    AccountLockedError,
    AccountNotActiveError,
    AccountSuspendedError,
    InvalidCredentialsError,
)
from menu_it.authentication.schemas import (
    AuthenticationResponse,
    EmailVerificationRequest,
    LoginRequest,
    PasswordChangeRequest,
    PasswordForgotRequest,
    PasswordResetRequest,
    RegisterRequest,
    ResendVerificationRequest,
    TokenRefreshRequest,
    TokenResponse,
)
from menu_it.authentication.service import AuthenticationService
from menu_it.core.config import get_settings
from menu_it.database.session import get_db_session
from menu_it.identity.exceptions import UserAlreadyExistsError
from menu_it.identity.schemas import UserResponse
from menu_it.recovery.exceptions import InvalidRecoveryTokenError
from menu_it.recovery.service import PasswordRecoveryService
from menu_it.schemas.common import APIResponse, ResponseMetadata
from menu_it.sessions.exceptions import (
    InvalidRefreshTokenError,
    TokenReuseDetectedError,
)
from menu_it.sessions.service import SessionService
from menu_it.verification.exceptions import InvalidVerificationTokenError
from menu_it.verification.service import EmailVerificationService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _meta(req_id_str: str | None) -> ResponseMetadata:
    req_uuid = UUID(int=0)
    if req_id_str:
        with contextlib.suppress(ValueError):
            req_uuid = UUID(req_id_str)
    return ResponseMetadata(request_id=req_uuid)


@router.post(
    "/register",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=APIResponse[UserResponse],
    summary="Self-Service User Registration",
)
async def register(
    payload: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[UserResponse]:
    """Register a new user account with pending verification state."""
    auth_service = AuthenticationService(session)
    try:
        user, _ = await auth_service.register(
            email=payload.email,
            display_name=payload.display_name,
            password=payload.password,
        )
        await session.commit()
        await session.refresh(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        meta=_meta(x_request_id),
    )


@router.post(
    "/login",
    response_model=APIResponse[AuthenticationResponse],
    summary="User Authentication & Token Issuance",
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[AuthenticationResponse]:
    """Authenticate email and password, issuing access JWT and setting refresh cookie."""
    auth_service = AuthenticationService(session)
    settings = get_settings()

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        user, user_session, access_token, refresh_token = await auth_service.login(
            email=payload.email,
            password=payload.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await session.commit()
        await session.refresh(user)
    except AccountLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=str(exc),
        ) from exc
    except AccountSuspendedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except (InvalidCredentialsError, AccountNotActiveError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        ) from exc

    # Set secure HttpOnly refresh cookie
    response.set_cookie(
        key="menu_it_refresh",
        value=refresh_token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/api/v1/auth",
        max_age=settings.auth_refresh_token_ttl_seconds,
        domain=settings.auth_cookie_domain,
    )

    return APIResponse(
        success=True,
        data=AuthenticationResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.auth_access_token_ttl_seconds,
            user=UserResponse.model_validate(user),
            refresh_token=refresh_token,
        ),
        meta=_meta(x_request_id),
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Rotate Refresh Token & Issue Access Token",
)
async def refresh_tokens(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    payload: TokenRefreshRequest | None = None,
    menu_it_refresh: Annotated[str | None, Cookie()] = None,
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[TokenResponse]:
    """Rotate opaque refresh token and issue new access JWT."""
    raw_token = menu_it_refresh or (payload.refresh_token if payload else None)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required.",
        )

    auth_service = AuthenticationService(session)
    settings = get_settings()

    try:
        user_session, access_token, new_refresh_token = await auth_service.refresh_tokens(raw_token)
        await session.commit()
    except TokenReuseDetectedError as exc:
        # Clear compromised cookie immediately
        response.delete_cookie(key="menu_it_refresh", path="/api/v1/auth")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    # Rotate cookie with newly issued refresh token
    response.set_cookie(
        key="menu_it_refresh",
        value=new_refresh_token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/api/v1/auth",
        max_age=settings.auth_refresh_token_ttl_seconds,
        domain=settings.auth_cookie_domain,
    )

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.auth_access_token_ttl_seconds,
            refresh_token=new_refresh_token,
        ),
        meta=_meta(x_request_id),
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict[str, str]],
    summary="Revoke Current Authenticated Session",
)
async def logout(
    response: Response,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Revoke active user session and clear refresh cookie."""
    if principal.session_id:
        session_svc = SessionService(session)
        await session_svc.revoke_session(principal.user_id, principal.session_id)
        await session.commit()

    response.delete_cookie(key="menu_it_refresh", path="/api/v1/auth")
    return APIResponse(
        success=True,
        data={"message": "Logged out successfully."},
        meta=_meta(x_request_id),
    )


@router.post(
    "/logout-all",
    response_model=APIResponse[dict[str, int]],
    summary="Revoke All Sessions for User",
)
async def logout_all(
    response: Response,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, int]]:
    """Revoke all active sessions across all devices."""
    session_svc = SessionService(session)
    count = await session_svc.revoke_all_user_sessions(principal.user_id)
    await session.commit()

    response.delete_cookie(key="menu_it_refresh", path="/api/v1/auth")
    return APIResponse(
        success=True,
        data={"revoked_sessions": count},
        meta=_meta(x_request_id),
    )


@router.post(
    "/email/verify",
    response_model=APIResponse[UserResponse],
    summary="Verify Email Address",
)
async def verify_email(
    payload: EmailVerificationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[UserResponse]:
    """Consume verification token and mark user account verified and active."""
    verification_svc = EmailVerificationService(session)
    try:
        user = await verification_svc.verify_email(payload.token)
        await session.commit()
        await session.refresh(user)
    except InvalidVerificationTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        meta=_meta(x_request_id),
    )


@router.post(
    "/email/resend",
    response_model=APIResponse[dict[str, str]],
    summary="Resend Verification Email",
)
async def resend_verification(
    payload: ResendVerificationRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Idempotently request a new verification token without leaking account existence."""
    verification_svc = EmailVerificationService(session)
    await verification_svc.resend_verification(payload.email)
    await session.commit()

    return APIResponse(
        success=True,
        data={
            "message": "If the account exists and is unverified, a verification link has been sent."
        },
        meta=_meta(x_request_id),
    )


@router.post(
    "/password/forgot",
    response_model=APIResponse[dict[str, str]],
    summary="Initiate Password Recovery",
)
async def forgot_password(
    payload: PasswordForgotRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Initiate password reset workflow without exposing account registration status."""
    recovery_svc = PasswordRecoveryService(session)
    await recovery_svc.create_password_reset_token(payload.email)
    await session.commit()

    return APIResponse(
        success=True,
        data={
            "message": "If the account is eligible, a password recovery link has been dispatched."
        },
        meta=_meta(x_request_id),
    )


@router.post(
    "/password/reset",
    response_model=APIResponse[dict[str, str]],
    summary="Complete Password Recovery",
)
async def reset_password(
    payload: PasswordResetRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Consume reset token, update password hash, and revoke existing sessions."""
    recovery_svc = PasswordRecoveryService(session)
    try:
        await recovery_svc.reset_password(payload.token, payload.new_password)
        await session.commit()
    except InvalidRecoveryTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        data={
            "message": "Password reset successfully. All existing sessions have been terminated."
        },
        meta=_meta(x_request_id),
    )


@router.post(
    "/password/change",
    response_model=APIResponse[dict[str, str]],
    summary="Change Password",
)
async def change_password(
    payload: PasswordChangeRequest,
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> APIResponse[dict[str, str]]:
    """Change user password after verifying current password."""
    auth_service = AuthenticationService(session)
    try:
        await auth_service.change_password(
            user_id=principal.user_id,
            current_password=payload.current_password,
            new_password=payload.new_password,
            current_session_id=principal.session_id,
        )
        await session.commit()
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is not correct.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return APIResponse(
        success=True,
        data={"message": "Password changed successfully."},
        meta=_meta(x_request_id),
    )
