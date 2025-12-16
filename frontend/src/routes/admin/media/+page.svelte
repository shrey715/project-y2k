<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import Card from '$lib/components/Card.svelte';
    import { auth, isAdmin } from '$lib/stores/auth';
    import { adminApi } from '$lib/api';

    interface MediaItem { id: number; filename: string; user_id: number; }

    let images: MediaItem[] = [];
    let audios: MediaItem[] = [];
    let loading = true;
    let activeTab: 'images' | 'audios' = 'images';

    onMount(async () => {
        await auth.check();
        if (!$isAdmin) {
            goto('/user_dashboard');
            return;
        }
        try {
            const data = await adminApi.getMedia();
            images = data.images || [];
            audios = data.audios || [];
        } catch (e) {
            console.error('Error:', e);
        } finally {
            loading = false;
        }
    });
</script>

<svelte:head>
    <title>Media Database | Y2K</title>
</svelte:head>

<Sidebar />

<main class="main-content">
    <header class="page-header">
        <h1>Media Database</h1>
        <p class="text-muted">View all user media files</p>
    </header>

    <!-- Tabs -->
    <div class="tabs">
        <button 
            class="tab" 
            class:active={activeTab === 'images'}
            on:click={() => activeTab = 'images'}
        >
            🖼️ Images ({images.length})
        </button>
        <button 
            class="tab" 
            class:active={activeTab === 'audios'}
            on:click={() => activeTab = 'audios'}
        >
            🎵 Audio ({audios.length})
        </button>
    </div>

    <!-- Content -->
    <Card variant="default" padding="none" hover={false}>
        {#if loading}
            <div class="table-loading">
                <div class="spinner"></div>
            </div>
        {:else if activeTab === 'images'}
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Filename</th>
                            <th>User ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each images as img}
                            <tr>
                                <td class="id-cell">{img.id}</td>
                                <td>{img.filename}</td>
                                <td class="number-cell">{img.user_id}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {:else}
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Filename</th>
                            <th>User ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each audios as aud}
                            <tr>
                                <td class="id-cell">{aud.id}</td>
                                <td>{aud.filename}</td>
                                <td class="number-cell">{aud.user_id}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </Card>
</main>

<style>
    .main-content {
        min-height: 100vh;
        padding: var(--space-xl);
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
        padding-left: calc(64px + var(--space-xl));
    }

    @media (max-width: 768px) {
        .main-content {
            padding-left: calc(64px + var(--space-md));
            padding-right: var(--space-md);
        }
    }

    .page-header {
        margin-bottom: var(--space-xl);
    }

    .page-header h1 {
        margin-bottom: var(--space-xs);
    }

    .text-muted {
        color: var(--text-secondary);
    }

    .tabs {
        display: flex;
        gap: var(--space-sm);
        margin-bottom: var(--space-lg);
    }

    .tab {
        padding: var(--space-sm) var(--space-lg);
        background: var(--bg-secondary);
        border: var(--border-subtle);
        border-radius: var(--radius-md);
        color: var(--text-secondary);
        font-size: 0.9rem;
        cursor: pointer;
        transition: var(--transition-fast);
    }

    .tab:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .tab.active {
        background: var(--neon-cyan);
        color: var(--bg-dark);
        border-color: var(--neon-cyan);
    }

    .table-loading {
        padding: var(--space-2xl);
        display: flex;
        justify-content: center;
    }

    .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid var(--bg-tertiary);
        border-top-color: var(--neon-cyan);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .table-wrapper {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th, td {
        padding: var(--space-md) var(--space-lg);
        text-align: left;
    }

    th {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        font-weight: 500;
        background: var(--bg-tertiary);
    }

    tr:hover {
        background: var(--bg-tertiary);
    }

    .id-cell {
        color: var(--text-muted);
        font-size: 0.85rem;
    }

    .number-cell {
        font-family: var(--font-mono);
        color: var(--neon-cyan);
    }
</style>
