<script>
	import { socketState } from '../socket.svelte';
	import MathJax from './MathJax.svelte';

	let { match } = $props();

	let result = $state();
	let inputRef = $state(null);

	function handleSubmit(event) {
		event.preventDefault();
		socketState.submitResult(result);
		result = null;
	}

	$effect(() => {
		inputRef?.focus();
	});

</script>

<form onsubmit={handleSubmit} class="task-form">
	<div>
		<MathJax
		  math={match.task.latex} 
		/>
	</div>
	<div>
		<input type="text" bind:value={result} bind:this={inputRef} pattern="\s*[+-]?[0-9]+(?:\s*/\s*[0-9]+)?\s*" />
	</div>
	<div>
		<button type="submit" style="display: none;">Solve</button>
	</div>
</form>

<style>
	.task-form {
		display: flex; 
		flex-direction: column; 
		align-items: center; 
		gap: 10px;
	}
</style>