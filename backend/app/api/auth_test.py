from fastapi import APIRouter, Depends

from backend.app.core.auth import get_current_user
from backend.app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }