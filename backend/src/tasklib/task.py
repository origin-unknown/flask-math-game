from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import Any

from .expressions import Expression


Number = int | Fraction


class HiddenSide(StrEnum):
	LEFT = "left"
	RIGHT = "right"
	RESULT = "result"


class TaskType(StrEnum):
	ADD = "add"
	SUBTRACT = "subtract"
	DIVIDE = "divide"
	MULTIPLY = "multiply"
	REDUCE = "reduce"
	EQUATION = "equation"
	RANDOM = "random"

	# @classmethod
	# def from_string(cls, value: object) -> Self | None:
	# 	if not isinstance(value, str):
	# 		return None
	# 
	# 	try: 
	# 		return cls(value.lower()) 
	# 	except ValueError: 
	# 		return None


OPERATORS_STR: dict[TaskType, str] = {
	TaskType.ADD: "+", 
	TaskType.SUBTRACT: "-", 
	TaskType.MULTIPLY: "*", 
	TaskType.DIVIDE: "/", 
	TaskType.REDUCE: "/", 
}

OPERATORS_LATEX: dict[TaskType, str] = {
	TaskType.ADD: "+", 
	TaskType.SUBTRACT: "-", 
	TaskType.MULTIPLY: r"\cdot", 
	TaskType.DIVIDE: r"\div", 
	TaskType.REDUCE: r"\div", 
}


def format_number(value: Number) -> str:
	if isinstance(value, Fraction):
		if value.denominator == 1:
			return str(value.numerator)
		return (
			rf"\frac{{{value.numerator}}}"
			rf"{{{value.denominator}}}"
		)
	return str(value)


def format_operand(value: Number, operation: str) -> str:
	if value < 0 and operation in ("+", "-"):
		return f"({format_number(value)})"
	return format_number(value)


@dataclass(frozen=True)
class Task:
	left: int
	right: int
	result: Number
	task_type: TaskType
	hidden_side: HiddenSide = HiddenSide.RESULT

	@property
	def operation(self) -> str:
		return OPERATORS_STR[self.task_type]

	@property
	def operation_latex(self) -> str:
		return OPERATORS_LATEX[self.task_type]

	@property
	def answer(self) -> Number:
		return {
			HiddenSide.LEFT: self.left,
			HiddenSide.RIGHT: self.right,
			HiddenSide.RESULT: self.result,
		}[self.hidden_side]

	def check_answer(self, answer: Number) -> bool:
		return answer == self.answer

	def __str__(self) -> str:
		left, right, result = self._parts()
		return f"{left} {self.operation} {right} = {result}"

	def _parts(self) -> tuple[str, str, str]:
		if self.hidden_side is HiddenSide.LEFT:
			return "x", format_operand(self.right, self.operation), str(self.result)

		if self.hidden_side is HiddenSide.RIGHT:
			return str(self.left), "x", str(self.result)

		return (
			str(self.left),
			format_operand(self.right, self.operation),
			"?",
		)

	def to_latex(self) -> str:
		left, right, result = self._parts()
		return f"{left} {self.operation_latex} {right} = {result}"

	def to_dict(self) -> dict[str, Any]:
		# WARNING: 
		# 	The complete result is returned.
		
		# def serialize(value: Any) -> Any:
		# 	if isinstance(value, Fraction):
		# 		return str(value)
		# 	return value

		return {
			# **{key: serialize(value) for key, value in asdict(self).items()},
			"expr": str(self),
			"latex": self.to_latex(),
		}


@dataclass(frozen=True)
class EquationTask:
	left: Expression
	right: Expression
	solution: Number

	@property
	def answer(self) -> Number:
		return self.solution

	def check_answer(self, answer: Number) -> bool:
		try:
			return (
				self.left.evaluate(answer)
				== self.right.evaluate(answer)
			)
		except (ArithmeticError, ValueError):
			return False

	def __str__(self) -> str:
		return f"{self.left} = {self.right}"

	def to_latex(self) -> str:
		return f"{self.left.to_latex()} = {self.right.to_latex()}"

	def to_dict(self) -> dict[str, Any]:
		return {
			"expr": str(self),
			"latex": self.to_latex(),
		}


TaskLike = Task | EquationTask
