class RepositoryError(Exception):
    pass


class RepositoryIntegrityError(RepositoryError):
    pass


class RepositoryDataError(RepositoryError):
    pass


class RepositoryDatabaseError(RepositoryError):
    pass
