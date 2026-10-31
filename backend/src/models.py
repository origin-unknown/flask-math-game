import secrets, string
from tasklib.answer import check_answer
from tasklib.config import TASK_CONFIGS
from tasklib.generators import choose_task_by_name
from tasklib.task import TaskLike, TaskType

from threading import Lock, RLock
from typing import Any, ClassVar, Self


class User:
	def __init__(self, sid: str, username: str, points: int = 0) -> None:
		self._sid = sid
		self._username = username
		self._points = points
		self._lock = Lock()

	@property
	def sid(self) -> str:
		return self._sid
	
	@property
	def username(self) -> str:
		return self._username
	
	@property
	def points(self) -> int:
		with self._lock:
			return self._points
	
	@points.setter
	def points(self, value: int) -> None:
		with self._lock:
			self._points = value

	def add_points(self, amount: int) -> None:
		with self._lock:
			self._points += amount

	def remove(self) -> None:
		with type(self)._user_lock:
			type(self).all_users.pop(self.sid, None)

	_user_lock: ClassVar[Lock] = Lock()
	all_users: ClassVar[dict[str, User]] = {}

	@classmethod
	def create(cls, sid: str, username: str, points: int=0) -> Self:
		with cls._user_lock:
			obj = cls(sid, username, points)
			cls.all_users[sid] = obj
			return obj

	@classmethod
	def find_by_sid(cls, sid: str) -> User | None:
		with cls._user_lock:
			return cls.all_users.get(sid)

	@classmethod
	def find_by_username(cls, username: str) -> User | None:
		with cls._user_lock:
			return next((u for u in cls.all_users.values() if u.username == username), None)


MAX_ROOM_MEMBERS = 2

class Room:

	# Separate based on the subclass.
	# def __init_subclass__(cls, **kwargs: Any) -> None:
	# 	super().__init_subclass__(**kwargs)
	# 	cls.all_rooms = {}

	def __init__(self, code: str) -> None:
		self._code = code
		self._members: dict[str, User] = {} 
		self._lock = RLock() 

	def __len__(self) -> int:
		return len(self._members)

	@property
	def code(self) -> str:
		return self._code

	@property
	def is_closed(self) -> bool:
		return not self.is_open

	@property
	def is_empty(self) -> bool:
		return len(self) == 0

	@property
	def is_open(self) -> bool:
		return len(self) < MAX_ROOM_MEMBERS

	@property
	def members(self) -> dict[str, User]:
		with self._lock:
			return self._members.copy()
	
	@property
	def task_type(self) -> TaskType:
		raise NotImplementedError

	def add_member(self, user: User) -> bool:
		with self._lock:
			if not self.is_open or self.is_member(user):
				return False

			self._members[user.sid] = user
			return True

	def is_member(self, user: User) -> bool:
		with self._lock:
			return user.sid in self._members

	def remove_member(self, user: User) -> None:
		with self._lock:
			self._members.pop(user.sid, None)

	def remove(self) -> None:
		with type(self)._room_lock:
			type(self).all_rooms.pop(self.code, None)

	_room_lock: ClassVar[RLock] = RLock()
	all_rooms: ClassVar[dict[str, Any]] = {}

	@classmethod
	def create(cls, *args: Any, **kwargs: Any) -> Self:
		with cls._room_lock:
			key = cls.generate_room_code()
			obj =  cls(key, *args, **kwargs)
			cls.all_rooms[key] = obj
			return obj

	@classmethod
	def generate_room_code(cls, size: int=8) -> str:
		alphanum = string.ascii_letters + string.digits
		return ''.join(secrets.choice(alphanum) for _ in range(size))

	@classmethod
	def find_by_code(cls, code: str) -> Self | None:
		with cls._room_lock:
			return cls.all_rooms.get(code)

	@classmethod
	def find_open_room(cls) -> Self | None:
		with cls._room_lock:
			return next((r for r in cls.all_rooms.values() if r.is_open), None)

	@classmethod
	def find_open_room_by_type(cls, selection: str) -> Self | None:
		with cls._room_lock:
			return next(
				(r for r in cls.all_rooms.values() if r.selection == selection and r.is_open), 
				None
			)

MAX_TASK_ATTEMPTS = 3
MAX_ROUNDS = 10

class Match(Room):
	def __init__(self, code: str, selection: str = TaskType.RANDOM.value) -> None:
		super().__init__(code)

		if (
			selection != TaskType.RANDOM.value
			and selection not in TASK_CONFIGS
		):
			raise ValueError(
				f"Unknown task selection: {selection}"
			)

		self._attempts = 0
		self._round = 0
		self._task: TaskLike | None = None 
		self._selection = selection
		self._ready: set[str] = set()

	@property
	def ready_members(self) -> set[str]:
		with self._lock:
			return self._ready.copy()

	@property 
	def round(self) -> int:
		with self._lock:
			return self._round

	@property
	def task(self) -> Task | None:
		with self._lock:
			return self._task

	@property 
	def is_finished(self) -> bool:
		return self.round >= MAX_ROUNDS
	
	@property
	def attempts(self) -> int:
		with self._lock:
			return self._attempts

	@property
	def selection(self) -> str:
		return self._selection

	@property
	def task_type(self) -> TaskType:
		if self._selection == TaskType.RANDOM.value:
			return TaskType.RANDOM

		return TASK_CONFIGS[self._selection].task_type

	@property
	def task_label(self):
		if self._selection == TaskType.RANDOM.value:
			return 'task_labels.random'
		return TASK_CONFIGS.get(self._selection).label

	def _create_task(self) -> TaskLike:
		self._task = choose_task_by_name(self._selection)
		return self._task

	def process(self, user: User, value: str) -> tuple[Task, int, bool, bool]:
		with self._lock:
			task = self._task or self._create_task()

			success = check_answer(task, value)

			self._attempts += 1

			task_finished = success or self._attempts >= MAX_TASK_ATTEMPTS

			if task_finished:
				self._attempts = 0
				self._round += 1

				if self.round < MAX_ROUNDS:
					task = self._create_task()

			finished = self._round >= MAX_ROUNDS

		if success:
			user.add_points(10)

		return task, self._attempts, success, finished

	def ready(self, user: User) -> tuple[bool, TaskLike | None]:
		with self._lock:
			if user.sid not in self._members:
				return False, None

			if 0 < self._round < MAX_ROUNDS:
				return False, None

			self._ready.add(user.sid)

			all_ready = (
				len(self._members) == MAX_ROOM_MEMBERS
				and len(self._ready) == len(self._members)
			)

			if not all_ready:
				return False, None

			self._reset()
			self.reset_scores()
			task = self._create_task()

			return True, task

	def remove_member(self, user: User) -> None:
		with self._lock:
			super().remove_member(user)
			self._ready.discard(user.sid)
	
	def _reset(self) -> None:
		self._round = 0
		self._attempts = 0
		self._task = None
		self._ready.clear()

	def reset_scores(self) -> None:
		for m in self._members.values():
			m.points = 0

	def restart(self) -> TaskLike:
		with self._lock:
			self._reset()
			self.reset_scores()
			return self._create_task()

	@classmethod
	def find_or_create(cls, selection: str | None = TaskType.RANDOM.value) -> Self:
		with cls._room_lock:
			room = next(
				(
					r for r in cls.all_rooms.values()
					if (selection is None or r.selection == selection)
					and r.is_open
				),
				None
			)

			if room is None:
				key = cls.generate_room_code()
				room = cls(key, selection or TaskType.RANDOM.value)
				cls.all_rooms[key] = room

			return room
