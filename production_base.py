from abc import ABC, abstractmethod
from graph_model import Graph


class Production(ABC):
    _production_registry = []

    @classmethod
    def register(cls, production_class):
        cls._production_registry.append(production_class)
        return production_class

    @classmethod
    def list_registered(cls):
        return [prod_cls() for prod_cls in cls._production_registry]

    @abstractmethod
    def get_left_side(self) -> Graph:
        pass

    @abstractmethod
    def get_right_side(self, matched: Graph, level: int) -> Graph:
        pass
