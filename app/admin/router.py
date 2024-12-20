from typing import Optional, List
from fastapi import APIRouter, status, Depends, Body
from fastapi_versioning import version
from app.auth.auth import get_password_hash, pwd_context
from app.dao.dao import UsersDAO, UsersRolesDAO
from app.dao.dependencies import get_current_admin_user
from app.exceptions import UserEmailAlreadyExistsException, UserNameAlreadyExistsException, UserCreated, \
    DeleteUser, UserNotFoundException, ErrorUpdatingUser
from app.logger.logger import logger
from app.admin.schemas import SUserAuth, UserIdRequest

router_admin = APIRouter(
    prefix="/auth",
    tags=["Админка"],

    dependencies=[Depends(get_current_admin_user)])


@router_admin.post("/register", status_code=status.HTTP_201_CREATED, summary="Форма регистрации нового пользователя ")
@version(1)
async def register_user(user_data: SUserAuth):
    """Логика регистрации нового пользователя админом"""
    users_dao = UsersDAO()
    users_roles_dao = UsersRolesDAO()

    existing_user = await users_dao.find_by_username_or_email(
        username=user_data.username,
        email=user_data.email
    )

    if existing_user:
        if existing_user.username == user_data.username:
            raise UserNameAlreadyExistsException
        if existing_user.email == user_data.email:
            raise UserEmailAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)

    new_user = await users_dao.add(
        username=user_data.username,
        firstname=user_data.firstname,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    if new_user:
        await users_roles_dao.add(user_id=new_user.id, role_name="user")

    raise UserCreated


@router_admin.post("/update-admin", status_code=status.HTTP_200_OK, summary="Обновление данных пользователя админом")
@version(1)
async def update_user(
        user_id: int = Body(..., description="ID пользователя для обновления"),
        username: str = Body(None, description="Новое имя пользователя"),
        email: str = Body(None, description="Новый email пользователя"),
        password: str = Body(None, description="Новый пароль пользователя"),
        firstname: str = Body(None, description="Новое имя пользователя"),
        update_roles: Optional[List[str]] = Body(None, description="Список новых ролей для пользователя"),
):
    """Обновление информации о пользователе и его ролей"""
    users_dao = UsersDAO()
    users_roles_dao = UsersRolesDAO()

    user_to_update = await users_dao.find_one_or_none(id=user_id)
    if not user_to_update:
        raise UserNotFoundException

    if username:
        existing_user = await users_dao.find_one_or_none(username=username)
        if existing_user and existing_user.id != user_to_update.id:
            raise UserNameAlreadyExistsException

    if email:
        existing_user = await users_dao.find_one_or_none(email=email)
        if existing_user and existing_user.id != user_to_update.id:
            raise UserEmailAlreadyExistsException

    hashed_password = pwd_context.hash(password) if password else None

    try:
        await users_dao.update(
            model_id=user_to_update.id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            firstname=firstname,
        )
    except Exception as e:
        logger.warning(f"Ошибка при обновлении пользователя: {e}")
        raise ErrorUpdatingUser

    if update_roles is not None:
        update_roles = [role for role in update_roles if role]

    if not update_roles:
        update_roles = ['user']

    await users_roles_dao.clear_roles(user_id)
    await users_roles_dao.add_roles(user_id, role_names=update_roles)

    return await users_dao.get_user_with_roles(user_id)


@router_admin.post("/delete", status_code=status.HTTP_200_OK, summary="Удаление пользователя по id")
@version(1)
async def delete_user(user_request: UserIdRequest):
    """Удаление пользователя. Только для администратора"""
    users_dao = UsersDAO()
    await users_dao.delete(user_request.user_id)
    return DeleteUser



