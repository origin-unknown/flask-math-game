import random
from fractions import Fraction

from .config import Difficulty, TASK_CONFIGS, TaskConfig
from .config import Difficulty, TaskConfig
from .expressions import (
	Add,
	Constant,
	Divide,
	Multiply,
	Power,
	Subtract,
	Variable,
)
from .task import EquationTask, Task, TaskLike, TaskType


def generate_numbers(
	task_type: TaskType,
	difficulty: Difficulty,
) -> tuple[int, int]:
	match task_type, difficulty:
		case TaskType.ADD, Difficulty.SMALL:
			a = random.randint(0, 10)
			return a, random.randint(0, 10 - a)

		case TaskType.ADD, Difficulty.MEDIUM:
			a = random.randint(0, 100)
			return a, random.randint(0, 100 - a)

		case TaskType.ADD, Difficulty.LARGE:
			a = random.randint(-100, 100)
			low = max(-100, -100 - a)
			high = min(100, 100 - a)
			return a, random.randint(low, high)

		case TaskType.SUBTRACT, Difficulty.SMALL:
			a = random.randint(0, 10)
			return a, random.randint(0, a)

		case TaskType.SUBTRACT, Difficulty.MEDIUM:
			a = random.randint(0, 100)
			return a, random.randint(0, a)

		case TaskType.SUBTRACT, Difficulty.LARGE:
			a = random.randint(-100, 100)
			low = max(-100, a - 100)
			high = min(100, a + 100)
			return a, random.randint(low, high)

		case TaskType.MULTIPLY, Difficulty.SMALL:
			return random.randint(1, 10), random.randint(1, 10)

		case TaskType.MULTIPLY, Difficulty.MEDIUM:
			return random.randint(1, 20), random.randint(1, 20)

		case TaskType.MULTIPLY, Difficulty.LARGE:
			return random.randint(1, 100), random.randint(1, 100)

		case TaskType.DIVIDE, Difficulty.SMALL:
			return random.randint(1, 10), random.randint(1, 10)

		case TaskType.DIVIDE, Difficulty.MEDIUM:
			return random.randint(1, 20), random.randint(1, 20)

		case TaskType.DIVIDE, Difficulty.LARGE:
			return random.randint(1, 100), random.randint(1, 100)

		case TaskType.REDUCE, Difficulty.SMALL:
			factor = random.randint(2, 10)
			numerator = random.randint(1, 10)
			denominator = random.randint(2, 10)
			return numerator * factor, denominator * factor

		case _:
			raise ValueError(
				f"Unsupported combination: "
				f"{task_type=}, {difficulty=}"
			)


def generate_arithmetic_task(config: TaskConfig) -> Task:
	# print('arithmetic')

	a, b = generate_numbers(config.task_type, config.difficulty)

	match config.task_type:
		case TaskType.ADD:
			return Task(a, b, a + b, TaskType.ADD)

		case TaskType.SUBTRACT:
			return Task(a, b, a - b, TaskType.SUBTRACT)

		case TaskType.MULTIPLY:
			return Task(a, b, a * b, TaskType.MULTIPLY)

		case TaskType.DIVIDE:
			return Task(a * b, b, a, TaskType.DIVIDE)

		case TaskType.REDUCE:
			return Task(a, b, Fraction(a, b), TaskType.REDUCE)

		case _:
			raise ValueError(f"Not a math problem type: {config.task_type}")


def generate_simple_equation() -> EquationTask:
	# print('simple')

	solution = random.randint(1, 20)
	kind = random.choice(("add", "subtract", "multiply"))

	if kind == "add":
		offset = random.randint(1, 10)
		expression = Add(Variable(), Constant(offset))
		result = Constant(solution + offset)

	elif kind == "subtract":
		offset = random.randint(1, solution)
		expression = Subtract(Variable(), Constant(offset))
		result = Constant(solution - offset)

	else:
		coefficient = random.randint(2, 10)
		expression = Multiply(Constant(coefficient), Variable())
		result = Constant(coefficient * solution)

	if random.choice((True, False)):
		left, right = expression, result
	else:
		left, right = result, expression

	return EquationTask(left, right, solution)


