from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class MembershipRequestWithIdNotFoundException(AppException):
    def __init__(self, request_id: int):
        super().__init__(
            detail=f"Membership request with ID {request_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
