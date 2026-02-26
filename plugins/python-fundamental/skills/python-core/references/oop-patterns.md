# OOP Patterns

Python supports object-oriented programming with a pragmatic philosophy: use classes when they clarify the code, not as a mandatory structure for everything. Python's OOP model is flexible — it supports single and multiple inheritance, duck typing, and both nominal and structural subtyping.

## Class Basics

A class groups data (attributes) and behavior (methods) together. The `__init__` method initializes instance state. Unlike languages like Java, Python does not have access modifiers — convention uses a single leading underscore for "internal" attributes and double underscore for name mangling. The absence of strict privacy reflects Python's trust-the-developer philosophy.

```python
class BankAccount:
    """A simple bank account with deposit and withdrawal."""

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner
        self._balance = balance  # Convention: internal attribute

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> float:
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        return amount

    @property
    def balance(self) -> float:
        return self._balance
```

## Instance, Class, and Static Methods

Instance methods receive `self` and operate on instance state — this is the default and most common type. Class methods receive `cls` and operate on class-level state; they are primarily used as alternative constructors that work correctly with inheritance. Static methods receive neither and are pure utility functions namespaced under the class.

```python
from datetime import date

class Employee:
    retirement_age: int = 65

    def __init__(self, name: str, birth_year: int) -> None:
        self.name = name
        self.birth_year = birth_year

    def years_until_retirement(self) -> int:
        """Instance method — needs self."""
        current_age = date.today().year - self.birth_year
        return max(0, self.retirement_age - current_age)

    @classmethod
    def from_csv(cls, line: str) -> "Employee":
        """Class method — alternative constructor."""
        name, year = line.split(",")
        return cls(name.strip(), int(year.strip()))

    @staticmethod
    def is_valid_year(year: int) -> bool:
        """Static method — no instance or class state needed."""
        return 1900 <= year <= date.today().year
```

## Inheritance and MRO

Python supports multiple inheritance. The Method Resolution Order (MRO) determines which parent's method is called. Python uses the C3 linearization algorithm, which you can inspect via `ClassName.__mro__`. The `super()` function delegates to the next class in the MRO, not necessarily the direct parent. This is essential for cooperative multiple inheritance.

```python
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "Woof"

class GuideDog(Dog):
    def speak(self) -> str:
        base = super().speak()  # Calls Dog.speak()
        return f"{base} (gentle)"

# MRO inspection
print(GuideDog.__mro__)
# (GuideDog, Dog, Animal, object)
```

## Composition Over Inheritance

Deep inheritance hierarchies become rigid and hard to modify. Composition — holding references to other objects — provides more flexibility. Prefer composition when the relationship is "has-a" rather than "is-a". Inheritance works well for genuine type hierarchies (e.g., a circle IS a shape) but poorly for code reuse between unrelated types.

```python
class Engine:
    def __init__(self, horsepower: int) -> None:
        self.horsepower = horsepower

    def start(self) -> str:
        return f"Engine ({self.horsepower}hp) started"

class Car:
    """Car HAS an engine — composition, not inheritance."""

    def __init__(self, model: str, engine: Engine) -> None:
        self.model = model
        self._engine = engine

    def start(self) -> str:
        return f"{self.model}: {self._engine.start()}"
```

## Abstract Base Classes (ABC)

ABCs define interfaces that subclasses must implement. They prevent instantiation of incomplete implementations, catching errors at class creation time rather than at runtime. Use ABCs when you need to enforce a contract across a family of related classes.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

# Shape()  # TypeError — can't instantiate abstract class
```

## Protocol (Structural Subtyping)

Protocols (Python 3.8+, `typing.Protocol`) enable structural subtyping — an object satisfies a Protocol if it has the required attributes and methods, regardless of its inheritance chain. This aligns with Python's duck typing philosophy and is preferable to ABCs when you want to accept any object with a compatible interface without requiring explicit inheritance.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        return "Drawing circle"

class Square:
    def draw(self) -> str:
        return "Drawing square"

def render(shape: Drawable) -> None:
    """Accepts any object with a draw() method."""
    print(shape.draw())

render(Circle())  # Works — Circle has draw()
render(Square())  # Works — Square has draw()
```

## Dataclasses

Dataclasses reduce boilerplate for classes that are primarily data containers. The `@dataclass` decorator auto-generates `__init__`, `__repr__`, and `__eq__`. Optional parameters add ordering (`order=True`), immutability (`frozen=True`), and hashing. Use `field(default_factory=...)` for mutable default values.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

v1 = Version(1, 2, 3)
v2 = Version(1, 3, 0)
print(v1 < v2)  # True — ordering compares field by field
```

## __slots__

By default, Python objects store attributes in a `__dict__` dictionary. `__slots__` replaces this with a fixed set of attribute descriptors, reducing memory usage by ~30-40% per instance. Use `__slots__` for classes that create many instances (e.g., data points in a simulation). The tradeoff is that you cannot add arbitrary attributes at runtime.

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

# p = Point(1.0, 2.0)
# p.z = 3.0  # AttributeError — not in __slots__
```

## Common Dunder Methods

Dunder (double underscore) methods let your objects integrate with Python's syntax and protocols. Implementing them makes your objects work with `print()`, `len()`, `in`, comparisons, iteration, and context management.

```python
class Matrix:
    def __init__(self, rows: list[list[float]]) -> None:
        self._rows = rows

    def __repr__(self) -> str:
        """Unambiguous representation for debugging."""
        return f"Matrix({self._rows!r})"

    def __str__(self) -> str:
        """Human-readable representation."""
        return "\n".join(str(row) for row in self._rows)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return self._rows == other._rows

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> list[float]:
        return self._rows[index]

    def __iter__(self):
        return iter(self._rows)

    def __enter__(self):
        """Context manager entry — enables 'with' statement."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit — cleanup here."""
        return False  # Do not suppress exceptions
```
