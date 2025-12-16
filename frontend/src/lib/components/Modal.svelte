<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    export let show = false;
    export let title = '';

    const dispatch = createEventDispatcher();

    function close() {
        show = false;
        dispatch('close');
    }

    function handleBackdropClick(e: MouseEvent) {
        if (e.target === e.currentTarget) {
            close();
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            close();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if show}
    <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click={handleBackdropClick}>
        <div class="modal-content">
            <div class="modal-header">
                <h2>{title}</h2>
                <button class="modal-close" on:click={close}>
                    <i class="bx bx-x"></i>
                </button>
            </div>
            <div class="modal-body">
                <slot />
            </div>
            <div class="modal-footer">
                <slot name="footer" />
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
    }

    .modal-content {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 1.5rem;
        max-width: 800px;
        max-height: 80vh;
        width: 90%;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .modal-header h2 {
        color: #fff;
        margin: 0;
        font-size: 1.5rem;
    }

    .modal-close {
        background: none;
        border: none;
        color: #fff;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
    }

    .modal-close:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    .modal-body {
        color: #e0e0e0;
    }

    .modal-footer {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .modal-footer:empty {
        display: none;
    }
</style>
