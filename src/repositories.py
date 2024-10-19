from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    model = None

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create_instance(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_instance(self, *args, **kwargs):
        pass
