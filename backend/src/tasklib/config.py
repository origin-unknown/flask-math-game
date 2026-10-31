from dataclasses import dataclass
from enum import StrEnum

from .task import TaskType


class Difficulty(StrEnum):
	SMALL = "small"
	MEDIUM = "medium"
	LARGE = "large"


@dataclass(frozen=True)
class TaskConfig:
	label: str
	task_type: TaskType
	difficulty: Difficulty

	def to_dict(self, name: str) -> dict[str, str]:
		return {
			"name": name,
			"label": self.label,
			"difficulty": self.difficulty, 
		}


TASK_CONFIGS: dict[str, TaskConfig] = {
	# "Basic Multiplication Table" 
	"small_multiplication": TaskConfig(
		"task_labels.small_multiplication", TaskType.MULTIPLY, Difficulty.SMALL
	),
	# "Basic Multiplication Table (Division)" 
	"small_division": TaskConfig(
		"task_labels.small_division", TaskType.DIVIDE, Difficulty.SMALL
	),
	# "Plus up to 10" 
	"small_addition": TaskConfig(
		"task_labels.small_addition", TaskType.ADD, Difficulty.SMALL
	),
	# "Plus up to 100" 
	"mid_addition": TaskConfig(
		"task_labels.mid_addition", TaskType.ADD, Difficulty.MEDIUM
	),
	# "Plus up to ±100" 
	"large_addition": TaskConfig(
		"task_labels.large_addition", TaskType.ADD, Difficulty.LARGE
	),
	# "Minus to 10" 
	"small_subtraction": TaskConfig(
		"task_labels.small_subtraction", TaskType.SUBTRACT, Difficulty.SMALL
	),
	# "Minus to 100" 
	"mid_subtraction": TaskConfig(
		"task_labels.mid_subtraction", TaskType.SUBTRACT, Difficulty.MEDIUM
	),
	# "Minus to ±100" 
	"large_subtraction": TaskConfig(
		"task_labels.large_subtraction", TaskType.SUBTRACT, Difficulty.LARGE
	),
	# "Reducing fractions" 
	"fraction_reduction": TaskConfig(
		"task_labels.fraction_reduction", TaskType.REDUCE, Difficulty.SMALL
	),
	# "Simple equations" 
	"easy_equations": TaskConfig(
		"task_labels.easy_equations", TaskType.EQUATION, Difficulty.SMALL
	),
	# "Equations with parentheses" 
	"medium_equations": TaskConfig(
		"task_labels.medium_equations", TaskType.EQUATION, Difficulty.MEDIUM,
	),
	# "Difficult equations" 
	"hard_equations": TaskConfig(
		"task_labels.hard_equations", TaskType.EQUATION, Difficulty.LARGE
	),
}
