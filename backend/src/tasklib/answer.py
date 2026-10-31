from fractions import Fraction
from math import gcd

from .task import Number, TaskLike


def parse_answer(value: object) -> Number | None:
	if not isinstance(value, str):
		return None

	value = value.strip()

	if not value:
		return None

	try:
		if "/" not in value:
			return int(value)

		numerator_text, denominator_text = value.split("/", 1)

		numerator = int(numerator_text.strip())
		denominator = int(denominator_text.strip())

		if denominator <= 0:
			return None

		if gcd(abs(numerator), denominator) != 1:
			return None

		return Fraction(numerator, denominator)

	except (ValueError, ZeroDivisionError):
		return None


def check_answer(task: TaskLike, value: object) -> bool:
	answer = parse_answer(value)

	if answer is None:
		return False

	return task.check_answer(answer)
