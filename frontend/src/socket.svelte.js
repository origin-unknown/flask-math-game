// src/socket.svelte.js
import { io } from "socket.io-client";

class SocketState {
	socket = $state(null);

	connect() { 	// async 
		if (this.socket) return this.socket;

		// try {
		// 	let success = await fetch('/api/init', { credentials: 'include' })
		// 		.then(resp => resp.ok)
		// 	if (success) {
		// 		console.log('Session successfully initialized.');
		// 	}
		// } catch(err) {
		// 	console.log('Session could not be initialized.', err);
		// }

		this.socket = io({
			withCredentials: true
		});
		return this.socket;
	}

	disconnect() {
		this.socket?.disconnect();
		this.socket = null;
	}

	joinRoom(username, roomname, tasktype) {
		this.socket?.emit("join", { username, roomname, tasktype });
	}

	leaveRoom() {
		this.socket?.emit("leave");
	}

	submitResult(result) {
		this.socket?.emit("solve", { c: result });
	}

	submitMessage(message) {
		this.socket?.emit("send_message", { message });
	}

	ready() {
		this.socket?.emit("ready");
	}
}

export const socketState = new SocketState();