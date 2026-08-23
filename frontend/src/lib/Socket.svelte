<script>
	import { socketState } from '../socket.svelte';
	import { room } from '../room.svelte';
	import { user } from '../user.svelte';
	import RoomGuard from './RoomGuard.svelte'
	import RoomLogin from './RoomLogin.svelte'
	import Roster from './Roster.svelte';
	import Points from './Points.svelte';
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
					<div>Type: <span style="text-transform: capitalize;">{room.type}</span></div>
					<div>Room: <span>{room.code}</span></div>
					<div><button type="button" onclick={ leave }>Leave</button></div>
				</div>
				<div class="main-container">
					<div class="sidebar">
						<Roster members={room.members} />
					</div>
					<div class="main-content">
						<p>Room is open. Waiting for members.</p>
					</div>
				</div>
			</div>        
		{/snippet}
		{#snippet close()}
			<div class="main-layout">
				<div class="top-bar">
					<Points points={user.points} />
					<div class="spacer"></div>
					<div>Task: <span style="text-transform: capitalize;">{room.type}</span></div>
					<div>Room: <span>{room.code}</span></div>
					<div><button type="button" onclick={ leave }>Leave</button></div>
				</div>
				<div class="main-container">
					<div class="sidebar">
						<Roster members={room.members} />
					</div>
					<div class="main-content">
						{#if gameOver}
							<div class="game-over">
								<h1>Congratulations!</h1>
								<p>All {gameOver.rounds} rounds have been played.</p>

								<h2>Score</h2>
								<div class="results">
									{#each gameOver.members.toSorted((a, b) => b.points - a.points) as member}
										<div class="result-row">
											<span>{member.username}</span>
											<span>{member.points}</span>
										</div>
									{/each}
								</div>

								<h2>New round</h2>
								<div style="margin-bottom: 1rem;">
									{#each readyMembers as member}
										<div>
											{member.username}:
											{#if member.ready}
												<span>✓ ready</span>
											{:else}
												<span>is waiting…</span>
											{/if}
										</div>
									{/each}
								</div>

								{#if readyMembers.find((m) => m.sid === user.sid)?.ready}
									<p>You are ready. Waiting for the other player…</p>
								{:else}
									<button type="button" onclick={() => socketState.ready()}>Ready</button>
								{/if}

							</div>
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
	padding: 1.2rem 1rem; 
	border-bottom: 1px solid black;
	display: flex; 
	gap: 1rem;
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

.game-over {
	text-align: center;
	width: min(500px, 90%);
}

.results {
	margin: 1rem 0;
	border: 1px solid black;
	border-radius: 3px;
}

.result-row {
	display: flex;
	justify-content: space-between;
	padding: 0.64rem;
	border-bottom: 1px solid #ddd;
}

.result-row:last-child {
	border-bottom: none;
}

</style>