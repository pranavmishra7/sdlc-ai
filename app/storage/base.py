from abc import ABC, abstractmethod

class BaseStore(ABC):
    @abstractmethod
    def save(self, job_id: str, data: dict):
        pass

    @abstractmethod
    def load(self, job_id: str) -> dict:
        pass
