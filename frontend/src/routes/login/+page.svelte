<script lang="ts">
    import { auth } from '$lib/stores/auth';
    import { goto } from '$app/navigation';
    import Button from '$lib/components/Button.svelte';
    import Input from '$lib/components/Input.svelte';
    import Card from '$lib/components/Card.svelte';

    let username = '';
    let password = '';
    let error = '';
    let loading = false;

    async function handleLogin() {
        if (!username || !password) {
            error = 'Please fill in all fields';
            return;
        }

        loading = true;
        error = '';

        try {
            const result = await auth.login(username, password);
            if (result.status === 'success') {
                if (username === 'admin') {
                    goto('/admin');
                } else {
                    goto('/user_dashboard');
                }
            } else {
                error = result.message || 'Login failed';
            }
        } catch (e) {
            error = e instanceof Error ? e.message : 'Login failed';
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Login | Y2K Video Editor</title>
</svelte:head>

<div class="auth-page">
    <!-- Background particles -->
    <div class="bg-gradient"></div>
    
    <!-- Back button -->
    <a href="/" class="back-link" aria-label="Go back to home">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
    </a>

    <!-- Auth card with spinning border -->
    <div class="auth-box">
        <span class="border-line"></span>
        <div class="auth-card">
            <!-- Header -->
            <div class="auth-header">
                <img src="/images/logo.png" alt="Y2K" class="auth-logo" />
                <h1>Welcome Back</h1>
                <p>Sign in to continue your creative journey</p>
            </div>

            <!-- Form -->
            <form on:submit|preventDefault={handleLogin}>
                {#if error}
                    <div class="error-alert">
                        <span>{error}</span>
                    </div>
                {/if}

                <Input 
                    label="Username" 
                    bind:value={username} 
                    required 
                />
                
                <Input 
                    label="Password" 
                    type="password" 
                    bind:value={password} 
                    required 
                />

                <Button type="submit" variant="primary" size="lg" {loading}>
                    {loading ? 'Signing in...' : 'Sign In'}
                </Button>
            </form>

            <!-- Footer -->
            <div class="auth-footer">
                <span>Don't have an account?</span>
                <a href="/signup">Create one</a>
            </div>
        </div>
    </div>
</div>

<style>
    .auth-page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--space-xl);
        position: relative;
    }

    .bg-gradient {
        position: fixed;
        inset: 0;
        background: 
            radial-gradient(ellipse at 20% 80%, rgba(0, 245, 255, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(255, 45, 117, 0.1) 0%, transparent 50%),
            var(--bg-dark);
        z-index: -1;
    }

    .back-link {
        position: fixed;
        top: var(--space-xl);
        left: var(--space-xl);
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-secondary);
        border: var(--border-subtle);
        border-radius: var(--radius-full);
        color: var(--text-secondary);
        transition: var(--transition-fast);
    }

    .back-link:hover {
        color: var(--neon-cyan);
        border-color: var(--neon-cyan);
        box-shadow: var(--shadow-glow-cyan);
    }

    /* Spinning border box */
    .auth-box {
        position: relative;
        width: 420px;
        max-width: 100%;
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }

    .auth-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 420px;
        height: 500px;
        background: linear-gradient(0deg, transparent, transparent, var(--neon-cyan), var(--neon-cyan), var(--neon-cyan));
        z-index: 1;
        transform-origin: bottom right;
        animation: borderSpin 6s linear infinite;
    }

    .auth-box::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 420px;
        height: 500px;
        background: linear-gradient(0deg, transparent, transparent, var(--neon-cyan), var(--neon-cyan), var(--neon-cyan));
        z-index: 1;
        transform-origin: bottom right;
        animation: borderSpin 6s linear infinite;
        animation-delay: -3s;
        filter: blur(30px);
    }

    .border-line {
        position: absolute;
        inset: 0;
        z-index: 1;
    }

    .border-line::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 420px;
        height: 500px;
        background: linear-gradient(0deg, transparent, transparent, var(--neon-pink), var(--neon-pink), var(--neon-pink));
        z-index: 1;
        transform-origin: bottom right;
        animation: borderSpin 6s linear infinite;
        animation-delay: -1.5s;
    }

    .border-line::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 420px;
        height: 500px;
        background: linear-gradient(0deg, transparent, transparent, var(--neon-pink), var(--neon-pink), var(--neon-pink));
        z-index: 1;
        transform-origin: bottom right;
        animation: borderSpin 6s linear infinite;
        animation-delay: -4.5s;
        filter: blur(30px);
    }

    @keyframes borderSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .auth-card {
        position: relative;
        z-index: 10;
        background: var(--bg-secondary);
        padding: var(--space-xl);
        margin: 3px;
        border-radius: calc(var(--radius-lg) - 3px);
    }

    .auth-header {
        text-align: center;
        margin-bottom: var(--space-xl);
    }

    .auth-logo {
        width: 64px;
        height: 64px;
        border-radius: var(--radius-md);
        margin-bottom: var(--space-md);
    }

    .auth-header h1 {
        font-size: 1.75rem;
        margin-bottom: var(--space-xs);
    }

    .auth-header p {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: var(--space-md);
    }

    .error-alert {
        padding: var(--space-sm) var(--space-md);
        background: rgba(255, 45, 117, 0.1);
        border: 1px solid rgba(255, 45, 117, 0.3);
        border-radius: var(--radius-md);
        color: var(--neon-pink);
        font-size: 0.875rem;
        animation: slideDown 0.3s ease;
    }

    form :global(.btn) {
        width: 100%;
        margin-top: var(--space-md);
    }

    .auth-footer {
        text-align: center;
        margin-top: var(--space-xl);
        padding-top: var(--space-lg);
        border-top: var(--border-subtle);
        font-size: 0.9rem;
    }

    .auth-footer span {
        color: var(--text-secondary);
    }

    .auth-footer a {
        margin-left: var(--space-xs);
        color: var(--neon-cyan);
        font-weight: 500;
    }

    .auth-footer a:hover {
        text-decoration: underline;
    }

    @keyframes slideDown {
        from { 
            opacity: 0;
            transform: translateY(-10px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>

