<script>

	let { display } = $props();

    let count = $state(10);

    $effect(() => {
        if (count <= 0) return;

        const timeout = setTimeout(() => {
            count--;
        }, 1000);

        return () => clearTimeout(timeout);
    });
</script>

{#if count > 0}
    <h1>{count}</h1>
{:else}
    {@render display()}
{/if}