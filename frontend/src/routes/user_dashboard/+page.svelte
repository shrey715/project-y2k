<script lang="ts">
    import { onMount } from 'svelte';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import Card from '$lib/components/Card.svelte';
    import Button from '$lib/components/Button.svelte';
    import { usersApi, mediaApi } from '$lib/api';
    import { goto } from '$app/navigation';

    interface MediaItem {
        id: number;
        filename: string;
    }

    let images: MediaItem[] = [];
    let audios: MediaItem[] = [];
    let defaultAudios: MediaItem[] = [];
    let selectedImageIds: Set<number> = new Set();
    let selectedAudioIds: Set<number> = new Set();
    let searchQuery = '';
    let showModal = false;
    let modalImageSrc = '';
    let modalImageName = '';
    let loading = true;

    onMount(async () => {
        try {
            const data = await usersApi.dashboard();
            images = data.images || [];
            audios = data.audios || [];
            defaultAudios = data.default_audios || [];
        } catch (e) {
            console.error('Failed to load dashboard:', e);
        } finally {
            loading = false;
        }
    });

    $: filteredImages = searchQuery 
        ? images.filter(img => img.filename?.toLowerCase().includes(searchQuery.toLowerCase()))
        : images;

    function toggleImageSelection(id: number) {
        if (selectedImageIds.has(id)) {
            selectedImageIds.delete(id);
        } else {
            selectedImageIds.add(id);
        }
        selectedImageIds = selectedImageIds;
    }

    function toggleAudioSelection(id: number) {
        if (selectedAudioIds.has(id)) {
            selectedAudioIds.delete(id);
        } else {
            selectedAudioIds.add(id);
        }
        selectedAudioIds = selectedAudioIds;
    }

    async function deleteSelectedImages() {
        if (selectedImageIds.size === 0) return;
        try {
            await mediaApi.deleteImages([...selectedImageIds]);
            images = images.filter(img => !selectedImageIds.has(img.id));
            selectedImageIds.clear();
            selectedImageIds = selectedImageIds;
        } catch (e) {
            alert('Failed to delete images');
        }
    }

    async function deleteSelectedAudios() {
        if (selectedAudioIds.size === 0) return;
        try {
            await mediaApi.deleteAudios([...selectedAudioIds]);
            audios = audios.filter(aud => !selectedAudioIds.has(aud.id));
            selectedAudioIds.clear();
            selectedAudioIds = selectedAudioIds;
        } catch (e) {
            alert('Failed to delete audios');
        }
    }

    function openModal(src: string, name: string) {
        modalImageSrc = src;
        modalImageName = name;
        showModal = true;
    }
</script>

<svelte:head>
    <title>Dashboard | Y2K Video Editor</title>
</svelte:head>

<Sidebar />

