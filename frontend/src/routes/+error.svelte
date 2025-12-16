<script>
    import { page } from '$app/stores';
    import Button from '$lib/components/Button.svelte';
</script>

<svelte:head>
    <title>Page Not Found | Y2K</title>
</svelte:head>

<div class="error-page">
    <div class="error-content">
        <div class="error-code">
            <span class="four">4</span>
            <span class="zero">0</span>
            <span class="four">4</span>
        </div>
        <h1>Page Not Found</h1>
        <p>The page you're looking for doesn't exist or has been moved.</p>
        <div class="error-actions">
            <Button variant="primary" on:click={() => window.history.back()}>
                Go Back
            </Button>
            <Button variant="secondary" on:click={() => window.location.href = '/'}>
                Home
            </Button>
        </div>
    </div>
</div>

<style>
    .error-page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--space-xl);
        background: var(--bg-dark);
    }

    .error-content {
        text-align: center;
        max-width: 400px;
    }

    .error-code {
        display: flex;
        justify-content: center;
        gap: var(--space-md);
        margin-bottom: var(--space-xl);
    }

    .error-code span {
        font-family: var(--font-display);
        font-size: clamp(4rem, 15vw, 8rem);
        font-weight: 900;
        line-height: 1;
    }

    .four {
        color: var(--neon-cyan);
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }

    .zero {
        color: var(--neon-pink);
        text-shadow: 0 0 20px rgba(255, 45, 117, 0.5);
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.95); }
    }

    h1 {
        font-size: 1.5rem;
        margin-bottom: var(--space-sm);
    }

    p {
        color: var(--text-secondary);
        margin-bottom: var(--space-xl);
    }

    .error-actions {
        display: flex;
        gap: var(--space-md);
        justify-content: center;
    }
</style>
