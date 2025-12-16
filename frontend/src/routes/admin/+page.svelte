<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import Card from '$lib/components/Card.svelte';
    import { auth, isAdmin } from '$lib/stores/auth';
    import { adminApi } from '$lib/api';

    interface UserItem { id: number; username: string; email: string; images_cnt: number; audios_cnt: number; }

    let users: UserItem[] = [];
    let loading = true;

    onMount(async () => {
        await auth.check();
        if (!$isAdmin) {
            goto('/user_dashboard');
            return;
        }
        try {
            const data = await adminApi.getUsers();
            users = data.users || [];
        } catch (e) {
            console.error('Error:', e);
        } finally {
            loading = false;
        }
    });
</script>

<svelte:head>
    <title>Admin Dashboard | Y2K</title>
</svelte:head>

<Sidebar />

<main class="main-content">
    <header class="page-header">
        <h1>Admin Dashboard</h1>
        <p class="text-muted">Manage users and system</p>
    </header>

    <!-- Stats cards -->
    <div class="stats-grid">
        <Card variant="glow" padding="md">
            <div class="stat-card">
                <span class="stat-icon">👥</span>
                <div class="stat-info">
                    <span class="stat-value">{users.length}</span>
                    <span class="stat-label">Total Users</span>
                </div>
            </div>
        </Card>
        <Card variant="glow" padding="md">
            <div class="stat-card">
                <span class="stat-icon">🖼️</span>
                <div class="stat-info">
                    <span class="stat-value">{users.reduce((a, u) => a + u.images_cnt, 0)}</span>
                    <span class="stat-label">Total Images</span>
                </div>
            </div>
        </Card>
        <Card variant="glow" padding="md">
            <div class="stat-card">
                <span class="stat-icon">🎵</span>
                <div class="stat-info">
                    <span class="stat-value">{users.reduce((a, u) => a + u.audios_cnt, 0)}</span>
                    <span class="stat-label">Total Audio</span>
                </div>
            </div>
        </Card>
    </div>

    <!-- Users table -->
    <Card variant="default" padding="none" hover={false}>
        <div class="table-header">
            <h2>All Users</h2>
        </div>
        {#if loading}
            <div class="table-loading">
                <div class="spinner"></div>
            </div>
        {:else}
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Images</th>
                            <th>Audio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each users as user}
                            <tr>
                                <td class="id-cell">{user.id}</td>
                                <td>
                                    <div class="user-cell">
                                        <span class="user-avatar">{user.username.charAt(0).toUpperCase()}</span>
                                        {user.username}
                                    </div>
                                </td>
                                <td class="email-cell">{user.email}</td>
                                <td class="number-cell">{user.images_cnt}</td>
                                <td class="number-cell">{user.audios_cnt}</td>
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

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--space-lg);
        margin-bottom: var(--space-xl);
    }

    .stat-card {
        display: flex;
        align-items: center;
        gap: var(--space-md);
    }

    .stat-icon {
        font-size: 2rem;
    }

    .stat-info {
        display: flex;
        flex-direction: column;
    }

    .stat-value {
        font-family: var(--font-display);
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--neon-cyan);
    }

    .stat-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .table-header {
        padding: var(--space-md) var(--space-lg);
        border-bottom: var(--border-subtle);
    }

    .table-header h2 {
        font-size: 1.1rem;
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

    .user-cell {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }

    .user-avatar {
        width: 28px;
        height: 28px;
        border-radius: var(--radius-full);
        background: var(--gradient-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--bg-dark);
    }

    .email-cell {
        color: var(--text-secondary);
    }

    .number-cell {
        font-family: var(--font-mono);
        color: var(--neon-cyan);
    }
</style>
