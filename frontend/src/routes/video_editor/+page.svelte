<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import Sidebar from '$lib/components/Sidebar.svelte';
    import Card from '$lib/components/Card.svelte';
    import Button from '$lib/components/Button.svelte';
    import Input from '$lib/components/Input.svelte';
    import Select from '$lib/components/Select.svelte';
    import { videoApi, mediaApi } from '$lib/api';
    import { toasts } from '$lib/stores/toasts';

    interface ImageItem { id: number; filename: string; }
    interface AudioItem { id: number; filename: string; }
    interface TimelineImage {
        image_id: string;
        filename: string;
        transition?: { name: string; duration: number };
        background_color?: string;
        duration?: number;
    }
    interface TimelineAudio {
        audio_id: string;
        filename: string;
        volume?: number;
        duration?: number;
    }

    let availableImages: ImageItem[] = [];
    let availableAudios: AudioItem[] = [];
    let timelineImages: TimelineImage[] = [];
    let timelineAudios: TimelineAudio[] = [];
    let selectedImageIndex = -1;
    let selectedAudioIndex = -1;
    let showImageModal = false;
    let showAudioModal = false;
    let rendering = false;
    let previewUrl = '';

    // Settings
    let projectName = '';
    let resolution = '360p';
    let imageTransition = 'dissolve';
    let backgroundColor = '#000000';
    let imageDuration = 5;
    let audioVolume = 50;
    let audioDuration = 5;

    onMount(async () => {
        try {
            const data = await videoApi.getEditorData();
            availableImages = data.images || [];
            availableAudios = data.audios || [];
        } catch (e) {
            console.error('Error:', e);
        }
    });

    function addToTimeline(type: 'image' | 'audio', id: number, filename: string) {
        if (type === 'image') {
            timelineImages = [...timelineImages, { image_id: id.toString(), filename, duration: 5 }];
        } else {
            timelineAudios = [...timelineAudios, { audio_id: id.toString(), filename, duration: 5, volume: 50 }];
        }
    }

    function removeFromTimeline(type: 'image' | 'audio', idx: number) {
        if (type === 'image') {
            timelineImages = timelineImages.filter((_, i) => i !== idx);
            if (selectedImageIndex === idx) selectedImageIndex = -1;
        } else {
            timelineAudios = timelineAudios.filter((_, i) => i !== idx);
            if (selectedAudioIndex === idx) selectedAudioIndex = -1;
        }
    }

    function selectTimelineItem(type: 'image' | 'audio', idx: number) {
        if (type === 'image') {
            selectedImageIndex = idx;
            selectedAudioIndex = -1;
            const item = timelineImages[idx];
            imageTransition = item.transition?.name || 'dissolve';
            backgroundColor = item.background_color || '#000000';
            imageDuration = item.duration || 5;
        } else {
            selectedAudioIndex = idx;
            selectedImageIndex = -1;
            const item = timelineAudios[idx];
            audioVolume = item.volume || 50;
            audioDuration = item.duration || 5;
        }
    }

    function applySettings() {
        if (selectedImageIndex >= 0) {
            timelineImages[selectedImageIndex].transition = { name: imageTransition, duration: 1 };
            timelineImages[selectedImageIndex].background_color = backgroundColor;
            timelineImages[selectedImageIndex].duration = imageDuration;
            timelineImages = timelineImages;
        } else if (selectedAudioIndex >= 0) {
            timelineAudios[selectedAudioIndex].volume = audioVolume;
            timelineAudios[selectedAudioIndex].duration = audioDuration;
            timelineAudios = timelineAudios;
        }
    }

    async function previewVideo() {
        if (timelineImages.length === 0) {
            alert('Add at least one image to the timeline');
            return;
        }
        rendering = true;
        previewUrl = '';
        try {
            // Use selected resolution for preview too
            const resMap: Record<string, number[]> = {
                '360p': [640, 360],
                '720p': [1280, 720],
                '1080p': [1920, 1080]
            };
            const res = resMap[resolution] || [640, 360];
            const data = {
                info: { title: projectName || 'untitled', resolution: res, framerate: 12 },
                video: { images: timelineImages },
                audios: timelineAudios
            };
            const result = await videoApi.render(data);
            if (result.success) {
                previewUrl = videoApi.getViewUrl() + '?t=' + Date.now();
            } else {
                toasts.show('Render failed: ' + (result.detail || result.message), 'error');
            }
        } catch (e) {
            toasts.show('Error rendering video', 'error');
        } finally {
            rendering = false;
        }
    }

    async function exportVideo() {
        if (timelineImages.length === 0) {
            alert('Add at least one image to the timeline');
            return;
        }
        rendering = true;
        try {
            // Map resolution string to actual dimensions
            const resMap: Record<string, number[]> = {
                '360p': [640, 360],
                '720p': [1280, 720],
                '1080p': [1920, 1080]
            };
            const res = resMap[resolution] || [640, 360];
            const data = {
                info: { title: projectName || 'untitled', resolution: res, framerate: 12 },
                video: { images: timelineImages },
                audios: timelineAudios
            };
            const result = await videoApi.render(data);
            if (result.success) {
                const a = document.createElement('a');
                a.href = videoApi.getViewUrl();
                a.download = (projectName || 'video') + '.mp4';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                toasts.show('Video exported successfully!', 'success');
            } else {
                toasts.show('Export failed: ' + (result.detail || result.message), 'error');
            }
        } catch (e) {
            toasts.show('Error exporting video', 'error');
        } finally {
            rendering = false;
        }
    }
