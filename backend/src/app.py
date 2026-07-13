from flask import Flask, render_template, request, session
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import Match as _Match, Room, User


app = Flask(__name__, 
    static_url_path='', 
)

app.config.from_mapping(
	SECRET_KEY='your secret here', 
	SESSION_TYPE='filesystem' 
)

socketio = SocketIO(app,
	manage_session=True, 
	cors_allowed_origins=[
		'http://127.0.0.1:5000', 
		'http://localhost:5173', 
	]
)

@app.route('/')
def index():
	return app.send_static_file('index.html')

@app.route('/dev')
def dev_index():
	session.clear() # deprecated 
	return render_template('index.html') 


@socketio.on('connect')
def on_connect():
	session.clear()

@socketio.on('disconnect')
def on_disconnect():
	user = User.find_by_sid(request.sid)
	room = Room.find_by_code(session.pop('code', None))

	if room:
		leave_room(room.code)

		user and room.remove_member(user)

		if room.is_open:
			emit('room', 
				{ 
					'state': 'open', 
					'code': room.code, 
					'members': [
						{ 
							'sid': m.sid, 
							'username': m.username, 
							'points': m.points
						} for m in room._members.values()
					] 
				}, 
				room=room.code
			)
			room.is_empty and room.remove()

		emit('message', {'msg': f'{user.username} has left room {room.code}'}, room=room.code)

	user and user.remove()


@socketio.on('join')
def on_join(data):
	if session.get('code'):
		return

	username = data['username'].strip()
	roomcode = data.get('roomname', None)

	if not username:
		return
	
	user = User.find_by_sid(request.sid) 
	if user: user.remove()
	user = User.create(sid=request.sid, username=username)

	room = None
	if roomcode:
		room = _Match.find_by_code(roomcode)
	if not room:		
		room = _Match.find_open_room()

	if not room or room.is_closed:
		room = _Match.create()
	room.add_member(user)

	join_room(room.code)
	session['code'] = room.code

	emit('message', {'msg': f'{user.username} has joined room {room.code}'}, room=room.code)

	if room.is_closed:
		# Start the match here!
		room.reset_points()

		emit('room', 
			{ 
				'state': 'closed', 
				'code': room.code, 
				'members': [
					{ 
						'sid': m.sid, 
						'username': m.username, 
						'points': m.points
					} for m in room._members.values()
				] 
			}, 
			room=room.code
		)
		
		task, attempts, success = room.create_task(), 0, False
		emit('task', 
			{
				'attempts': attempts, 
				'task': task._asdict(), 
				'success': success
			}, 
			room=room.code
		)
		emit('user', { 'username': user.username, 'sid': user.sid, 'points': user.points }, room=room.code)

	else:
		emit('room', 
			{ 
				'state': 'open', 
				'code': room.code, 
				'members': [
					{ 
						'sid': m.sid, 
						'username': m.username, 
						'points': m.points
					} for m in room._members.values()
				] 
			}, 
			room=room.code
		)
		emit('user', { 'username': user.username, 'sid': user.sid, 'points': user.points }, room=room.code)

@socketio.on('leave')
def on_leave(data):
	user = User.find_by_sid(request.sid)
	room = Room.find_by_code(session.pop('code', None))

	if user is None or room is None:
		return

	room.remove_member(user)
	if room.is_open:
		emit('room', 
			{ 
				'state': 'open', 
				'code': room.code, 
				'members': [
					{ 
						'sid': m.sid, 
						'username': m.username, 
						'points': m.points
					} for m in room._members.values()
				] 
			}, 
			room=room.code
		)

	leave_room(room.code)

	room.is_empty and room.remove()

	emit('user', { 'username': '', 'sid': user.sid, 'points': user.points }, room=user.sid)
	emit('message', {'msg': f'{user.username} has left room {room.code}'}, room=room.code)


@socketio.on('message')
def room_message(data):
	room = Room.find_by_code(session.get('code'))
	if room is None:
		return

	user = User.find_by_sid(request.sid)
	
	if user and room.is_member(user):
		msg = data['message']
		emit('message', {'msg': f'{user.username}: {msg}'}, room=room.code)


@socketio.on('solve')
def on_solve(data):
	user = User.find_by_sid(request.sid)
	room = _Match.find_by_code(session.get('code', None))
	if user is None or room is None:
		return 

	# Process the attempted solution here!
	num = int(data['c'])
	task, attempts, success = room.process(num)
	emit('task', 
		{
			'attempts': attempts, 
			'task': task._asdict(), 
			'success': success
		}, 
		room=room.code
	)
	if success:
		user.points += 10
		emit('user', { 'username': user.username, 'sid': user.sid, 'points': user.points }, room=room.code) #user.sid)
		# <- room ?


if __name__ == "__main__":
	socketio.run(app, debug=True)