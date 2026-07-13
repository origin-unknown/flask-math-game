<script>
  import { socketState } from '../socket.svelte';

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

<form onsubmit={handleSubmit}>
  {match.task.a} * {match.task.b} = 
  <input type="number" bind:value={result} bind:this={inputRef} />
  <button type="submit" style="display: none;">Solve</button>
</form>