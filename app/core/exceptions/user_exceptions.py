from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UserWithIdNotFoundException(AppException):
    def __init__(self, user_id: int):
        super().__init__(
            detail=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserWithEmailNotFoundException(AppException):
    def __init__(self, email: str):
        super().__init__(
            detail=f"User with email {email} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            detail=f"User with email '{email}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class UserUpdateException(AppException):
    def __init__(self, user_id: int):
        super().__init__(
            detail=f"Error updating user {user_id}: Wrong data",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
