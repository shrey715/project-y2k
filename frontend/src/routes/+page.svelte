<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth';
    import Button from '$lib/components/Button.svelte';

    let loading = true;
    let mounted = false;

    // Generate random star particles with varied properties
    const stars = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        top: Math.random() * 100,
        size: 1 + Math.random() * 3,
        delay: Math.random() * 5,
        duration: 2 + Math.random() * 4,
        type: ['cyan', 'pink', 'white'][Math.floor(Math.random() * 3)]
    }));

    // Rising particles
    const particles = Array.from({ length: 15 }, (_, i) => ({
        id: i,
        left: Math.random() * 100,
        delay: Math.random() * 5,
        duration: 6 + Math.random() * 4
    }));

    onMount(async () => {
        mounted = true;
        setTimeout(() => loading = false, 1500);
        
        const isAuth = await auth.check();
        if (isAuth) {
            setTimeout(() => goto('/user_dashboard'), 1600);
        }
    });
</script>

<svelte:head>
    <title>Y2K Video Editor - Turn Moments to Melodies</title>
</svelte:head>

<!-- Stars background -->
<div class="stars-bg">
    {#each stars as star}
        <div 
            class="star star-{star.type}"
            style="
                left: {star.left}%; 
                top: {star.top}%; 
                width: {star.size}px; 
                height: {star.size}px;
                animation-delay: {star.delay}s; 
                animation-duration: {star.duration}s;
            "
        ></div>
    {/each}
</div>

<!-- Rising particles -->
<div class="particles">
    {#each particles as p}
        <div 
            class="particle"
            style="left: {p.left}%; animation-delay: {p.delay}s; animation-duration: {p.duration}s;"
        ></div>
    {/each}
</div>

{#if loading}
    <div class="loader" class:fade-out={!loading && mounted}>
        <div class="loader-content">
            <img src="/images/logo.png" alt="Y2K" class="loader-logo" />
            <div class="loader-bar">
                <div class="loader-progress"></div>
            </div>
        </div>
    </div>
{/if}

<main class="hero" class:visible={!loading}>
    <div class="hero-content">
        <!-- Logo -->
        <div class="logo-container">
            <img src="/images/logo.png" alt="Y2K Video Editor" class="logo" />
        </div>
        
        <!-- Title -->
        <h1 class="title">
            <span class="text-gradient">Y2K</span>
        </h1>
        <p class="subtitle">Video Editor</p>
        <p class="tagline">Turn Moments to Melodies</p>
        
        <!-- CTA Buttons -->
        <div class="cta-buttons">
            <Button variant="primary" size="lg" on:click={() => goto('/login')}>
                Get Started
            </Button>
            <Button variant="secondary" size="lg" on:click={() => goto('/signup')}>
                Create Account
            </Button>
        </div>

        <!-- Features -->
        <div class="features">
            <div class="feature">
                <span class="feature-icon">🎬</span>
                <span>Create Videos</span>
            </div>
            <div class="feature">
                <span class="feature-icon">🎵</span>
                <span>Add Music</span>
            </div>
            <div class="feature">
                <span class="feature-icon">✨</span>
                <span>Apply Effects</span>
            </div>
        </div>
    </div>
</main>

<style>
    /* Stars Background */
    .stars-bg {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }

    .star {
        position: absolute;
        border-radius: 50%;
        animation: twinkle ease-in-out infinite;
    }

    .star-cyan {
        background: var(--neon-cyan);
        box-shadow: 0 0 6px var(--neon-cyan), 0 0 12px var(--neon-cyan);
    }

    .star-pink {
        background: var(--neon-pink);
        box-shadow: 0 0 6px var(--neon-pink), 0 0 12px var(--neon-pink);
    }

    .star-white {
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
    }

    @keyframes twinkle {
        0%, 100% {
            opacity: 0.3;
            transform: scale(0.8);
        }
        50% {
            opacity: 1;
            transform: scale(1.2);
        }
    }

    /* Rising Particles */
    .particles {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }

    .particle {
        position: absolute;
        width: 3px;
        height: 3px;
        background: var(--neon-cyan);
        border-radius: 50%;
        bottom: -10px;
        animation: rise linear infinite;
        opacity: 0.5;
        box-shadow: 0 0 8px var(--neon-cyan);
    }

    .particle:nth-child(even) {
        background: var(--neon-pink);
        box-shadow: 0 0 8px var(--neon-pink);
    }

    .particle:nth-child(3n) {
        width: 2px;
        height: 2px;
    }

    @keyframes rise {
        0% {
            transform: translateY(0) scale(0);
            opacity: 0;
        }
        10% {
            opacity: 0.6;
            transform: translateY(-10vh) scale(1);
        }
        90% {
            opacity: 0.6;
        }
        100% {
            transform: translateY(-100vh) scale(0.5);
            opacity: 0;
        }
    }

    /* Loader */
    .loader {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-dark);
        z-index: 100;
        transition: opacity 0.5s ease;
    }

    .fade-out {
        opacity: 0;
        pointer-events: none;
    }

    .loader-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-xl);
    }

    .loader-logo {
        width: 120px;
        height: 120px;
        border-radius: var(--radius-xl);
        animation: pulse 2s ease-in-out infinite;
    }

    .loader-bar {
        width: 200px;
        height: 4px;
        background: var(--bg-tertiary);
        border-radius: var(--radius-full);
        overflow: hidden;
    }

    .loader-progress {
        width: 100%;
        height: 100%;
        background: var(--gradient-primary);
        animation: loading 1.5s ease-out forwards;
    }

    @keyframes loading {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(0, 245, 255, 0.4);
        }
        50% { 
            transform: scale(1.05);
            box-shadow: 0 0 30px 10px rgba(0, 245, 255, 0.2);
        }
    }

    /* Hero */
    .hero {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 1;
    }

    .hero.visible {
        opacity: 1;
        transform: translateY(0);
    }

    .hero-content {
        text-align: center;
        max-width: 600px;
        padding: var(--space-xl);
    }

    /* Logo */
    .logo-container {
        margin-bottom: var(--space-xl);
    }

    .logo {
        width: 140px;
        height: 140px;
        border-radius: var(--radius-xl);
        transition: var(--transition-normal);
        cursor: pointer;
    }

    .logo:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: var(--shadow-glow-cyan);
    }

    /* Title */
    .title {
        font-size: clamp(4rem, 15vw, 8rem);
        font-weight: 900;
        letter-spacing: 0.1em;
        margin-bottom: var(--space-sm);
        animation: glow 3s ease-in-out infinite;
    }

    .subtitle {
        font-family: var(--font-display);
        font-size: clamp(1.5rem, 5vw, 2.5rem);
        font-weight: 400;
        color: var(--text-secondary);
        margin-bottom: var(--space-sm);
    }

    .tagline {
        font-size: 1rem;
        color: var(--text-muted);
        margin-bottom: var(--space-2xl);
    }

    /* CTA Buttons */
    .cta-buttons {
        display: flex;
        gap: var(--space-md);
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: var(--space-2xl);
    }

    /* Features */
    .features {
        display: flex;
        gap: var(--space-xl);
        justify-content: center;
        flex-wrap: wrap;
    }

    .feature {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .feature-icon {
        font-size: 1.25rem;
    }

    @keyframes glow {
        0%, 100% { 
            filter: drop-shadow(0 0 10px rgba(0, 245, 255, 0.5));
        }
        50% { 
            filter: drop-shadow(0 0 20px rgba(0, 245, 255, 0.8)) 
                   drop-shadow(0 0 30px rgba(255, 45, 117, 0.4));
        }
    }
</style>
