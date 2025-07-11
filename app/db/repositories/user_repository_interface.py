from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    async def get_all_users(self):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    async def create_user(self, user_data):
        pass

    @abstractmethod
    async def update_user(self, user_id: int, update_data):
        pass

    @abstractmethod
    async def delete_user(self, user_id: int):
        pass
