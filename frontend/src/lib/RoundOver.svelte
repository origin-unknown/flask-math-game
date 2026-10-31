<script>
	import { i18n } from '../i18n/i18n.js';
	import { socketState } from '../socket.svelte';
	import { user } from '../user.svelte';

	let { gameOver, readyMembers = [] } = $props();
</script>

<div class="game-over">
	<h1>{ i18n.t('gratulation_msg') }</h1>
	<p>{ i18n.t('rounds_msg', {rounds: gameOver.rounds }) }</p>

	<h2>{ i18n.t('score_msg') }</h2>
	<div class="results">
		{#each gameOver.members.toSorted((a, b) => b.points - a.points) as member}
			<div class="result-row">
				<span>{member.username}</span>
				<span>{member.points}</span>
			</div>
		{/each}
	</div>

	<h2>{ i18n.t('round_msg') }</h2>
	<div style="margin-bottom: 1rem;">
		{#each readyMembers as member}
			<div>
				{member.username}:
				{#if member.ready}
					<span>{ i18n.t('user_ready_msg') }</span>
				{:else}
					<span>{ i18n.t('user_waiting_msg') }</span>
				{/if}
			</div>
		{/each}
	</div>

	{#if readyMembers.find((m) => m.sid === user.sid)?.ready}
		<p>{ i18n.t('user_ready_desc') }</p>
	{:else}
		<button type="button" onclick={() => socketState.ready()}>{ i18n.t('ready_button_label') }</button>
	{/if}
</div>

<style>

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