def generate_parentheses_equation() -> EquationTask:
	# print('parentheses')
	
	solution = random.randint(1, 20)
	coefficient = random.randint(2, 5)
	offset = random.randint(1, 10)

	if random.choice((True, False)):
		inner = Add(Variable(), Constant(offset))
		result = coefficient * (solution + offset)
	else:
		inner = Subtract(Variable(), Constant(offset))
		result = coefficient * (solution - offset)

	left = Multiply(Constant(coefficient), inner)

	return EquationTask(left, Constant(result), solution)


def generate_complex_equation() -> EquationTask:
	# print('complex')

	solution = random.randint(-10, 20)
	coefficient = random.randint(2, 6)
	offset = random.randint(1, 10)
	constant = random.randint(-10, 10)

	if random.choice((True, False)):
		inner = Add(Variable(), Constant(offset))
		inner_value = solution + offset
	else:
		inner = Subtract(Variable(), Constant(offset))
		inner_value = solution - offset

	left = Add(
		Multiply(Constant(coefficient), inner),
		Constant(constant),
	)
	result = coefficient * inner_value + constant

	return EquationTask(left, Constant(result), solution)

def generate_two_sided_equation() -> EquationTask:
	# print('two sided')

	solution = random.randint(-10, 20)
	a = random.randint(2, 8)
	b = random.randint(1, a - 1)
	c = random.randint(-10, 10)
	d = (a - b) * solution + c

	left = Add(
		Multiply(Constant(a), Variable()),
		Constant(c),
	)
	right = Add(
		Multiply(Constant(b), Variable()),
		Constant(d),
	)

	return EquationTask(left, right, solution)


def generate_fraction_equation() -> EquationTask:
	# print('fraction')

	solution = random.randint(1, 20)
	offset = random.randint(1, 10)
	divisor = random.randint(2, 5)

	left = Divide(
		Add(Variable(), Constant(offset)),
		Constant(divisor),
	)
	right = Constant(Fraction(solution + offset, divisor))

	return EquationTask(left, right, solution)


def generate_power_equation() -> EquationTask:
	# print('power')

	solution = random.randint(1, 10)
	offset = random.randint(1, 10)

	left = Add(Power(Variable(), 2), Constant(offset))
	right = Constant(solution**2 + offset)

	return EquationTask(left, right, solution)


EQUATION_GENERATORS = {
	Difficulty.SMALL: (generate_simple_equation,),
	Difficulty.MEDIUM: (
		generate_parentheses_equation,
		generate_two_sided_equation,
	),
	Difficulty.LARGE: (
		generate_complex_equation,
		generate_two_sided_equation,
		generate_fraction_equation,
		generate_power_equation,
	),
}


def generate_equation(difficulty: Difficulty) -> EquationTask:
	try:
		generators = EQUATION_GENERATORS[difficulty]
	except KeyError:
		raise ValueError(
			f"Unsupported difficulty level: {difficulty}"
		) from None

	return random.choice(generators)()


def choose_task(config: TaskConfig) -> TaskLike:
	if config.task_type is TaskType.EQUATION:
		return generate_equation(config.difficulty)

	return generate_arithmetic_task(config)


def choose_random_task() -> TaskLike:
	task_type = random.choice([
		TaskType.ADD,
		TaskType.SUBTRACT,
		TaskType.MULTIPLY,
		TaskType.DIVIDE,
		TaskType.REDUCE,
		TaskType.EQUATION,
	])

	configs = [
		config
		for config in TASK_CONFIGS.values()
		if config.task_type is task_type
	]

	config = random.choice(configs)

	return choose_task(config)


def choose_task_by_name(name: str) -> TaskLike:
	if name == TaskType.RANDOM.value:
		return choose_random_task()

	try:
		config = TASK_CONFIGS[name]
	except KeyError:
		raise ValueError(
			f"Unknown task selection: {name}"
		) from None

	return choose_task(config)
