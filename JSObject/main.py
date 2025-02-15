from typing import Type, is_typeddict, Optional, Any, Self, TypeVar, TypedDict, Generic
from collections.abc import Callable, Hashable
from types import FunctionType

__all__ = "annotation", "Field", "JSObject"


Obj = TypeVar("Obj", bound=Callable[..., None])
Instance = TypeVar("Instance", bound=object)
Owner = TypeVar("Owner", bound=Type)


def annotation(obj: Obj) -> Obj:
    obj.__annotated__ = True
    return obj


def isTypedDict(obj: dict, typedDict: Type) -> bool:
    return isinstance(obj, dict) and is_typeddict(typedDict) and set(obj).symmetric_difference(getattr(typedDict, "__annotations__")).issubset(getattr(typedDict, "__optional_keys__"))


class Field(Generic[Instance, Owner]):
    def __init__(self, alias: Optional[str] = None, default: Optional[Any] = None, base: Optional[Callable] = None) -> None:
        self.alias = alias
        self.default = default
        self.base = base

    def __repr__(self) -> str:
        return "{name}({value})".format(
            name=self.__class__.__name__,
            value=", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        )

    def __set_name__(self, owner: Owner, name: str) -> None:
        if self.alias is None:
            self.alias = name
        self.name = name

    def __get__(self, instance: Instance, owner: Owner) -> Any:
        return instance.__dict__.get(self.name)

    def __set__(self, instance: Instance, value: Any) -> None:
        match value, self.default:
            case None, None:
                instance.pop(self.alias, None)
                instance.__dict__[self.name] = None
            case None, _:
                if self.alias in instance:
                    instance.pop(self.alias, None)
                    instance.__dict__[self.name] = None
                else:
                    instance[self.alias] = self.default
                    instance.__dict__[self.name] = self.default
            case _:
                instance[self.alias] = value
                instance.__dict__[self.name] = value if self.base is None and not isinstance(value, JSObject) else self.base(value)


class PreparedDict(dict):
    __slots__ = "annotatedDict",

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.annotatedDict: dict[str, list[FunctionType]] = {"__annotated__": []}

    def __setitem__(self, key: Hashable, value: Any) -> None:
        if hasattr(value, "__annotated__") and key == "__init__":
            self.annotatedDict[key := "__annotated__"].append(value)
            value = self.annotatedDict[key]
        super().__setitem__(key, value)


class JSObject(type):
    @classmethod
    def __prepare__(mcs, name: str, bases: tuple[Type]) -> PreparedDict:
        return PreparedDict()

    def __new__(mcs, name: str, bases: tuple[Type], attrs: dict) -> Type:
        attrs["__repr__"] = mcs.__repr__
        attrs["__based_on__"] = getattr(mcs, "__based_on__")
        return super().__new__(mcs, name, (dict, ), attrs)

    def __call__(cls, *args, **kwargs) -> object:
        if not getattr(cls, "__init_vars__", False):
            if (typedDict := getattr(cls, "__based_on__", None)) is None:
                raise ValueError(f"Specify appropriate TypedDict: class {cls.__name__}(metaclass={cls.__class__.__name__}[TypedDict])")
            annotations = cls.__dict__.get("__annotated__")
            if annotations is None:
                raise AttributeError(f"class {cls.__name__} must contain at least one __init__ method")
            initFunc: FunctionType = next(filter(lambda item: not ((a := item.__annotations__, a.pop("return", None))[0] and typedDict in a.values()), annotations), None)
            if initFunc is None:
                raise AttributeError(f"{cls.__name__}.__init__ missing TypedDict annotation")
            initVars = list(initFunc.__code__.co_varnames[1:])
            if sorted(initVars) != sorted(dict(fields := list(filter(lambda item: isinstance(item[1], Field), cls.__dict__.items()))).keys()):  # type: ignore
                raise AttributeError(f"{cls.__name__}.__init__ signature does not match Field names")
            setattr(cls, "__init_vars__", initVars)
            setattr(cls, "__fields__", fields)
            delattr(cls, "__annotated__")
        instance = super().__call__()
        if (len(args) + len(kwargs)) == 1 and isTypedDict(dct := [*args, *(kwargs.values())][0], getattr(cls, "__based_on__")):
            for name, field in getattr(cls, "__fields__"):
                setattr(instance, name, dct.get(field.alias))
        else:
            args = iter(args)
            for name in getattr(cls, "__init_vars__"):
                value = next(args, None) if name not in kwargs.keys() else kwargs.get(name)
                setattr(instance, name, value)
        return instance

    def __class_getitem__(mcs, typeDict: Type) -> Self:
        if not is_typeddict(typeDict):
            raise AttributeError(f"{getattr(typeDict, '__name__', typeDict)} object must be of type {TypedDict.__qualname__}, not {type(typeDict)}")
        mcs.__based_on__ = typeDict
        return mcs

    def __repr__(self) -> str:
        return "{name}({value})".format(
            name=self.__class__.__name__,
            value=", ".join(f"{k}={v}" for k, v in self.__dict__.items() if v is not None)
        )
