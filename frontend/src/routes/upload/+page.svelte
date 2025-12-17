<script lang="ts">
    import Sidebar from '$lib/components/Sidebar.svelte';
    import Card from '$lib/components/Card.svelte';
    import Button from '$lib/components/Button.svelte';
    import { goto } from '$app/navigation';
    import { mediaApi } from '$lib/api';
    import { toasts } from '$lib/stores/toasts';

    let imageFiles: File[] = [];
    let audioFiles: File[] = [];
    let uploadingImages = false;
    let uploadingAudios = false;
    let dragOverImages = false;
    let dragOverAudios = false;

    function handleImageDrop(e: DragEvent) {
        e.preventDefault();
        dragOverImages = false;
        if (e.dataTransfer?.files) {
            const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
            imageFiles = [...imageFiles, ...files];
        }
    }

    function handleAudioDrop(e: DragEvent) {
        e.preventDefault();
        dragOverAudios = false;
        if (e.dataTransfer?.files) {
            const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('audio/'));
            audioFiles = [...audioFiles, ...files];
        }
    }

    function handleImageSelect(e: Event) {
        const input = e.target as HTMLInputElement;
        if (input.files) {
            imageFiles = [...imageFiles, ...Array.from(input.files)];
        }
    }

    function handleAudioSelect(e: Event) {
        const input = e.target as HTMLInputElement;
        if (input.files) {
            audioFiles = [...audioFiles, ...Array.from(input.files)];
        }
    }

    function removeImageFile(idx: number) {
        imageFiles = imageFiles.filter((_, i) => i !== idx);
    }

    function removeAudioFile(idx: number) {
        audioFiles = audioFiles.filter((_, i) => i !== idx);
    }

    async function uploadImages() {
        if (imageFiles.length === 0) return;
        uploadingImages = true;
        try {
            const fileList = new DataTransfer();
            imageFiles.forEach(f => fileList.items.add(f));
            await mediaApi.uploadFiles(fileList.files, 'image');
            imageFiles = [];
            toasts.show('Images uploaded successfully!', 'success');
        } catch (e) {
            toasts.show('Failed to upload images', 'error');
        } finally {
            uploadingImages = false;
        }
    }

    async function uploadAudios() {
        if (audioFiles.length === 0) return;
        uploadingAudios = true;
        try {
            const fileList = new DataTransfer();
            audioFiles.forEach(f => fileList.items.add(f));
            await mediaApi.uploadFiles(fileList.files, 'audio');
            audioFiles = [];
            toasts.show('Audio files uploaded successfully!', 'success');
        } catch (e) {
            toasts.show('Failed to upload audio files', 'error');
        } finally {
            uploadingAudios = false;
        }
    }
</script>

<svelte:head>
    <title>Upload | Y2K Video Editor</title>
</svelte:head>

<Sidebar />

