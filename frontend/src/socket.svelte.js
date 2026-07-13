// src/socket.svelte.js
import { io } from "socket.io-client";

class SocketState {
    socket = $state(null);

    connect() {
        if (this.socket) return this.socket;

        this.socket = io();
        return this.socket;
    }

    disconnect() {
        this.socket?.disconnect();
        this.socket = null;
    }

    joinRoom(username, roomname) {
        this.socket?.emit("join", { username, roomname });
    }

    leaveRoom() {
        this.socket?.emit("leave", {});
    }

    submitResult(result) {
        this.socket?.emit("solve", { c: result });
    }

    submitMessage(message) {
        this.socket?.emit("send_message", { message });
    }
}

export const socketState = new SocketState();