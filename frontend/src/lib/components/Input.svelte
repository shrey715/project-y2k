<script lang="ts">
    export let value: string = '';
    export let placeholder: string = '';
    export let label: string = '';
    export let type: 'text' | 'email' | 'password' | 'number' = 'text';
    export let disabled: boolean = false;
    export let required: boolean = false;

    // Use label as placeholder if no placeholder specified
    $: displayPlaceholder = placeholder || label;
</script>

<div class="input-wrapper">
    {#if label}
        <label class="input-label">{label}</label>
    {/if}
    <input
        {type}
        {disabled}
        {required}
        placeholder={displayPlaceholder}
        bind:value
        on:input
        on:focus
        on:blur
        {...$$restProps}
    />
</div>

<style>
    .input-wrapper {
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .input-label {
        font-family: var(--font-display);
        font-size: 1rem;
        color: var(--neon-cyan);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    input {
        width: 100%;
        background: var(--bg-dark);
        border: 2px solid var(--text-muted);
        padding: 12px 14px;
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 1.1rem;
        transition: all 0.15s ease;
    }

    input::placeholder {
        color: var(--text-muted);
        opacity: 0.6;
    }

    input:focus {
        outline: none;
        border-color: var(--neon-cyan);
        box-shadow: 
            0 0 8px rgba(64, 224, 208, 0.3),
            inset 0 0 8px rgba(64, 224, 208, 0.05);
    }

    input:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
