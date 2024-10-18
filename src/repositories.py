from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    model = None

    @abstractmethod
    async def get_list_of_instances(self,  *args, **kwargs):
        pass

    @abstractmethod
    async def create_instance(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_instance(self, *args, **kwargs):
        pass
