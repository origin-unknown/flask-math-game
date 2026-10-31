from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction

Number = int | Fraction


def format_number_latex(value: Number) -> str:
	if isinstance(value, Fraction):
		if value.denominator == 1:
			return str(value.numerator)
		return rf"\frac{{{value.numerator}}}{{{value.denominator}}}"
	return str(value)


def format_number_str(value: Number) -> str:
	if isinstance(value, Fraction):
		if value.denominator == 1:
			return str(value.numerator)
		return f"{value.numerator}/{value.denominator}"
	return str(value)


class Expression(ABC):
	@property
	@abstractmethod
	def precedence(self) -> int:
		...

	@abstractmethod
	def evaluate(self, x: Number) -> Number:
		...

	@abstractmethod
	def to_latex(self) -> str:
		...

	@abstractmethod
	def to_str(self) -> str:
		...

	def __str__(self) -> str:
		return self.to_str()


def format_child_latex(expression: Expression, parent_precedence: int) -> str:
	text = expression.to_latex()
	if expression.precedence < parent_precedence:
		return rf"\left({text}\right)"
	return text


def format_child_str(expression: Expression, parent_precedence: int) -> str:
	text = expression.to_str()
	if expression.precedence < parent_precedence:
		return f"({text})"
	return text


@dataclass(frozen=True)
class Constant(Expression):
	value: Number

	@property
	def precedence(self) -> int:
		return 100

	def evaluate(self, x: Number) -> Number:
		return self.value

	def to_latex(self) -> str:
		return format_number_latex(self.value)

	def to_str(self) -> str:
		return format_number_str(self.value)


@dataclass(frozen=True)
class Variable(Expression):
	name: str = "x"

	@property
	def precedence(self) -> int:
		return 100

	def evaluate(self, x: Number) -> Number:
		return x

	def to_latex(self) -> str:
		return self.name

	def to_str(self) -> str:
		return self.name


@dataclass(frozen=True)
class Add(Expression):
	left: Expression
	right: Expression

	@property
	def precedence(self) -> int:
		return 10

	def evaluate(self, x: Number) -> Number:
		return self.left.evaluate(x) + self.right.evaluate(x)

	def to_latex(self) -> str:
		left = format_child_latex(self.left, self.precedence)
		right = format_child_latex(self.right, self.precedence)

		if isinstance(self.right, Constant) and self.right.value < 0:
			return f"{left} - {format_number_latex(abs(self.right.value))}"

		return f"{left} + {right}"

	def to_str(self) -> str:
		left = format_child_str(self.left, self.precedence)
		right = format_child_str(self.right, self.precedence)

		if isinstance(self.right, Constant) and self.right.value < 0:
			return f"{left} - {format_number_str(abs(self.right.value))}"

		return f"{left} + {right}"


@dataclass(frozen=True)
class Subtract(Expression):
	left: Expression
	right: Expression

	@property
	def precedence(self) -> int:
		return 10

	def evaluate(self, x: Number) -> Number:
		return self.left.evaluate(x) - self.right.evaluate(x)

	def to_latex(self) -> str:
		left = format_child_latex(self.left, self.precedence)

		if isinstance(self.right, Constant) and self.right.value < 0:
			return f"{left} + {format_number_latex(abs(self.right.value))}"

		right = self.right.to_latex()
		if self.right.precedence <= self.precedence:
			right = rf"\left({right}\right)"

		return f"{left} - {right}"

	def to_str(self) -> str:
		left = format_child_str(self.left, self.precedence)

		if isinstance(self.right, Constant) and self.right.value < 0:
			return f"{left} + {format_number_str(abs(self.right.value))}"

		right = self.right.to_str()
		if self.right.precedence <= self.precedence:
			right = f"({right})"

		return f"{left} - {right}"


@dataclass(frozen=True)
class Multiply(Expression):
	left: Expression
	right: Expression

	@property
	def precedence(self) -> int:
		return 20

	def evaluate(self, x: Number) -> Number:
		return self.left.evaluate(x) * self.right.evaluate(x)

	def to_latex(self) -> str:
		left = format_child_latex(self.left, self.precedence)
		right = format_child_latex(self.right, self.precedence)

		if isinstance(self.left, Constant) and isinstance(self.right, Variable):
			return f"{left}{right}"

		if isinstance(self.left, Constant) and isinstance(self.right, (Add, Subtract)):
			return f"{left}{right}"

		return f"{left} \\cdot {right}"

	def to_str(self) -> str:
		left = format_child_str(self.left, self.precedence)
		right = format_child_str(self.right, self.precedence)

		if isinstance(self.left, Constant) and isinstance(self.right, Variable):
			return f"{left}{right}"

		if isinstance(self.left, Constant) and isinstance(self.right, (Add, Subtract)):
			return f"{left}{right}"

		# Nutzt '*' statt '\cdot' für die Textausgabe
		return f"{left} * {right}"


@dataclass(frozen=True)
class Divide(Expression):
	left: Expression
	right: Expression

	@property
	def precedence(self) -> int:
		return 20

	def evaluate(self, x: Number) -> Number:
		numerator = self.left.evaluate(x)
		denominator = self.right.evaluate(x)

		if denominator == 0:
			raise ZeroDivisionError("Division durch null")

		return Fraction(numerator, denominator)

	def to_latex(self) -> str:
		return rf"\frac{{{self.left.to_latex()}}}{{{self.right.to_latex()}}}"

	def to_str(self) -> str:
		left = format_child_str(self.left, self.precedence)
		right = format_child_str(self.right, self.precedence)
		# Nutzt '/' statt der LaTeX-Bruchdarstellung
		return f"{left} / {right}"


@dataclass(frozen=True)
class Power(Expression):
	left: Expression
	exponent: int

	@property
	def precedence(self) -> int:
		return 30

	def evaluate(self, x: Number) -> Number:
		return self.left.evaluate(x) ** self.exponent

	def to_latex(self) -> str:
		left = format_child_latex(self.left, self.precedence)
		return f"{left}^{{{self.exponent}}}"

	def to_str(self) -> str:
		left = format_child_str(self.left, self.precedence)
		return f"{left}^{self.exponent}"
