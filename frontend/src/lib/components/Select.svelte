<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    
    export let value: string = '';
    export let options: { value: string; label: string }[] = [];
    export let placeholder: string = 'Select...';
    export let disabled: boolean = false;
    export let variant: 'primary' | 'secondary' = 'secondary';

    const dispatch = createEventDispatcher();
    
    let isOpen = false;
    let wrapperEl: HTMLDivElement;

    $: selectedLabel = options.find(o => o.value === value)?.label || placeholder;

    function toggle() {
        if (!disabled) {
            isOpen = !isOpen;
        }
    }

    function select(opt: { value: string; label: string }) {
        value = opt.value;
        isOpen = false;
        dispatch('change', { value: opt.value });
    }

    function handleClickOutside(event: MouseEvent) {
        if (wrapperEl && !wrapperEl.contains(event.target as Node)) {
            isOpen = false;
        }
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Escape') {
            isOpen = false;
        }
    }
</script>

<svelte:window on:click={handleClickOutside} on:keydown={handleKeydown} />

<div class="select-wrapper" bind:this={wrapperEl} class:disabled>
    <button 
        type="button"
        class="select-trigger variant-{variant}" 
        class:open={isOpen}
        on:click={toggle}
        {disabled}
    >
        <span class="select-value">{selectedLabel}</span>
        <span class="select-arrow">▼</span>
    </button>
    
    {#if isOpen}
        <div class="select-dropdown">
            {#each options as opt}
                <button 
                    type="button"
                    class="select-option"
                    class:selected={opt.value === value}
                    on:click={() => select(opt)}
                >
                    {opt.label}
                </button>
            {/each}
        </div>
    {/if}
</div>

<style>
    .select-wrapper {
        position: relative;
        display: inline-block;
    }

    .select-wrapper.disabled {
        opacity: 0.5;
        pointer-events: none;
    }

    /* Match Button component styling exactly */
    .select-trigger {
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
        padding: 12px 24px;
        font-size: 0.75rem;
    }

    /* Secondary variant - matches secondary button */
    .variant-secondary {
        background: var(--bg-secondary);
        color: var(--neon-pink);
        border-color: var(--neon-pink);
    }

    .variant-secondary:hover {
        background: var(--neon-pink);
        color: var(--bg-dark);
        box-shadow: 0 0 15px var(--neon-pink);
    }

    /* Primary variant - matches primary button */
    .variant-primary {
        background: var(--neon-cyan);
        color: var(--bg-dark);
        border-color: var(--neon-cyan);
        box-shadow: 0 0 10px var(--neon-cyan);
    }

    .variant-primary:hover {
        background: var(--bg-dark);
        color: var(--neon-cyan);
    }

    .select-trigger.open {
        background: var(--neon-pink);
        color: var(--bg-dark);
    }

    .select-arrow {
        font-size: 0.5rem;
        margin-left: 4px;
    }

    .select-dropdown {
        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        right: 0;
        background: var(--bg-secondary);
        border: 2px solid var(--neon-pink);
        z-index: 100;
        min-width: 100%;
    }

    .select-option {
        display: block;
        width: 100%;
        padding: 10px 16px;
        background: transparent;
        border: none;
        color: var(--text-secondary);
        font-family: var(--font-arcade);
        font-size: 0.65rem;
        text-transform: uppercase;
        text-align: center;
        cursor: pointer;
        transition: all 0.1s ease;
    }

    .select-option:hover {
        background: var(--neon-pink);
        color: var(--bg-dark);
    }

    .select-option.selected {
        color: var(--neon-pink);
        background: rgba(224, 102, 160, 0.15);
    }
</style>
