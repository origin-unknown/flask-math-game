<script>
	import { i18n } from './i18n/i18n.js';
	import Socket from './lib/Socket.svelte'

	if (typeof document !== 'undefined') {
		document.documentElement.lang = i18n.locale;
	}
</script>

<section id="center">
	<Socket />
</section>
