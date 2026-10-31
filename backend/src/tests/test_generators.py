import pytest

from tasklib.answer import check_answer, parse_answer
from tasklib.config import Difficulty, TASK_CONFIGS
from tasklib.expressions import (
	Add,
	Constant,
	Divide,
	Multiply,
	Power,
	Subtract,
	Variable,
)
from tasklib.generators import (
	EQUATION_GENERATORS,
	choose_random_task,
	choose_task,
	choose_task_by_name,
	generate_arithmetic_task,
	generate_complex_equation,
	generate_fraction_equation,
	generate_numbers,
	generate_parentheses_equation,
	generate_power_equation,
	generate_simple_equation,
	generate_two_sided_equation,
)
from tasklib.task import (
	EquationTask,
	HiddenSide,
	Task,
	TaskType,
)


# --------------------------------------------------
# 1. All TaskConfigs can be used.
# --------------------------------------------------

@pytest.mark.parametrize(
	"name",
	list(TASK_CONFIGS),
)
def test_choose_task_by_name(name):
	task = choose_task_by_name(name)

	assert isinstance(task, (Task, EquationTask))
	assert task.to_dict()["expr"]
	assert task.to_dict()["latex"]


def test_unknown_task_name():
	with pytest.raises(ValueError):
		choose_task_by_name("does_not_exist")


# --------------------------------------------------
# 2. Arithmetic problems
# --------------------------------------------------

@pytest.mark.parametrize(
	"name",
	[
		"small_addition",
		"mid_addition",
		"large_addition",
		"small_subtraction",
		"mid_subtraction",
		"large_subtraction",
		"small_multiplication",
		"small_division",
		"fraction_reduction",
	],
)
def test_arithmetic_task_is_correct(name):
	task = choose_task_by_name(name)

	assert isinstance(task, Task)

	assert task.check_answer(task.answer)
	assert task.to_dict()["expr"]


@pytest.mark.parametrize(
	"task_type,difficulty",
	[
		(TaskType.ADD, Difficulty.SMALL),
		(TaskType.ADD, Difficulty.MEDIUM),
		(TaskType.ADD, Difficulty.LARGE),
		(TaskType.SUBTRACT, Difficulty.SMALL),
		(TaskType.SUBTRACT, Difficulty.MEDIUM),
		(TaskType.SUBTRACT, Difficulty.LARGE),
		(TaskType.MULTIPLY, Difficulty.SMALL),
		(TaskType.MULTIPLY, Difficulty.MEDIUM),
		(TaskType.MULTIPLY, Difficulty.LARGE),
		(TaskType.DIVIDE, Difficulty.SMALL),
		(TaskType.DIVIDE, Difficulty.MEDIUM),
		(TaskType.DIVIDE, Difficulty.LARGE),
		(TaskType.REDUCE, Difficulty.SMALL),
	],
)
def test_generated_numbers_are_supported(task_type, difficulty):
	a, b = generate_numbers(task_type, difficulty)

	assert isinstance(a, int)
	assert isinstance(b, int)


@pytest.mark.parametrize(
	"name",
	[
		"small_addition",
		"mid_addition",
		"large_addition",
		"small_subtraction",
		"mid_subtraction",
		"large_subtraction",
		"small_multiplication",
		"small_division",
		"fraction_reduction",
	],
)
def test_arithmetic_task_answer_matches_operation(name):
	task = choose_task_by_name(name)

	assert isinstance(task, Task)

	if task.task_type is TaskType.ADD:
		expected = task.left + task.right
	elif task.task_type is TaskType.SUBTRACT:
		expected = task.left - task.right
	elif task.task_type is TaskType.MULTIPLY:
		expected = task.left * task.right
	elif task.task_type is TaskType.DIVIDE:
		expected = task.left // task.right
	elif task.task_type is TaskType.REDUCE:
		from fractions import Fraction
		expected = Fraction(task.left, task.right)
	else:
		pytest.fail(f"Unexpected task type: {task.task_type}")

	assert task.result == expected


# --------------------------------------------------
# 3. Equations: Checking the stored solution
# --------------------------------------------------

