<script lang="ts">
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import Toast from '$lib/components/Toast.svelte';
    import '../app.css';

    const publicRoutes = ['/', '/login', '/signup'];

    onMount(async () => {
        await auth.check();
    });

    $: if ($auth.checked && !$auth.loading) {
        const isPublicRoute = publicRoutes.includes($page.url.pathname);
        if (!$auth.user && !isPublicRoute) {
            goto('/login');
        }
    }
</script>

<Toast />
<slot />
