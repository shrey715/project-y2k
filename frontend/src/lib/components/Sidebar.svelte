<script lang="ts">
    import { page } from '$app/stores';
    import { auth, isAdmin, currentUser } from '$lib/stores/auth';
    import { goto } from '$app/navigation';

    let expanded = false;

    async function handleLogout() {
        await auth.logout();
        goto('/');
    }

    $: currentPath = $page.url.pathname;

    const navItems = [
        { path: '/user_dashboard', icon: 'home', label: 'Dashboard' },
        { path: '/video_editor', icon: 'video', label: 'Video Editor' },
        { path: '/upload', icon: 'upload', label: 'Upload' },
    ];

    const adminItems = [
        { path: '/admin', icon: 'shield', label: 'Admin' },
        { path: '/admin/media', icon: 'database', label: 'Media DB' },
    ];
</script>

<nav class="sidebar" class:expanded on:mouseenter={() => expanded = true} on:mouseleave={() => expanded = false}>
    <!-- Logo -->
    <div class="sidebar-logo">
        <img src="/images/logo.png" alt="Y2K" />
    </div>

    <!-- Main navigation -->
    <ul class="nav-list">
        {#each navItems as item}
            <li>
                <a 
                    href={item.path} 
                    class="nav-item" 
                    class:active={currentPath === item.path}
                    title={item.label}
                >
                    <span class="nav-icon">
                        {#if item.icon === 'home'}
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                                <polyline points="9,22 9,12 15,12 15,22"/>
                            </svg>
                        {:else if item.icon === 'video'}
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="23,7 16,12 23,17 23,7"/>
                                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                            </svg>
                        {:else if item.icon === 'upload'}
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="17,8 12,3 7,8"/>
                                <line x1="12" y1="3" x2="12" y2="15"/>
                            </svg>
                        {/if}
                    </span>
                    <span class="nav-label">{item.label}</span>
                </a>
            </li>
        {/each}
    </ul>

    <!-- Admin section -->
    {#if $isAdmin}
        <div class="nav-divider"></div>
        <ul class="nav-list">
            {#each adminItems as item}
                <li>
                    <a 
                        href={item.path} 
                        class="nav-item" 
                        class:active={currentPath === item.path}
                        title={item.label}
                    >
                        <span class="nav-icon">
                            {#if item.icon === 'shield'}
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                                </svg>
                            {:else if item.icon === 'database'}
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <ellipse cx="12" cy="5" rx="9" ry="3"/>
                                    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                                    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                                </svg>
                            {/if}
                        </span>
                        <span class="nav-label">{item.label}</span>
                    </a>
                </li>
            {/each}
        </ul>
    {/if}

    <!-- Bottom section -->
    <div class="sidebar-bottom">
        <a 
            href="/user_details" 
            class="nav-item user-item" 
            class:active={currentPath === '/user_details'}
            title={$currentUser?.username || 'Profile'}
        >
            <span class="nav-icon user-avatar">
                {($currentUser?.username || 'U').charAt(0).toUpperCase()}
            </span>
            <span class="nav-label">{$currentUser?.username || 'User'}</span>
        </a>
        
        <button class="nav-item logout-btn" on:click={handleLogout} title="Logout">
            <span class="nav-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16,17 21,12 16,7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
            </span>
            <span class="nav-label">Logout</span>
        </button>
    </div>
</nav>

<style>
    .sidebar {
        position: fixed;
        left: 0;
        top: 0;
        height: 100vh;
        width: 64px;
        background: var(--bg-secondary);
        border-right: 2px solid var(--neon-cyan);
        display: flex;
        flex-direction: column;
        z-index: 100;
        transition: width 0.2s ease;
        overflow: hidden;
    }

    .sidebar.expanded {
        width: 200px;
    }

    .sidebar-logo {
        padding: var(--space-md);
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid rgba(64, 224, 208, 0.3);
        background: var(--bg-dark);
    }

    .sidebar-logo img {
        width: 36px;
        height: 36px;
        opacity: 0.9;
    }

    .nav-list {
        list-style: none;
        padding: var(--space-sm);
        flex: 1;
    }

    .nav-divider {
        height: 1px;
        background: rgba(224, 102, 160, 0.4);
        margin: var(--space-md) var(--space-sm);
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: var(--space-md);
        padding: var(--space-sm) var(--space-md);
        color: var(--text-secondary);
        text-decoration: none;
        transition: var(--transition-fast);
        white-space: nowrap;
        margin-bottom: 2px;
        border-radius: var(--radius-sm);
        font-family: var(--font-display);
        font-size: 1.1rem;
        text-transform: uppercase;
        position: relative;
    }

    .nav-item:hover {
        background: var(--bg-tertiary);
        color: var(--neon-cyan);
    }

    .nav-item.active {
        background: rgba(64, 224, 208, 0.15);
        color: var(--neon-cyan);
        border-left: 3px solid var(--neon-cyan);
    }

    .nav-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .nav-label {
        opacity: 0;
        transition: opacity 0.15s ease;
        letter-spacing: 1px;
    }

    .sidebar.expanded .nav-label {
        opacity: 1;
    }

    .user-avatar {
        width: 24px;
        height: 24px;
        background: var(--gradient-primary);
        border-radius: var(--radius-full);
        color: var(--bg-dark);
        font-weight: 600;
        font-size: 0.7rem;
        font-family: var(--font-arcade);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .sidebar-bottom {
        padding: var(--space-sm);
        border-top: 1px solid rgba(64, 224, 208, 0.3);
    }

    .logout-btn {
        width: 100%;
        border: none;
        cursor: pointer;
        background: none;
        font-family: var(--font-display);
    }

    .logout-btn:hover {
        color: var(--neon-pink);
    }
</style>