@pytest.mark.parametrize(
	"generator",
	[
		generate_simple_equation,
		generate_parentheses_equation,
		generate_complex_equation,
		generate_two_sided_equation,
		generate_fraction_equation,
		generate_power_equation,
	],
)
def test_equation_generator_produces_valid_solution(generator):
	for _ in range(100):
		task = generator()

		assert isinstance(task, EquationTask)

		left = task.left.evaluate(task.solution)
		right = task.right.evaluate(task.solution)

		assert left == right, (
			f"Generator: {generator.__name__}\n"
			f"Gleichung: {task}\n"
			f"Lösung: {task.solution}\n"
			f"Linke Seite: {left}\n"
			f"Rechte Seite: {right}"
		)

		assert task.check_answer(task.solution)


@pytest.mark.parametrize(
	"difficulty",
	list(EQUATION_GENERATORS),
)
def test_equation_difficulty_selects_correct_generator(difficulty):
	task = choose_task(
		next(
			config
			for config in TASK_CONFIGS.values()
			if (
				config.task_type is TaskType.EQUATION
				and config.difficulty is difficulty
			)
		)
	)

	assert isinstance(task, EquationTask)
	assert task.left.evaluate(task.solution) == (
		task.right.evaluate(task.solution)
	)


@pytest.mark.parametrize(
	"name",
	[
		"easy_equations",
		"medium_equations",
		"hard_equations",
	],
)
def test_equation_config_returns_equation_task(name):
	task = choose_task_by_name(name)

	assert isinstance(task, EquationTask)
	assert task.check_answer(task.solution)


# --------------------------------------------------
# 4. Concrete equations: known solutions
# --------------------------------------------------

@pytest.mark.parametrize(
	"left,right,solution",
	[
		(
			Add(Variable(), Constant(94)),
			Constant(112),
			18,
		),
		(
			Subtract(Variable(), Constant(4)),
			Constant(8),
			12,
		),
		(
			Multiply(Constant(3), Variable()),
			Constant(21),
			7,
		),
		(
			Divide(
				Add(Variable(), Constant(2)),
				Constant(3),
			),
			Constant(4),
			10,
		),
	],
)
def test_known_equation_solutions(left, right, solution):
	task = EquationTask(
		left=left,
		right=right,
		solution=solution,
	)

	assert task.left.evaluate(solution) == task.right.evaluate(solution)
	assert task.check_answer(solution)


# --------------------------------------------------
# 5. Parsing and checking answers
# --------------------------------------------------

@pytest.mark.parametrize(
	"value,expected",
	[
		("12", 12),
		("-3", -3),
		(" 18 ", 18),
		("1/2", __import__("fractions").Fraction(1, 2)),
		("-2/3", __import__("fractions").Fraction(-2, 3)),
	],
)
def test_parse_valid_answers(value, expected):
	assert parse_answer(value) == expected


@pytest.mark.parametrize(
	"value",
	[
		"",
		"abc",
		"1/0",
		"1/-2",
		"2/4",
		"1/2/3",
		None,
		12,
	],
)
def test_parse_invalid_answers(value):
	assert parse_answer(value) is None


def test_check_correct_arithmetic_answer():
	task = Task(
		left=7,
		right=5,
		result=12,
		task_type=TaskType.ADD,
	)

	assert check_answer(task, "12")
	assert not check_answer(task, "13")


def test_check_correct_equation_answer():
	task = EquationTask(
		left=Add(Variable(), Constant(94)),
		right=Constant(112),
		solution=18,
	)

	assert check_answer(task, "18")
	assert not check_answer(task, "13")


# --------------------------------------------------
# 6. HiddenSide
# --------------------------------------------------

@pytest.mark.parametrize(
	"hidden_side,expected",
	[
		(HiddenSide.LEFT, 7),
		(HiddenSide.RIGHT, 5),
		(HiddenSide.RESULT, 12),
	],
)
def test_hidden_side_answer(hidden_side, expected):
	task = Task(
		left=7,
		right=5,
		result=12,
		task_type=TaskType.ADD,
		hidden_side=hidden_side,
	)

	assert task.answer == expected
	assert task.check_answer(expected)
	assert not task.check_answer(expected + 1)


# --------------------------------------------------
# 7. Random task selection
# --------------------------------------------------

def test_random_task_returns_supported_task():
	task = choose_random_task()

	assert isinstance(task, (Task, EquationTask))
	assert task.check_answer(task.answer)