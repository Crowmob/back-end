class RepositoryError(Exception):
    pass


class RepositoryIntegrityError(RepositoryError):
    pass


class RepositoryDataError(RepositoryError):
    pass


class RepositoryDatabaseError(RepositoryError):
    pass


class RedisRepositoryError(RepositoryError):
    pass


class RedisRepositoryScanError(RepositoryError):
    pass


class RedisRepositoryMultipleFetchError(RepositoryError):
    pass
