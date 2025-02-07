from typing import Type, Optional, Any, TypeVar, Generic
from types import FunctionType
from functools import reduce

__all__ = "Private", "ReadOnly"


Instance = TypeVar("Instance", bound=object)
Owner = TypeVar("Owner", bound=Type)


def merge(classes: tuple[Type], ignored: Optional[dict] = None) -> dict:
    if ignored is None:
        ignored = {}
    return reduce(lambda x, y: x | ((({}, ignored.update(getattr(y, "__inherited__")))[0] if getattr(y, "__affectInherited__") else {}) if isinstance(y, ReadOnly) else ({} if set(y.__dict__).intersection(ignored) else y.__dict__)) | (merge(y.__bases__, ignored) if y.__bases__[0] is not object else {}), classes, {})


def getClassVars(classDict: dict) -> dict:
    return (d := dict(filter(lambda item: not isinstance(item[1], FunctionType) and item[0] not in type.__dict__, classDict.items())), d.pop("__weakref__", None))[0]


class Private(Generic[Instance, Owner]):
    def __repr__(self) -> str:
        return "{name}({value})".format(
            name=self.__class__.__name__,
            value=", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        )

    def __set_name__(self, owner: Owner, name: str) -> None:
        self.name = name

    def __get__(self, instance: Instance, owner: Owner) -> Any:
        return instance.__dict__.get(self.name)

    def __set__(self, instance: Instance, value: Any) -> None:
        if self.name in instance.__dict__:
            raise SyntaxError(f"Attribute .{self.name} of class {instance.__class__.__name__} instance is {self.__class__.__name__}")
        instance.__dict__[self.name] = value


class ReadOnly(type):
    def __new__(mcs, name: str, bases: tuple[Type], attrs: dict) -> Type:
        setattr(mcs, "attrs", getClassVars(attrs))
        getattr(mcs, "attrs").update({"__inherited__": getClassVars(merge(bases)), "__affectInherited__": getattr(mcs, "__affectInherited__", True), "__repr__": mcs.__repr__})
        return super().__new__(mcs, name, bases, getattr(mcs, "attrs"))

    def __call__(cls, *args, **kwargs) -> Type:
        return cls

    def __class_getitem__(mcs, affectInherited: bool = True):
        if not isinstance(affectInherited, bool):
            raise AttributeError(f"{getattr(affectInherited, '__name__', affectInherited)} object must be of type {bool.__qualname__}, not {type(affectInherited)}")
        setattr(mcs, "__affectInherited__", affectInherited)
        return mcs

    def __repr__(self) -> str:
        return "{name}({value})".format(
            name=self.__class__.__name__,
            value=", ".join(f"{k}={v}" for k, v in self.__dict__.items() if v is not None)
        )

    def __setattr__(self, key: str, value: Any) -> None:
        if not getattr(self, "__affectInherited__") and key in getattr(self, "__inherited__", ()):
            return super().__setattr__(key, value)
        raise SyntaxError(f"Attribute .{key} of {self.__name__} class is {self.__class__.__name__}")