</script>

<svelte:head>
    <title>Video Editor | Y2K</title>
</svelte:head>

<Sidebar />

<main class="main-content">
    <!-- Toolbar -->
    <header class="toolbar">
        <Input 
            placeholder="Project Name" 
            bind:value={projectName}
        />
        <div class="toolbar-actions">
            <Button variant="secondary" on:click={() => showImageModal = true}>Add Image</Button>
            <Button variant="secondary" on:click={() => showAudioModal = true}>Add Audio</Button>
            <Select 
                bind:value={resolution}
                options={[
                    { value: '360p', label: '360p' },
                    { value: '720p', label: '720p' },
                    { value: '1080p', label: '1080p' }
                ]}
            />
            <Button variant="secondary" loading={rendering} on:click={previewVideo}>Preview</Button>
            <Button variant="primary" loading={rendering} on:click={exportVideo}>Export</Button>
        </div>
    </header>

    <div class="editor-layout">
        <!-- Preview -->
        <Card variant="glass" padding="md" hover={false}>
            <div class="preview-panel">
                {#if rendering}
                    <div class="preview-loading">
                        <div class="spinner"></div>
                        <span>Rendering...</span>
                    </div>
                {:else if previewUrl}
                    <video controls autoplay src={previewUrl}><track kind="captions" /></video>
                {:else if selectedImageIndex >= 0}
                    <img src={mediaApi.getImageUrl(parseInt(timelineImages[selectedImageIndex].image_id))} alt="Selected" />
                {:else}
                    <div class="preview-placeholder">
                        <span>🎬</span>
                        <p>Select an item or click Preview</p>
                    </div>
                {/if}
            </div>
        </Card>

        <!-- Settings Panel -->
        <Card variant="default" padding="md" hover={false}>
            <div class="settings-panel">
                <h3>Settings</h3>
                {#if selectedImageIndex >= 0}
                    <div class="setting-group">
                        <label>Transition</label>
                        <select bind:value={imageTransition}>
                            <option value="dissolve">Dissolve</option>
                            <option value="fadeblack">Fade Black</option>
                            <option value="slideup">Slide Up</option>
                            <option value="slidedown">Slide Down</option>
                            <option value="slideleft">Slide Left</option>
                            <option value="slideright">Slide Right</option>
                        </select>
                    </div>
                    <div class="setting-group">
                        <label>Background</label>
                        <input type="color" bind:value={backgroundColor} />
                    </div>
                    <div class="setting-group">
                        <label>Duration: {imageDuration}s</label>
                        <input type="range" min="1" max="30" bind:value={imageDuration} />
                    </div>
                    <Button variant="primary" on:click={applySettings}>Apply</Button>
                {:else if selectedAudioIndex >= 0}
                    <div class="setting-group">
                        <label>Volume: {audioVolume}%</label>
                        <input type="range" min="0" max="100" bind:value={audioVolume} />
                    </div>
                    <div class="setting-group">
                        <label>Duration: {audioDuration}s</label>
                        <input type="range" min="1" max="30" bind:value={audioDuration} />
                    </div>
                    <Button variant="primary" on:click={applySettings}>Apply</Button>
                {:else}
                    <p class="no-selection">Select a timeline item to edit</p>
                {/if}
            </div>
        </Card>
    </div>

    <!-- Timeline -->
    <div class="timeline-section">
        <div class="timeline-row">
            <span class="timeline-label">🎵 Audio</span>
            <div class="timeline-track">
                {#each timelineAudios as audio, i}
                    <!-- svelte-ignore a11y_no_static_element_interactions -->
                    <div 
                        class="timeline-item audio" 
                        class:selected={selectedAudioIndex === i}
                        on:click={() => selectTimelineItem('audio', i)}
                        on:keypress={() => {}}
                        role="button"
                        tabindex="0"
                    >
                        <span>{audio.filename}</span>
                        <button class="remove" aria-label="Remove audio" on:click|stopPropagation={() => removeFromTimeline('audio', i)}>×</button>
                    </div>
                {/each}
                {#if timelineAudios.length === 0}
                    <span class="empty-track">No audio added</span>
                {/if}
            </div>
        </div>
        <div class="timeline-row">
            <span class="timeline-label">🖼️ Images</span>
            <div class="timeline-track">
                {#each timelineImages as image, i}
                    <!-- svelte-ignore a11y_no_static_element_interactions -->
                    <div 
                        class="timeline-item image" 
                        class:selected={selectedImageIndex === i}
                        on:click={() => selectTimelineItem('image', i)}
                        on:keypress={() => {}}
                        role="button"
                        tabindex="0"
                    >
                        <img src={mediaApi.getImageUrl(parseInt(image.image_id))} alt={image.filename} />
                        <button class="remove" aria-label="Remove image" on:click|stopPropagation={() => removeFromTimeline('image', i)}>×</button>
                    </div>
                {/each}
                {#if timelineImages.length === 0}
                    <span class="empty-track">No images added</span>
                {/if}
            </div>
        </div>
    </div>
</main>

<!-- Image Modal -->
{#if showImageModal}
    <div class="modal-overlay" on:click={() => showImageModal = false} on:keypress={() => {}} role="button" tabindex="0">
        <Card variant="glass" padding="lg" hover={false}>
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="modal-content" on:click|stopPropagation on:keypress={() => {}}>
                <h2>Select Images</h2>
                <p class="modal-hint">Click to add to timeline. Images play in order added.</p>
                <div class="image-grid">
                    {#each availableImages as img}
                        <button class="image-item" on:click={() => { addToTimeline('image', img.id, img.filename); showImageModal = false; }}>
                            <img src={mediaApi.getImageUrl(img.id)} alt={img.filename} />
                            <div class="image-overlay">
                                <span class="image-add">+</span>
                            </div>
                        </button>
                    {/each}
                    {#if availableImages.length === 0}
                        <p class="empty-images">No images available. Upload some first!</p>
                    {/if}
                </div>
                <Button variant="ghost" on:click={() => showImageModal = false}>Close</Button>
            </div>
        </Card>
    </div>
{/if}

<!-- Audio Modal -->
{#if showAudioModal}
    <div class="modal-overlay" on:click={() => showAudioModal = false} on:keypress={() => {}} role="button" tabindex="0">
        <Card variant="glass" padding="lg" hover={false}>
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="modal-content" on:click|stopPropagation on:keypress={() => {}}>
                <h2>Select Audio</h2>
                <p class="modal-hint">Click to add to timeline. Multiple audios play sequentially.</p>
                <div class="audio-list">
                    {#each availableAudios as audio}
                        <button class="audio-item" on:click={() => { addToTimeline('audio', audio.id, audio.filename); showAudioModal = false; }}>
                            <span class="audio-icon">♪</span>
                            <span class="audio-name">{audio.filename}</span>
                            <span class="audio-add">+</span>
                        </button>
                    {/each}
                    {#if availableAudios.length === 0}
                        <p class="empty-audio">No audio files available. Upload some first!</p>
                    {/if}
                </div>
                <Button variant="ghost" on:click={() => showAudioModal = false}>Close</Button>
            </div>
        </Card>
    </div>
{/if}

<style>
    .main-content {
        min-height: 100vh;
        padding: var(--space-lg);
        display: flex;
        flex-direction: column;
        gap: var(--space-lg);
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
        padding-left: calc(64px + var(--space-lg));
    }

    @media (max-width: 1024px) {
        .main-content {
            padding-left: calc(64px + var(--space-md));
            padding-right: var(--space-md);
        }
        .editor-layout {
            grid-template-columns: 1fr;
        }
    }

    .toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-md);
        flex-wrap: wrap;
        padding: var(--space-md);
        background: var(--bg-secondary);
        border: 2px solid var(--neon-cyan);
        margin-bottom: var(--space-lg);
    }

    .project-name {
        background: var(--bg-dark);
        border: 2px solid var(--text-muted);
        padding: var(--space-sm) var(--space-md);
        color: var(--text-primary);
        font-family: var(--font-display);
        font-size: 1.2rem;
        width: 200px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .project-name::placeholder {
        color: var(--text-muted);
        text-transform: uppercase;
    }

    .project-name:focus {
        border-color: var(--neon-cyan);
        outline: none;
        box-shadow: 0 0 8px rgba(64, 224, 208, 0.3);
    }

    .toolbar-actions {
        display: flex;
        gap: var(--space-sm);
        align-items: center;
    }

    .toolbar-actions select {
        background: var(--bg-dark);
        border: 2px solid var(--neon-pink);
        padding: var(--space-sm) var(--space-md);
        color: var(--neon-pink);
        font-family: var(--font-display);
        font-size: 1.1rem;
        text-transform: uppercase;
        cursor: pointer;
        min-width: 80px;
    }

    .toolbar-actions select:focus {
        outline: none;
        box-shadow: 0 0 8px rgba(224, 102, 160, 0.3);
    }

    .toolbar-actions select option {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }

    .editor-layout {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: var(--space-lg);
    }

    .preview-panel {
        aspect-ratio: 16/9;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-dark);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    .preview-panel video,
    .preview-panel img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }

    .preview-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-md);
        color: var(--text-secondary);
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--bg-tertiary);
        border-top-color: var(--neon-cyan);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .preview-placeholder {
        text-align: center;
        color: var(--text-muted);
    }

    .preview-placeholder span {
        font-size: 3rem;
    }

    .settings-panel {
        display: flex;
        flex-direction: column;
        gap: var(--space-md);
    }

    .setting-group {
        display: flex;
        flex-direction: column;
        gap: var(--space-xs);
    }

    .setting-group label {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .setting-group input[type="range"] {
        width: 100%;
    }

    .no-selection {
        color: var(--text-muted);
        text-align: center;
        font-size: 0.9rem;
    }

    .timeline-section {
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: var(--space-md);
    }

    .timeline-row {
        display: flex;
        align-items: center;
        gap: var(--space-md);
        padding: var(--space-sm) 0;
    }

    .timeline-row + .timeline-row {
        border-top: var(--border-subtle);
    }

    .timeline-label {
        width: 80px;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .timeline-track {
        flex: 1;
        display: flex;
        gap: var(--space-sm);
        overflow-x: auto;
        padding: var(--space-sm) 0;
    }

    .timeline-item {
        position: relative;
        background: var(--bg-tertiary);
        border: 2px solid transparent;
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: var(--transition-fast);
    }

    .timeline-item:hover {
        border-color: var(--neon-cyan);
    }

    .timeline-item.selected {
        border-color: var(--neon-cyan);
        box-shadow: var(--shadow-glow-cyan);
    }

    .timeline-item.image {
        width: 80px;
        height: 60px;
        padding: 0;
        overflow: hidden;
    }

    .timeline-item.image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .timeline-item.audio {
        padding: var(--space-sm) var(--space-md);
        padding-right: 32px;
        font-size: 0.8rem;
        white-space: nowrap;
    }

    .timeline-item .remove {
        position: absolute;
        top: 2px;
        right: 2px;
        width: 20px;
        height: 20px;
        border-radius: var(--radius-full);
        background: rgba(0,0,0,0.6);
        border: none;
        color: white;
        font-size: 14px;
        cursor: pointer;
        opacity: 0;
        transition: var(--transition-fast);
    }

    .timeline-item:hover .remove {
        opacity: 1;
    }

    .timeline-item .remove:hover {
        background: var(--neon-pink);
    }

    .empty-track {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-style: italic;
    }

    /* Modals */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 200;
    }

    .modal-content {
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
    }

    .modal-content h2 {
        margin-bottom: var(--space-lg);
    }

    .modal-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: var(--space-sm);
        margin-bottom: var(--space-lg);
    }

    .modal-item {
        aspect-ratio: 1;
        border: 2px solid transparent;
        border-radius: var(--radius-md);
        overflow: hidden;
        cursor: pointer;
        background: none;
        padding: 0;
        transition: var(--transition-fast);
    }

    .modal-item:hover {
        border-color: var(--neon-cyan);
    }

    .modal-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Improved Image Grid */
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: var(--space-md);
        margin-bottom: var(--space-lg);
        max-height: 400px;
        overflow-y: auto;
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* IE/Edge */
    }

    .image-grid::-webkit-scrollbar {
        display: none; /* Chrome/Safari */
    }

    .image-item {
        position: relative;
        aspect-ratio: 1;
        border: 2px solid var(--text-muted);
        overflow: hidden;
        cursor: pointer;
        background: var(--bg-tertiary);
        padding: 0;
        transition: all 0.15s ease;
    }

    .image-item:hover {
        border-color: var(--neon-cyan);
        transform: scale(1.02);
    }

    .image-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .image-overlay {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.15s ease;
    }

    .image-item:hover .image-overlay {
        opacity: 1;
    }

    .image-add {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--neon-cyan);
        color: var(--bg-dark);
        font-weight: bold;
        font-size: 1.5rem;
        border: 2px solid var(--neon-cyan);
    }

    .empty-images {
        grid-column: 1 / -1;
        color: var(--text-muted);
        text-align: center;
        padding: var(--space-lg);
    }

    .modal-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
        margin-bottom: var(--space-lg);
    }

    .modal-audio-item {
        padding: var(--space-md);
        background: var(--bg-tertiary);
        border: var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        text-align: left;
        transition: var(--transition-fast);
    }

    .modal-audio-item:hover {
        border-color: var(--neon-cyan);
    }

    /* Improved Audio List */
    .modal-hint {
        color: var(--text-muted);
        font-size: 1rem;
        margin-bottom: var(--space-md);
    }

    .audio-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-sm);
        margin-bottom: var(--space-lg);
        max-height: 300px;
        overflow-y: auto;
    }

    .audio-item {
        display: flex;
        align-items: center;
        gap: var(--space-md);
        padding: var(--space-md);
        background: var(--bg-tertiary);
        border: 2px solid var(--text-muted);
        cursor: pointer;
        transition: all 0.15s ease;
        font-family: var(--font-display);
        font-size: 1.1rem;
    }

    .audio-item:hover {
        border-color: var(--neon-cyan);
        background: rgba(64, 224, 208, 0.1);
    }

    .audio-item:hover .audio-add {
        background: var(--neon-cyan);
        color: var(--bg-dark);
    }

    .audio-icon {
        font-size: 1.5rem;
        color: var(--neon-pink);
    }

    .audio-name {
        flex: 1;
        color: var(--text-primary);
        text-align: left;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .audio-add {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-secondary);
        border: 2px solid var(--neon-cyan);
        color: var(--neon-cyan);
        font-weight: bold;
        font-size: 1.2rem;
        transition: all 0.15s ease;
    }

    .empty-audio {
        color: var(--text-muted);
        text-align: center;
        padding: var(--space-lg);
    }
</style>

