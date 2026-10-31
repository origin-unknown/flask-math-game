<script>
	import { i18n } from '../i18n/i18n.js';
	import { socketState } from '../socket.svelte';
	import { room } from '../room.svelte';
	import { user } from '../user.svelte';
	import RoomGuard from './RoomGuard.svelte'
	import RoomLogin from './RoomLogin.svelte'
	import Roster from './Roster.svelte';
	import RoundOver from './RoundOver.svelte'
	import GameRoom from './GameRoom.svelte'
	import Countdown from './Countdown.svelte'
	import { onMount } from 'svelte';

	let match = $state();
	let gameOver = $state(null); 
	let readyMembers = $state([]);

	function leave() {
		socketState.leaveRoom();
		Object.assign(user, {});
	}

	onMount(() => { 	// async 
		const socket = socketState.connect(); // await

		socket.on("connect", () => {
			console.log("Connected:", socket.id);
		});

		const onRoom = (data) => {
			console.log(data);
			Object.assign(room, data);
			let member = data.members.find((item) => item.sid === user.sid);
			if (user && member) {
				user.points = member.points; 
			}
		};

		socket.on("room", onRoom);

		const onUser = (data) => {
			console.log(data);
			Object.assign(user, data);
		};

		socket.on("user", onUser);

		const onScore = (data) => {
			if (user.sid === data.sid) user.points = data.points;
			Object.assign(room.members.find((item) => item.sid === data.sid) || {}, data);
		};

		socket.on("score", onScore); 

		const onTask = (data) => {
			console.log(data);
			match = data;
			gameOver = null;
		};

		socket.on("task", onTask);

		const onGameOver = (data) => {
			console.log('Game Over', data); 
			gameOver = data;
			readyMembers = data.members;
		};

		socket.on('game_over', onGameOver); 

		const onReadyState = (data) => {
			console.log('Ready:', data);

			readyMembers = data.members;
		};

		socket.on("ready_state", onReadyState);

		return () => {
			socketState.leaveRoom();
			socket.off("room", onRoom);
			socket.off("user", onUser);
			socket.off("score", onScore);
			socket.off("task", onTask);
			socket.off("game_over", onGameOver);
			socket.off("ready_state", onReadyState);
			socketState.disconnect();
		};
	});

	$effect(() => {
		if (!socketState.socket) return;

		console.log("Socket available");
	});

</script>

<div>
	<RoomGuard joined={user.username} closed={room.state === 'closed'}>
		{#snippet join()}
			<RoomLogin />
		{/snippet}
		{#snippet open()}
			<div class="main-layout">
				<div class="top-bar">
					<div class="spacer"></div>
					<div><span class="label">{ i18n.t('type_disp_label') }:</span><span>{i18n.t(room.name)}</span></div>
					<div><span class="label">{ i18n.t('room_disp_label') }:</span> <span>{room.code}</span></div>
					<div><button type="button" onclick={ leave }>{ i18n.t('leave_button_label') }</button></div>
				</div>
				<div class="main-container">
					<div class="sidebar">
						<Roster members={room.members} />
					</div>
					<div class="main-content">
						<p>{ i18n.t('room_waiting_msg') }</p>
					</div>
				</div>
			</div>
		{/snippet}
		{#snippet close()}
			<div class="main-layout">
				<div class="top-bar">
					<div><span class="label">{i18n.t('points_disp_label')}:</span> <span>{user.points}</span></div>
					<div class="spacer"></div>
					<div><span class="label">{ i18n.t('type_disp_label') }:</span> <span>{i18n.t(room.name)}</span></div>
					<div><span class="label">{ i18n.t('room_disp_label') }:</span> <span>{room.code}</span></div>
					<div><button type="button" onclick={ leave }>{ i18n.t('leave_button_label') }</button></div>
				</div>
				<div class="main-container">
					<div class="sidebar">
						<Roster members={room.members} />
					</div>
					<div class="main-content">
						{#if gameOver}
							<RoundOver gameOver={gameOver} readyMembers={readyMembers} />
						{:else if match}
							<Countdown>
								{#snippet display()}
									<GameRoom match={match} />
								{/snippet}
							</Countdown>
						{/if}
					</div>
				</div>
			</div>
		{/snippet}
	</RoomGuard>
</div>

<style>

.main-layout {
	display: flex; 
	flex-direction: column;
	width: 100vw; 
	height: 100vh; 
}

.top-bar {
	flex-shrink: 0; 
	padding: 0rem 1rem;
	border-bottom: 1px solid black;
	display: flex; 
	gap: 1rem;
	font-size: 12pt;
}

.top-bar > * {
	padding: 1rem 0rem; 
	display: flex;
	gap: 2px;
	justify-content: center;
	align-items: center;
}

.label {
	font-weight: 600;
}

.main-container {
	display: flex; 
	flex: 1;
}

.main-content {
	flex: 1;
	overflow-y: auto;
	display: flex;
	justify-content: center; 
	align-items: center; 
	height: 100%;
	box-sizing: border-box;
}

.sidebar {
	flex: 0 0 240px;
	overflow-y: auto;
	padding: 0;
	border-right: 1px solid black;
}

.spacer {
	flex-grow: 1;
}

</style>