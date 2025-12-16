<script lang="ts">
    export let variant: 'primary' | 'secondary' | 'ghost' = 'primary';
    export let size: 'sm' | 'md' | 'lg' = 'md';
    export let disabled = false;
    export let loading = false;
    export let type: 'button' | 'submit' = 'button';
</script>

<button
    {type}
    {disabled}
    class="btn btn-{variant} btn-{size}"
    class:loading
    on:click
    {...$$restProps}
>
    {#if loading}
        <span class="spinner"></span>
    {/if}
    <slot />
</button>

<style>
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-sm);
        font-family: var(--font-arcade);
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 1px;
        cursor: pointer;
        position: relative;
        transition: all 0.15s ease;
        border: 4px solid;
    }

    .btn::before {
        content: '>';
        position: absolute;
        left: 8px;
        opacity: 0;
        transition: opacity 0.1s ease;
        font-size: 0.75em;
    }

    .btn:hover::before {
        opacity: 1;
    }

    /* Sizes */
    .btn-sm {
        padding: 8px 16px;
        font-size: 0.625rem;
    }

    .btn-md {
        padding: 12px 24px;
        font-size: 0.75rem;
    }

    .btn-lg {
        padding: 16px 32px;
        font-size: 0.875rem;
    }

    /* Primary - Cyan glow */
    .btn-primary {
        background: var(--neon-cyan);
        color: var(--bg-dark);
        border-color: var(--neon-cyan);
        box-shadow: 0 0 10px var(--neon-cyan);
    }

    .btn-primary:hover:not(:disabled) {
        background: var(--bg-dark);
        color: var(--neon-cyan);
        box-shadow: 
            0 0 10px var(--neon-cyan),
            0 0 20px var(--neon-cyan),
            inset 0 0 20px rgba(0, 255, 255, 0.1);
        transform: scale(1.02);
    }

    .btn-primary:active:not(:disabled) {
        transform: scale(0.98);
    }

    /* Secondary - Pink outline */
    .btn-secondary {
        background: var(--bg-secondary);
        color: var(--neon-pink);
        border-color: var(--neon-pink);
    }

    .btn-secondary:hover:not(:disabled) {
        background: var(--neon-pink);
        color: var(--bg-dark);
        box-shadow: 0 0 15px var(--neon-pink);
        transform: scale(1.02);
    }

    /* Ghost - Subtle */
    .btn-ghost {
        background: transparent;
        color: var(--text-secondary);
        border-color: var(--text-muted);
        border-width: 2px;
    }

    .btn-ghost:hover:not(:disabled) {
        color: var(--neon-yellow);
        border-color: var(--neon-yellow);
        text-shadow: 0 0 10px var(--neon-yellow);
    }

    /* Disabled */
    .btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }

    /* Loading */
    .loading {
        pointer-events: none;
    }

    .spinner {
        width: 12px;
        height: 12px;
        border: 2px solid transparent;
        border-top-color: currentColor;
        border-right-color: currentColor;
        animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
