import random, secrets, string


class User:
	def __init__(self, sid, username, points=0):
		self._sid = sid
		self._username = username
		self._points = points

	@property
	def sid(self):
		return self._sid
	
	@property
	def username(self):
		return self._username
	
	@property
	def points(self):
		return self._points
	
	@points.setter
	def points(self, value):
		self._points = value

	def remove(self):
		del self.__class__.all_users[self.sid]

	all_users = {}

	@classmethod
	def create(cls, sid, username, points=0):
		obj = cls(sid, username, points)
		cls.all_users[sid] = obj
		return obj

	@classmethod
	def find_by_sid(cls, sid):
		return cls.all_users.get(sid)

	@classmethod
	def find_by_username(cls, username):
		for v in cls.all_users.values():
			if v.username == username:
				return v
		return None


MAX_ROOM_MEMBERS = 2

class Room:
	def __init__(self, code):
		self._code = code
		self._members = {} 

	def __len__(self):
		return len(self._members)

	@property
	def code(self):
		return self._code

	@property
	def is_closed(self):
		return not self.is_open

	@property
	def is_empty(self):
		return len(self) == 0

	@property
	def is_open(self):
		return len(self) < MAX_ROOM_MEMBERS

	def add_member(self, user):
		self._members[user.sid] = user

	def is_member(self, user):
		return user.sid in self._members

	def remove_member(self, user):
		del self._members[user.sid]

	def remove(self):
		del self.__class__.all_rooms[self.code]

	all_rooms = {}

	@classmethod
	def create(cls):
		key = cls.generate_room_code()
		obj =  cls(key)
		cls.all_rooms[key] = obj
		return obj

	@classmethod
	def generate_room_code(cls, size=8):
		alphanum = string.ascii_letters + string.digits
		return ''.join(secrets.choice(alphanum) for _ in range(size))

	@classmethod
	def find_by_code(cls, code):
		return cls.all_rooms.get(code)

	@classmethod
	def find_open_room(cls):
		for v in cls.all_rooms.values():
			if v.is_open: 
				return v
		return None


MAX_TASK_ATTEMPTS = 3

class _Task:
	def __init__(self, a, b):
		self.a = a
		self.b = b
		self.c = a * b 

	def check(self, num):
		return num == self.c

	def _asdict(self):
		return {
			'a': self.a, 
			'b': self.b, 
			'c': self.c
		}


class Match(Room):
	def __init__(self, code):
		super().__init__(code)
		self._attempts = 0
		self._task = None 

	@property
	def attemmpts(self):
		return self._attempts
	
	@attemmpts.setter
	def attempts(self, value):
		self._attempts = value

	def create_task(self):
		self._task = _Task(
			random.randint(0, 10), 
			random.randint(0, 10)
		)
		return self._task

	def process(self, num):
		success = self._task.check(num)
		if success:
			self._task = self.create_task()
			self.attempts = 0
		else:
			self.attempts += 1 
			if self.attempts >= MAX_TASK_ATTEMPTS:
				self._task = self.create_task()
				self.attempts = 0 
		return self._task, self.attempts, success

	def reset_points(self):
		for m in self._members.values():
			m.points = 0