<main class="main-content">
    {#if loading}
        <div class="loading-state">
            <div class="skeleton skeleton-header"></div>
            <div class="skeleton-grid">
                {#each Array(6) as _}
                    <div class="skeleton skeleton-card"></div>
                {/each}
            </div>
        </div>
    {:else}
        <!-- Header -->
        <header class="page-header">
            <div>
                <h1>Your Media</h1>
                <p class="text-muted">Manage your images and audio files</p>
            </div>
            <div class="header-actions">
                <div class="search-box">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"/>
                        <path d="m21 21-4.35-4.35"/>
                    </svg>
                    <input 
                        type="search" 
                        placeholder="Search media..." 
                        bind:value={searchQuery}
                    >
                </div>
                <Button variant="primary" on:click={() => goto('/upload')}>
                    Upload
                </Button>
            </div>
        </header>

        <!-- Images Section -->
        <section class="media-section">
            <div class="section-header">
                <h2>Images</h2>
                <span class="badge">{images.length}</span>
            </div>

            {#if filteredImages.length === 0}
                <Card variant="glass" padding="lg" hover={false}>
                    <div class="empty-state">
                        <div class="empty-icon">🖼️</div>
                        <h3>No images yet</h3>
                        <p>Upload your first image to get started</p>
                        <Button variant="secondary" on:click={() => goto('/upload')}>Upload Images</Button>
                    </div>
                </Card>
            {:else}
                <div class="media-grid">
                    {#each filteredImages as image (image.id)}
                        <div 
                            class="media-card"
                            class:selected={selectedImageIds.has(image.id)}
                        >
                            <button 
                                class="media-image"
                                on:click={() => openModal(mediaApi.getImageUrl(image.id), image.filename)}
                            >
                                <img src={mediaApi.getImageUrl(image.id)} alt={image.filename} loading="lazy" />
                            </button>
                            <div class="media-info">
                                <span class="media-name">{image.filename}</span>
                            </div>
                            <button 
                                class="select-btn"
                                class:selected={selectedImageIds.has(image.id)}
                                on:click={() => toggleImageSelection(image.id)}
                                aria-label="Select image"
                            >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                    <polyline points="20,6 9,17 4,12"/>
                                </svg>
                            </button>
                        </div>
                    {/each}
                </div>
            {/if}
        </section>

        <!-- Audios Section -->
        <section class="media-section">
            <div class="section-header">
                <h2>Audio Files</h2>
                <span class="badge">{audios.length}</span>
            </div>

            {#if audios.length === 0}
                <Card variant="glass" padding="lg" hover={false}>
                    <div class="empty-state">
                        <div class="empty-icon">🎵</div>
                        <h3>No audio files yet</h3>
                        <p>Upload audio to add to your videos</p>
                        <Button variant="secondary" on:click={() => goto('/upload')}>Upload Audio</Button>
                    </div>
                </Card>
            {:else}
                <div class="audio-list">
                    {#each audios as audio (audio.id)}
                        <div 
                            class="audio-card"
                            class:selected={selectedAudioIds.has(audio.id)}
                        >
                            <div class="audio-icon">🎵</div>
                            <div class="audio-info">
                                <span class="audio-name">{audio.filename}</span>
                                <audio controls>
                                    <source src={mediaApi.getAudioUrl(audio.id)} type="audio/mpeg">
                                </audio>
                            </div>
                            <button 
                                class="select-btn"
                                class:selected={selectedAudioIds.has(audio.id)}
                                on:click={() => toggleAudioSelection(audio.id)}
                                aria-label="Select audio"
                            >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                    <polyline points="20,6 9,17 4,12"/>
                                </svg>
                            </button>
                        </div>
                    {/each}
                </div>
            {/if}
        </section>

        <!-- Default Audios -->
        {#if defaultAudios.length > 0}
            <section class="media-section">
                <div class="section-header">
                    <h2>Default Audio Library</h2>
                    <span class="badge secondary">{defaultAudios.length}</span>
                </div>
                <div class="audio-list">
                    {#each defaultAudios as audio (audio.id)}
                        <div class="audio-card">
                            <div class="audio-icon">🎶</div>
                            <div class="audio-info">
                                <span class="audio-name">{audio.filename}</span>
                                <audio controls>
                                    <source src={mediaApi.getAudioUrl(audio.id)} type="audio/mpeg">
                                </audio>
                            </div>
                        </div>
                    {/each}
                </div>
            </section>
        {/if}
    {/if}
</main>

<!-- Selection action bar -->
{#if selectedImageIds.size > 0 || selectedAudioIds.size > 0}
    <div class="action-bar">
        <span>
            {selectedImageIds.size + selectedAudioIds.size} item(s) selected
        </span>
        <div class="action-buttons">
            <Button variant="ghost" on:click={() => { selectedImageIds.clear(); selectedAudioIds.clear(); selectedImageIds = selectedImageIds; selectedAudioIds = selectedAudioIds; }}>
                Cancel
            </Button>
            <Button variant="primary" on:click={() => selectedImageIds.size > 0 ? deleteSelectedImages() : deleteSelectedAudios()}>
                Delete Selected
            </Button>
        </div>
    </div>
{/if}

<!-- Image Modal -->
{#if showModal}
    <div class="modal-overlay" on:click={() => showModal = false} on:keypress={() => {}} role="button" tabindex="0">
        <button class="modal-close" on:click={() => showModal = false}>×</button>
        <img src={modalImageSrc} alt={modalImageName} />
        <p class="modal-caption">{modalImageName}</p>
    </div>
{/if}

<style>
    .main-content {
        margin-left: 64px;
        min-height: 100vh;
        padding: var(--space-xl);
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
        padding-left: calc(64px + var(--space-xl));
    }

    @media (max-width: 768px) {
        .main-content {
            padding-left: var(--space-md);
            padding-right: var(--space-md);
            margin-left: 64px;
        }
    }

    /* Loading state */
    .loading-state {
        animation: fadeIn 0.3s ease;
    }

    .skeleton {
        background: linear-gradient(90deg, var(--bg-secondary) 0%, var(--bg-tertiary) 50%, var(--bg-secondary) 100%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--radius-md);
    }

    .skeleton-header {
        height: 80px;
        margin-bottom: var(--space-xl);
    }

    .skeleton-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: var(--space-md);
    }

    .skeleton-card {
        aspect-ratio: 1;
    }

    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* Header */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--space-2xl);
        gap: var(--space-lg);
        flex-wrap: wrap;
    }

    .page-header h1 {
        margin-bottom: var(--space-xs);
    }

    .text-muted {
        color: var(--text-secondary);
    }

    .header-actions {
        display: flex;
        gap: var(--space-md);
        align-items: center;
    }

    .search-box {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        background: var(--bg-tertiary);
        border: 1px solid transparent;
        border-radius: var(--radius-md);
        padding: var(--space-sm) var(--space-md);
        transition: var(--transition-fast);
    }

    .search-box:focus-within {
        border-color: var(--neon-cyan);
    }

    .search-box svg {
        color: var(--text-muted);
        flex-shrink: 0;
    }

    .search-box input {
        background: transparent;
        border: none;
        color: var(--text-primary);
        width: 180px;
        padding: 0;
    }

    .search-box input:focus {
        outline: none;
        box-shadow: none;
    }

    .search-box input::placeholder {
        color: var(--text-muted);
    }

    /* Section */
    .media-section {
        margin-bottom: var(--space-2xl);
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: var(--space-md);
        margin-bottom: var(--space-lg);
    }

    .section-header h2 {
        font-size: 1.25rem;
    }

    .badge {
        background: var(--neon-cyan);
        color: var(--bg-dark);
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: var(--radius-full);
    }

    .badge.secondary {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: var(--space-2xl);
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: var(--space-md);
    }

    .empty-state h3 {
        margin-bottom: var(--space-sm);
    }

    .empty-state p {
        color: var(--text-secondary);
        margin-bottom: var(--space-lg);
    }

    /* Media grid */
    .media-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: var(--space-md);
    }

    .media-card {
        position: relative;
        background: var(--bg-secondary);
        border: var(--border-subtle);
        border-radius: var(--radius-lg);
        overflow: hidden;
        transition: var(--transition-fast);
    }

    .media-card:hover {
        border-color: rgba(0, 245, 255, 0.3);
        transform: translateY(-2px);
    }

    .media-card.selected {
        border-color: var(--neon-cyan);
        box-shadow: var(--shadow-glow-cyan);
    }

    .media-image {
        width: 100%;
        aspect-ratio: 1;
        padding: 0;
        border: none;
        cursor: pointer;
        background: var(--bg-tertiary);
    }

    .media-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .media-info {
        padding: var(--space-sm);
    }

    .media-name {
        font-size: 0.85rem;
        color: var(--text-secondary);
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .select-btn {
        position: absolute;
        top: var(--space-sm);
        right: var(--space-sm);
        width: 28px;
        height: 28px;
        border-radius: var(--radius-full);
        background: var(--bg-dark);
        border: 2px solid var(--text-muted);
        color: transparent;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: var(--transition-fast);
    }

    .select-btn:hover {
        border-color: var(--neon-cyan);
    }

    .select-btn.selected {
        background: var(--neon-cyan);
        border-color: var(--neon-cyan);
        color: var(--bg-dark);
    }

    /* Audio list */
    .audio-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
    }

    .audio-card {
        display: flex;
        align-items: center;
        gap: var(--space-md);
        padding: var(--space-md);
        background: var(--bg-secondary);
        border: var(--border-subtle);
        border-radius: var(--radius-lg);
        transition: var(--transition-fast);
    }

    .audio-card:hover {
        border-color: rgba(0, 245, 255, 0.3);
    }

    .audio-card.selected {
        border-color: var(--neon-cyan);
        box-shadow: var(--shadow-glow-cyan);
    }

    .audio-icon {
        font-size: 1.5rem;
    }

    .audio-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
    }

    .audio-name {
        font-weight: 500;
    }

    .audio-info audio {
        width: 100%;
        height: 32px;
    }

    /* Action bar */
    .action-bar {
        position: fixed;
        bottom: var(--space-xl);
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        align-items: center;
        gap: var(--space-lg);
        padding: var(--space-md) var(--space-lg);
        background: var(--bg-secondary);
        border: var(--border-subtle);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-lg);
        animation: slideUp 0.3s ease;
        z-index: 50;
    }

    .action-buttons {
        display: flex;
        gap: var(--space-sm);
    }

    /* Modal */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 200;
        animation: fadeIn 0.2s ease;
    }

    .modal-overlay img {
        max-width: 90%;
        max-height: 80vh;
        object-fit: contain;
        border-radius: var(--radius-md);
    }

    .modal-close {
        position: absolute;
        top: var(--space-xl);
        right: var(--space-xl);
        width: 48px;
        height: 48px;
        background: var(--bg-secondary);
        border: var(--border-subtle);
        border-radius: var(--radius-full);
        color: var(--text-primary);
        font-size: 1.5rem;
        cursor: pointer;
        transition: var(--transition-fast);
    }

    .modal-close:hover {
        background: var(--neon-pink);
    }

    .modal-caption {
        margin-top: var(--space-md);
        color: var(--text-secondary);
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideUp {
        from { 
            opacity: 0;
            transform: translateX(-50%) translateY(20px);
        }
        to { 
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
</style>
