'''
WARNING:
	Use Gunicorn with only one worker to protect locks and class variables. 
	Possible offloading of the models to an in-memory system such as Redis. 
'''

from flask import Flask, render_template, request, session
# from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import MAX_ROUNDS, Match as _Match, Room, User
from tasks import TaskType 
from typing import Any


app = Flask(__name__, 
	static_url_path='', 
)

app.config.from_mapping(
	SECRET_KEY='your secret here', 
	# SESSION_TYPE='filesystem' 
)

# Session(app)

socketio = SocketIO(app,
	manage_session=True, # False
	cors_allowed_origins=[
		'http://127.0.0.1:5000', 
		'http://127.0.0.1:5173',  
	], 
	# cors_credentials=True
)

@app.route('/')
def index():
	return app.send_static_file('index.html')

# @app.route('/dev')
# def dev_index():
# 	session.clear() # deprecated 
# 	return render_template('index.html') 

# The session must be initialized within an endpoint.
# @app.get('/api/init')
# def init_session():
# 	session['_init'] = True
# 	return '', 204


def room_data(room: Room) -> dict[str, Any]:
	return {
		'state': 'open' if room.is_open else 'closed',
		'code': room.code,
		'type': room.task_type.value,
		'members': [
			{
				'sid': member.sid,
				'username': member.username,
				'points': member.points,
			}
			for member in room.members.values()
		],
	}

def member_data(room: Room) -> list[dict[str, Any]]:
	return [
		{
			'sid': m.sid, 
			'username': m.username, 
			'points': m.points, 
			'ready': m.sid in room.ready_members
		}
		for m in room.members.values()
	]


@socketio.on('connect')
def on_connect():
	# session.clear()	# not required
	pass

@socketio.on('disconnect')
def on_disconnect():
	user = User.find_by_sid(request.sid)
	code = session.pop('code', None)

	room = Room.find_by_code(code)

	if room is None:
		user and user.remove()
		return 

	leave_room(room.code)

	if user is not None:
		room.remove_member(user)

	is_empty = room.is_empty
	room_state = room_data(room) if room.is_open else None

	if is_empty:
		room.remove()

	if user is not None:
		emit('message', {'msg': f'{user.username} has left room {room.code}'}, room=room.code)

	if room_state is not None:
		emit('room', room_state, room=room.code)

	user and user.remove()

@socketio.on('join')
def on_join(data):
	if not isinstance(data, dict):
		return

	if session.get('code'):
		return

	username = data.get('username', '').strip()
	roomcode = data.get('roomname', '').strip()
	task_type = TaskType.from_string(data.get('tasktype', ''))

	if not username:
		return

	user = User.find_by_sid(request.sid)
	if user is not None:
		user.remove()

	user = User.create(
		sid=request.sid,
		username=username,
	)

	room = None

	if roomcode:
		room = _Match.find_by_code(roomcode)

		if room is not None and not room.is_open:
			room = None

	if room is None:
		room = _Match.find_or_create(task_type)

	if not room.add_member(user):
		user.remove()
		return

	is_closed = room.is_closed

	if is_closed:
		task = room.restart()
	else:
		task = None

	room_state = room_data(room)

	join_room(room.code)
	session['code'] = room.code

	emit(
		'message',
		{'msg': f'{user.username} has joined room {room.code}'},
		room=room.code,
	)

	emit(
		'room',
		room_state,
		room=room.code,
	)

	emit(
		'user',
		{
			'username': user.username,
			'sid': user.sid,
			'points': user.points,
		},
		to=user.sid,
	)

	if is_closed:
		emit(
			'task',
			{
				'attempts': 0,
				'round': room.round,
				'max_rounds': MAX_ROUNDS,
				'task': task.to_dict(),
				'success': False,
			},
			room=room.code,
		)

@socketio.on('leave')
def on_leave():
	user = User.find_by_sid(request.sid)
	room = Room.find_by_code(session.pop('code', None))

	if user is None or room is None:
		return

	if not room.is_member(user):
		return 

	room.remove_member(user)
	leave_room(room.code)

	is_empty = room.is_empty
	room_state = room_data(room) if room.is_open else None

	is_empty and room.remove()

	room_state and emit('room', room_state, room=room.code)

	emit('user', { 'username': '', 'sid': user.sid, 'points': user.points }, to=user.sid)
	emit('message', {'msg': f'{user.username} has left room {room.code}'}, room=room.code)

	user.remove()


@socketio.on('message')
def room_message(data):
	if not isinstance(data, dict):
		return

	room = Room.find_by_code(session.get('code'))
	if room is None:
		return

	user = User.find_by_sid(request.sid)
	
	if user and room.is_member(user):
		msg = data.get('message', '').strip()
		if not msg:
			return 
		emit('message', {'msg': f'{user.username}: {msg}'}, room=room.code)


@socketio.on('solve')
def on_solve(data):
	if not isinstance(data, dict):
		return

	user = User.find_by_sid(request.sid)
	room = _Match.find_by_code(session.get('code', None))
	if user is None or room is None:
		return 

	# Process the attempted solution here!
	value = data.get('c', '')
	# better move this to check. Problem blocking answers by spaming RETURN.
	if not isinstance(value, str): 
		return

	if not room.is_member(user):
		return 

	if room.is_finished:
		return 

	task, attempts, success, finished = room.process(user, value)

	members = member_data(room)

	if success:
		emit(
			'score',
			{
				'username': user.username,
				'sid': user.sid,
				'points': user.points,
			},
			room=room.code,
		)
	
	if finished:
		emit('game_over', 
			{
				'rounds': room.round, 
				'members': members
			}, 
			room=room.code
		)

		return 

	emit('task', 
		{
			'attempts': attempts, 
			'round': room.round, 
			'max_rounds': MAX_ROUNDS, 
			'task': task.to_dict(), 
			'success': success
		}, 
		room=room.code
	)

@socketio.on('ready')
def on_ready():
	user = User.find_by_sid(request.sid)
	room = _Match.find_by_code(session.get('code'))

	if user is None or room is None:
		return

	all_ready, task = room.ready(user)

	members = member_data(room)

	emit(
		'ready_state',
		{ 'members': members },
		room=room.code
	)

	if not all_ready or task is None:
		return

	emit('room', room_data(room), room=room.code)
	emit(
		'task', 
		{
			'attempts': 0,
			'round': 0,
			'max_rounds': MAX_ROUNDS,
			'task': task.to_dict(),
			'success': False
		}, 
		room=room.code
	)


if __name__ == "__main__":
	socketio.run(app, debug=True)