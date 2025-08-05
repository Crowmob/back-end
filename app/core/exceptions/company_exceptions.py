from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class CompanyWithIdNotFoundException(AppException):
    def __init__(self, company_id: int):
        super().__init__(
            detail=f"Company with ID {company_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class CompanyUpdateException(AppException):
    def __init__(self, company_id: int):
        super().__init__(
            detail=f"Error updating company {company_id}: Wrong data",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
