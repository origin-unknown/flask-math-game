<script>
  let { join, open, close, joined = false, closed = false } = $props();
</script>

{#if !joined}
  {@render join()}
{:else if joined && !closed}
  {@render open()}
{:else}
  {@render close()}
{/if}
