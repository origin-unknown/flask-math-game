<script>
	let { options = [], placeholder = 'Please choose…', value = $bindable() } = $props();

	let isOpen = $state(false);
	let highlightedIndex = $state(-1);

	let selectedLabel = $derived(
		options.find(opt => opt.value === value)?.title ?? placeholder
	);

	function toggleDropdown() {
		isOpen = !isOpen;
		if (isOpen) {
			highlightedIndex = options.findIndex(opt => opt.value === value);
		}
	}

	function selectOption(option) {
		value = option.value;
		selectedLabel = option.title;
		isOpen = false;
	}

	function closeDropdown(event) {
		if (!event.currentTarget.contains(event.relatedTarget)) {
			isOpen = false;
		}
	}

	function scrollIntoView(node, isHighlighted) {
		function update(highlighted) {
			if (highlighted) {
				node.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
			}
		}

		update(isHighlighted);

		return {
			update
		};
	}

	function handleKeyDown(event) {
		if (!isOpen) {
			if (event.key === 'Enter') {
				const form = event.currentTarget.closest('form');
				if (form) {
					form.requestSubmit();
				}
				return;
			}

			if (event.key === ' ' || event.key === 'ArrowDown' || event.key === 'ArrowUp') {
				event.preventDefault();
				toggleDropdown();
				highlightedIndex = 0;
			}

			return;
		}

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				highlightedIndex = (highlightedIndex + 1) % options.length;
				break;
				
			case 'ArrowUp':
				event.preventDefault();
				highlightedIndex = (highlightedIndex - 1 + options.length) % options.length;
				break;
				
			case ' ':
			case 'Enter':
				event.preventDefault();
				if (highlightedIndex >= 0 && highlightedIndex < options.length) {
					selectOption(options[highlightedIndex]);
				}
				break;
				
			case 'Escape':
				event.preventDefault();
				isOpen = false;
				break;
		}
	}
</script>

<div 
	class="custom-select" 
	role="combobox"
	aria-expanded={isOpen}
	aria-controls="select-dropdown-list"
	onfocusout={closeDropdown} 
	tabindex="0" 
	onkeydown={handleKeyDown}
>
	<button type="button" class="select-trigger" onclick={toggleDropdown}>
		{selectedLabel}
		<span class="arrow" class:open={isOpen}>▼</span>
	</button>

	{#if isOpen}
		<div class="options-dropdown">
			{#each options as option, i}
				<button 
					type="button" 
					class="option-item" 
					role="option"
					aria-selected={value === option.value}
					class:active={value === option.value}
					class:highlighted={highlightedIndex === i}
					use:scrollIntoView={highlightedIndex === i}
					onclick={() => selectOption(option)}
					onmouseenter={() => highlightedIndex = i} 
				>
					<span class="option-title">{option.title}</span>
					{#if option.subtitle}
						<span class="option-subtitle">{option.subtitle}</span>
					{/if}
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.custom-select {
		position: relative;
		width: 100%; 
	}

	.select-trigger {
		width: 100%;
		padding: 12px;
		background: #fff;
		border: 1px solid #000;
		text-align: left;
		cursor: pointer;
		display: flex;
		justify-content: space-between;
		align-items: center;
		transition: border-color 0.2s;
	}

	.arrow {
		transition: transform 0.2s;
	}

	.arrow.open {
		transform: rotate(180deg);
	}

	.options-dropdown {
		position: absolute;
		top: 105%;
		left: 0;
		right: 0;
		background: #ffffff;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
		z-index: 10;
		max-height: 250px;
		overflow-y: auto;
	}

	.option-item {
		width: 100%;
		padding: 10px 14px;
		border: none;
		background: none;
		text-align: left;
		cursor: pointer;
		display: flex;
		flex-direction: column;
		gap: 2px;
		transition: background 0.15s;
		border-bottom: 1px dotted #e2e8f0;
	}

	.option-item:last-of-type {
		border-bottom: none;
	}

	.option-item.highlighted
	{
		background: #f1f5f9;
	}

	.option-item.active {
		background: #eff6ff;
	}

	.option-title {
		font-weight: 600;
	}

	.option-subtitle {
		color: #64748b;
	}
</style>
