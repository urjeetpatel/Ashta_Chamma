<script lang="ts">
	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import '../app.css';
	let { children } = $props();

</script>
<div class="flex flex-col h-screen">
	<Navbar />
	<main class="flex-1">
		{@render children()}
	</main>

	<Footer />
</div>
