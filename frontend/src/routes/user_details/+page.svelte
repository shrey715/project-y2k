<script lang="ts">
    import { onMount } from 'svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import Card from '$lib/components/Card.svelte';
    import { usersApi } from '$lib/api';

    let user = { username: '', email: '', images_cnt: 0, audios_cnt: 0 };
    let loading = true;

    onMount(async () => {
        try {
            user = await usersApi.me();
        } catch (e) {
            console.error('Error:', e);
        } finally {
            loading = false;
        }
    });
</script>

<svelte:head>
    <title>Profile | Y2K Video Editor</title>
</svelte:head>

<Sidebar />

<main class="main-content">
    {#if loading}
        <div class="skeleton-profile">
            <div class="skeleton skeleton-avatar"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text short"></div>
        </div>
    {:else}
        <Card variant="glass" padding="lg" hover={false}>
            <div class="profile-card">
                <div class="avatar">
                    <span>{user.username.charAt(0).toUpperCase()}</span>
                </div>
                <h1>{user.username}</h1>
                <p class="email">{user.email}</p>
                
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-value">{user.images_cnt}</span>
                        <span class="stat-label">Images</span>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat-item">
                        <span class="stat-value">{user.audios_cnt}</span>
                        <span class="stat-label">Audio Files</span>
                    </div>
                </div>
            </div>
        </Card>
    {/if}
</main>

<style>
    .main-content {
        min-height: 100vh;
        padding: var(--space-xl);
        padding-left: calc(64px + var(--space-xl));
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .skeleton-profile {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-md);
    }

    .skeleton {
        background: linear-gradient(90deg, var(--bg-secondary) 0%, var(--bg-tertiary) 50%, var(--bg-secondary) 100%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--radius-md);
    }

    .skeleton-avatar {
        width: 100px;
        height: 100px;
        border-radius: var(--radius-full);
    }

    .skeleton-text {
        width: 200px;
        height: 24px;
    }

    .skeleton-text.short {
        width: 150px;
        height: 16px;
    }

    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    .profile-card {
        text-align: center;
        padding: var(--space-xl);
        min-width: 300px;
    }

    .avatar {
        width: 100px;
        height: 100px;
        border-radius: var(--radius-full);
        background: var(--gradient-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto var(--space-lg);
        font-family: var(--font-display);
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--bg-dark);
    }

    h1 {
        margin-bottom: var(--space-xs);
    }

    .email {
        color: var(--text-secondary);
        margin-bottom: var(--space-xl);
    }

    .stats {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-xl);
        padding-top: var(--space-lg);
        border-top: var(--border-subtle);
    }

    .stat-item {
        text-align: center;
    }

    .stat-value {
        display: block;
        font-family: var(--font-display);
        font-size: 2rem;
        font-weight: 700;
        color: var(--neon-cyan);
    }

    .stat-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .stat-divider {
        width: 1px;
        height: 40px;
        background: var(--border-subtle);
    }
</style>