<main class="main-content">
    <header class="page-header">
        <div>
            <h1>Upload Media</h1>
            <p class="text-muted">Add images and audio to your library</p>
        </div>
    </header>

    <div class="upload-grid">
        <!-- Image Upload -->
        <Card variant="glass" padding="lg" hover={false}>
            <div class="upload-section">
                <div class="section-icon">🖼️</div>
                <h2>Images</h2>
                <p class="text-muted">PNG, JPG, GIF up to 10MB each</p>

                <div 
                    class="dropzone"
                    class:dragover={dragOverImages}
                    on:drop={handleImageDrop}
                    on:dragover|preventDefault={() => dragOverImages = true}
                    on:dragleave={() => dragOverImages = false}
                    role="button"
                    tabindex="0"
                >
                    <input 
                        type="file" 
                        accept="image/*" 
                        multiple 
                        on:change={handleImageSelect}
                        id="image-input"
                    />
                    <label for="image-input">
                        <div class="dropzone-icon">
                            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="17,8 12,3 7,8"/>
                                <line x1="12" y1="3" x2="12" y2="15"/>
                            </svg>
                        </div>
                        <span>Drag & drop or click to browse</span>
                    </label>
                </div>

                {#if imageFiles.length > 0}
                    <div class="file-list">
                        {#each imageFiles as file, i}
                            <div class="file-item">
                                <span class="file-name">{file.name}</span>
                                <button class="remove-btn" on:click={() => removeImageFile(i)}>×</button>
                            </div>
                        {/each}
                    </div>
                    <Button variant="primary" loading={uploadingImages} on:click={uploadImages}>
                        Upload {imageFiles.length} Image{imageFiles.length > 1 ? 's' : ''}
                    </Button>
                {/if}
            </div>
        </Card>

        <!-- Audio Upload -->
        <Card variant="glass" padding="lg" hover={false}>
            <div class="upload-section">
                <div class="section-icon">🎵</div>
                <h2>Audio</h2>
                <p class="text-muted">MP3, WAV, OGG up to 20MB each</p>

                <div 
                    class="dropzone"
                    class:dragover={dragOverAudios}
                    on:drop={handleAudioDrop}
                    on:dragover|preventDefault={() => dragOverAudios = true}
                    on:dragleave={() => dragOverAudios = false}
                    role="button"
                    tabindex="0"
                >
                    <input 
                        type="file" 
                        accept="audio/*" 
                        multiple 
                        on:change={handleAudioSelect}
                        id="audio-input"
                    />
                    <label for="audio-input">
                        <div class="dropzone-icon">
                            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path d="M9 18V5l12-2v13"/>
                                <circle cx="6" cy="18" r="3"/>
                                <circle cx="18" cy="16" r="3"/>
                            </svg>
                        </div>
                        <span>Drag & drop or click to browse</span>
                    </label>
                </div>

                {#if audioFiles.length > 0}
                    <div class="file-list">
                        {#each audioFiles as file, i}
                            <div class="file-item">
                                <span class="file-name">{file.name}</span>
                                <button class="remove-btn" on:click={() => removeAudioFile(i)}>×</button>
                            </div>
                        {/each}
                    </div>
                    <Button variant="primary" loading={uploadingAudios} on:click={uploadAudios}>
                        Upload {audioFiles.length} Audio File{audioFiles.length > 1 ? 's' : ''}
                    </Button>
                {/if}
            </div>
        </Card>
    </div>
</main>

<style>
    .main-content {
        min-height: 100vh;
        padding: var(--space-xl);
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
        padding-left: calc(64px + var(--space-xl));
    }

    @media (max-width: 768px) {
        .main-content {
            padding-left: calc(64px + var(--space-md));
            padding-right: var(--space-md);
        }
        .upload-grid {
            grid-template-columns: 1fr;
        }
    }

    .page-header {
        margin-bottom: var(--space-2xl);
    }

    .page-header h1 {
        margin-bottom: var(--space-xs);
    }

    .text-muted {
        color: var(--text-secondary);
    }

    .upload-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: var(--space-xl);
    }

    .upload-section {
        text-align: center;
    }

    .section-icon {
        font-size: 3rem;
        margin-bottom: var(--space-md);
    }

    .upload-section h2 {
        margin-bottom: var(--space-xs);
    }

    .upload-section > p {
        margin-bottom: var(--space-lg);
    }

    .dropzone {
        border: 2px dashed var(--bg-elevated);
        border-radius: var(--radius-lg);
        padding: var(--space-2xl);
        transition: var(--transition-fast);
        cursor: pointer;
    }

    .dropzone:hover,
    .dropzone.dragover {
        border-color: var(--neon-cyan);
        background: rgba(0, 245, 255, 0.05);
    }

    .dropzone input {
        display: none;
    }

    .dropzone label {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-md);
        cursor: pointer;
    }

    .dropzone-icon {
        color: var(--text-muted);
        transition: var(--transition-fast);
    }

    .dropzone:hover .dropzone-icon {
        color: var(--neon-cyan);
    }

    .dropzone span {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .file-list {
        margin-top: var(--space-lg);
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
        max-height: 200px;
        overflow-y: auto;
    }

    .file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--space-sm) var(--space-md);
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
    }

    .file-name {
        font-size: 0.85rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .remove-btn {
        width: 24px;
        height: 24px;
        border-radius: var(--radius-full);
        background: none;
        border: none;
        color: var(--text-muted);
        font-size: 1.25rem;
        cursor: pointer;
        transition: var(--transition-fast);
    }

    .remove-btn:hover {
        color: var(--neon-pink);
    }

    .upload-section :global(.btn) {
        width: 100%;
        margin-top: var(--space-lg);
    }
</style>
