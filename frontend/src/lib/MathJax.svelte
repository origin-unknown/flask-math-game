<script>
	let { math = '' } = $props();
	
	let container = $state(null);

	function render(node, textToRender) {
		if (!node) return;

		if (window.MathJax && window.MathJax.typesetPromise) {
			window.MathJax.typesetClear([node]);

			node.innerHTML = `$$${textToRender}$$`;
			
			window.MathJax.typesetPromise([node])
				.catch((err) => console.error("MathJax Error:", err));
		}
	}

	$effect(() => {
		render(container, math);
	});
</script>

<div bind:this={container}></div>
