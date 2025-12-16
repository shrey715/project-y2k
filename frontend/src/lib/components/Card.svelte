<script lang="ts">
    export let variant: 'default' | 'glass' | 'glow' = 'default';
    export let padding: 'none' | 'sm' | 'md' | 'lg' = 'md';
    export let hover: boolean = true;
</script>

<div class="card card-{variant} pad-{padding}" class:hoverable={hover}>
    <slot />
</div>

<style>
    .card {
        background: var(--arcade-dark);
        border: 3px solid var(--neon-cyan);
        position: relative;
        transition: all 0.15s ease;
    }

    /* Pixel corner decorations */
    .card::before,
    .card::after {
        content: '';
        position: absolute;
        width: 8px;
        height: 8px;
        background: var(--neon-pink);
    }

    .card::before {
        top: -4px;
        left: -4px;
    }

    .card::after {
        bottom: -4px;
        right: -4px;
    }

    /* Padding variants */
    .pad-none { padding: 0; }
    .pad-sm { padding: var(--space-sm); }
    .pad-md { padding: var(--space-md); }
    .pad-lg { padding: var(--space-lg); }

    /* Default variant */
    .card-default {
        background: var(--arcade-dark);
        box-shadow: 
            inset 0 0 30px rgba(0, 255, 255, 0.05),
            0 0 10px rgba(0, 255, 255, 0.2);
    }

    /* Glass variant - more transparent */
    .card-glass {
        background: rgba(26, 26, 46, 0.9);
        border-color: var(--neon-pink);
        box-shadow: 
            inset 0 0 30px rgba(255, 0, 255, 0.05),
            0 0 10px rgba(255, 0, 255, 0.2);
    }

    .card-glass::before,
    .card-glass::after {
        background: var(--neon-cyan);
    }

    /* Glow variant - extra bright */
    .card-glow {
        border-color: var(--neon-yellow);
        box-shadow: 
            0 0 15px var(--neon-yellow),
            inset 0 0 30px rgba(255, 255, 0, 0.05);
    }

    .card-glow::before,
    .card-glow::after {
        background: var(--neon-yellow);
    }

    /* Hover effect */
    .hoverable:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 0 20px var(--neon-cyan),
            0 0 40px rgba(0, 255, 255, 0.3);
    }
</style>
