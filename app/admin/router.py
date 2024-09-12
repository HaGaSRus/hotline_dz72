from fastapi import APIRouter, status, Depends, Body
from fastapi_versioning import version
from app.auth.auth import get_password_hash, pwd_context
from app.dao.dao import UsersDAO, UsersRolesDAO
from app.dao.dependencies import get_current_admin_user
from app.exceptions import UserEmailAlreadyExistsException, UserNameAlreadyExistsException, UserCreated, UserChangeRole, \
    DeleteUser, UserNotFoundException, PermissionDeniedException, UpdateUser
from app.logger.logger import logger
from app.users.models import Users
from app.users.schemas import UpdateUserRolesRequest
from app.admin.schemas import SUserAuth, UserIdRequest

router_admin = APIRouter(
    prefix="/auth",
    tags=["Админка"],
)


@router_admin.post("/register", status_code=status.HTTP_201_CREATED)
@version(1)
async def register_user(user_data: SUserAuth, current_user: Users = Depends(get_current_admin_user)):
    users_dao = UsersDAO()
    users_roles_dao = UsersRolesDAO()

    # Проверяем, существует ли уже пользователь с таким username или email
    existing_user_by_username = await users_dao.find_one_or_none(username=user_data.username)
    existing_user_by_email = await users_dao.find_one_or_none(email=user_data.email)

    if existing_user_by_username:
        raise UserNameAlreadyExistsException
    if existing_user_by_email:
        raise UserEmailAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)

    new_user = await users_dao.add(
        username=user_data.username,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    if new_user:
        await users_roles_dao.add(user_id=new_user.id, role_name="user")

    raise UserCreated


@router_admin.post("/update-admin", status_code=status.HTTP_200_OK)
@version(1)
async def update_user(
        user_id: int = Body(..., description="ID пользователя для обновления"),
        username: str = Body(None, description="Новое имя пользователя"),
        email: str = Body(None, description="Новый email пользователя"),
        password: str = Body(None, description="Новый пароль пользователя"),
        firstname: str = Body(None, description="Новое имя пользователя"),
        lastname: str = Body(None, description="Новая фамилия пользователя"),
        current_user: Users = Depends(get_current_admin_user)
):
    """Обновление информации о пользователе"""
    users_dao = UsersDAO()

    # Проверка, существует ли такой пользователь
    user_to_update = await users_dao.find_one_or_none(id=user_id)
    if not user_to_update:
        raise UserNotFoundException

    # Проверяем, что текущий пользователь имеет право обновлять данные
    if user_to_update.id != current_user.id:
        raise PermissionDeniedException

    if username:
        existing_user = await users_dao.find_one_or_none(username=username)
        if existing_user and existing_user.id != user_to_update.id:
            raise UserNameAlreadyExistsException

    if email:
        existing_user = await users_dao.find_one_or_none(email=email)
        if existing_user and existing_user.id != user_to_update.id:
            raise UserEmailAlreadyExistsException

    hashed_password = pwd_context.hash(password) if password else None

    # Логирование перед обновлением
    logger.info(
        f"Обновление пользователя с id={user_to_update.id}: username={username}, email={email},"
        f" hashed_password={hashed_password is not None}")

    # Обновляем данные пользователя
    await users_dao.update(
        model_id=user_to_update.id,
        username=username,
        email=email,
        hashed_password=hashed_password,
        firstname=firstname,
        lastname=lastname,
    )

    return UpdateUser


@router_admin.post("/update-roles", status_code=status.HTTP_200_OK)
@version(1)
async def update_user_roles(
        user_request: UserIdRequest,
        update_roles: UpdateUserRolesRequest,
        current_user: Users = Depends(get_current_admin_user),
):
    """Изменение или добавление ролей пользователю. Только для администратора"""
    users_roles_dao = UsersRolesDAO()

    # Очистка текущих ролей и добавление новых ролей
    await users_roles_dao.clear_roles(user_request.user_id)  # Очистка ролей
    await users_roles_dao.add_roles(user_request.user_id, role_names=update_roles.roles)  # Добавление новых ролей

    return UserChangeRole


@router_admin.post("/delete", status_code=status.HTTP_200_OK)
@version(1)
async def delete_user(user_request: UserIdRequest, current_user: Users = Depends(get_current_admin_user)):
    """Удаление пользователя. Только для администратора"""
    users_dao = UsersDAO()
    await users_dao.delete(user_request.user_id)
    return DeleteUser



