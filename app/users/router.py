from typing import List

from fastapi import APIRouter, status, Depends

from app.dao.dao import UsersDAO, UsersRolesDAO

from app.dao.dependencies import get_current_user, get_current_admin_user
from app.users.models import Users
from app.exceptions import UserNameAlreadyExistsException, UserEmailAlreadyExistsException
from app.users.schemas import UserResponse, UpdateUserRequest, UpdateUserRolesRequest
from fastapi_versioning import version

router_users = APIRouter(
    prefix="/users",
    tags=["Пользователи"]
)

@router_users.delete("/delete", status_code=status.HTTP_200_OK)
@version(1)
async def delete_user(user_data: Users = Depends(get_current_admin_user)):
    await UsersDAO.delete(user_data.id)
    return {"message": "Пользователь успешно удален"}


@router_users.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
@version(1)
async def read_users_me(current_user: Users = Depends(get_current_user)):
    user_with_roles = await UsersDAO().get_user_with_roles(current_user.id)
    return user_with_roles


@router_users.get("/all-users", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
@version(1)
async def get_all_users(current_user: Users = Depends(get_current_admin_user)) -> List[UserResponse]:
    """Получение всех пользователей. Доступно только администраторам."""
    # Получение всех пользователей
    users_all = await UsersDAO.find_all()
    return users_all


@router_users.post("/update", status_code=status.HTTP_200_OK, response_model=UpdateUserRequest)
@version(1)
async def update_user(
        update_data: UpdateUserRequest,
        current_user: Users = Depends(get_current_user),
):
    """Обновление информации о пользователе"""
    users_dao = UsersDAO()

    # Проверка, существует ли такой пользователь
    if update_data.username:
        existing_user = await users_dao.find_one_or_none(username=update_data.username)
        if existing_user and existing_user.id != current_user.id:
            raise UserNameAlreadyExistsException

    if update_data.email:
        existing_user = await users_dao.find_one_or_none(email=update_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise UserEmailAlreadyExistsException

    # Обновляем данные пользователя
    updated_user = await users_dao.update(
        model_id=current_user.id,
        username=update_data.username,
        email=update_data.email,
        firstname=update_data.firstname,
        lastname=update_data.lastname,
    )

    return updated_user


@router_users.post("/update-roles", status_code=status.HTTP_200_OK)
@version(1)
async def update_user_roles(
        user_id: int,
        update_roles: UpdateUserRolesRequest,
        current_user: Users = Depends(get_current_admin_user),
):
    """Изменение или добавление ролей пользователю. Только для администратора"""
    users_roles_dao = UsersRolesDAO

    # Очистка текущих ролей при необходимости и добавление новых ролей
    await users_roles_dao.clear_roles(user_id=user_id) # Если необходимо очистить
    await users_roles_dao.add_roles(user_id=user_id, roles_names=update_roles.roles)

    return {"message": "Роли успешно обновлены."}












