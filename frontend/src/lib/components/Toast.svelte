<script lang="ts">
    import { toasts, type Toast } from '$lib/stores/toasts';
    import { fly, fade } from 'svelte/transition';

    function getIcon(type: Toast['type']): string {
        switch (type) {
            case 'success': return '✓';
            case 'error': return '✕';
            case 'warning': return '⚠';
            case 'info': return 'ℹ';
            default: return '';
        }
    }
</script>

<div class="toast-container">
    {#each $toasts as toast (toast.id)}
        <div 
            class="toast toast-{toast.type}"
            in:fly={{ x: 300, duration: 300 }}
            out:fade={{ duration: 200 }}
        >
            <span class="toast-icon">{getIcon(toast.type)}</span>
            <span class="toast-message">{toast.message}</span>
            <button class="toast-close" on:click={() => toasts.dismiss(toast.id)}>×</button>
        </div>
    {/each}
</div>

<style>
    .toast-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 400px;
    }

    .toast {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px;
        border-radius: 4px;
        background: var(--bg-secondary);
        border: 2px solid;
        font-family: var(--font-display);
        font-size: 0.95rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    .toast-success {
        border-color: #40e0d0;
        background: linear-gradient(135deg, rgba(64, 224, 208, 0.2), transparent);
    }

    .toast-success .toast-icon {
        color: #40e0d0;
    }

    .toast-error {
        border-color: #ff4757;
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.2), transparent);
    }

    .toast-error .toast-icon {
        color: #ff4757;
    }

    .toast-warning {
        border-color: #ffa502;
        background: linear-gradient(135deg, rgba(255, 165, 2, 0.2), transparent);
    }

    .toast-warning .toast-icon {
        color: #ffa502;
    }

    .toast-info {
        border-color: #00d2ff;
        background: linear-gradient(135deg, rgba(0, 210, 255, 0.2), transparent);
    }

    .toast-info .toast-icon {
        color: #00d2ff;
    }

    .toast-icon {
        font-size: 1.2rem;
        font-weight: bold;
    }

    .toast-message {
        flex: 1;
        color: var(--text-primary);
    }

    .toast-close {
        background: none;
        border: none;
        color: var(--text-muted);
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        line-height: 1;
        transition: color 0.2s;
    }

    .toast-close:hover {
        color: var(--text-primary);
    }
</style>
