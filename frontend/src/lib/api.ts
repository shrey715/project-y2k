// Use environment variable for production backend URL (remove trailing slash)
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

interface ApiOptions {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
    body?: unknown;
    headers?: Record<string, string>;
}

async function apiRequest<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options;

    const config: RequestInit = {
        method,
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, config);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || error.message || 'Request failed');
    }

    return response.json();
}

// Auth API
export const authApi = {
    login: (username: string, password: string) =>
        apiRequest<{ status: string; message: string }>('/api/auth/login', {
            method: 'POST',
            body: { username, password }
        }),

    signup: (username: string, email: string, password: string) =>
        apiRequest<{ status: string; message: string }>('/api/auth/signup', {
            method: 'POST',
            body: { username, email, password }
        }),

    logout: () => fetch('/api/auth/logout', { credentials: 'include' }),

    check: () => apiRequest<{ authenticated: boolean; username?: string }>('/api/auth/check')
};

// Users API
export const usersApi = {
    me: () => apiRequest<{
        username: string;
        email: string;
        images_cnt: number;
        audios_cnt: number;
    }>('/api/users/me'),

    dashboard: () => apiRequest<{
        username: string;
        images: Array<{ id: number; filename: string }>;
        audios: Array<{ id: number; filename: string }>;
        default_audios: Array<{ id: number; filename: string }>;
    }>('/api/users/dashboard')
};

// Media API
export const mediaApi = {
    getImages: () => apiRequest<Array<{ id: number; filename: string }>>('/api/media/images'),

    getAudios: () => apiRequest<Array<{ id: number; filename: string }>>('/api/media/audios'),

    uploadFiles: async (files: FileList, fileType: 'image' | 'audio') => {
        const formData = new FormData();
        Array.from(files).forEach(file => formData.append('files', file));
        formData.append('file_type', fileType);

        const response = await fetch('/api/media/upload', {
            method: 'POST',
            credentials: 'include',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        return response.json();
    },

    deleteImages: (imageIds: number[]) =>
        fetch(`/api/media/images?image_ids=${imageIds.join(',')}`, {
            method: 'DELETE',
            credentials: 'include'
        }),

    deleteAudios: (audioIds: number[]) =>
        fetch(`/api/media/audios?audio_ids=${audioIds.join(',')}`, {
            method: 'DELETE',
            credentials: 'include'
        }),

    getImageUrl: (id: number) => `/api/media/images/${id}`,
    getAudioUrl: (id: number) => `/api/media/audios/${id}`
};

// Video API
export const videoApi = {
    getEditorData: () => apiRequest<{
        username: string;
        images: Array<{ id: number; filename: string }>;
        audios: Array<{ id: number; filename: string }>;
    }>('/api/video/editor-data'),

    render: (data: unknown) => apiRequest<{ success: boolean; message?: string }>('/api/video/render', {
        method: 'POST',
        body: data
    }),

    viewUrl: '/api/video/view'
};

// Admin API
export const adminApi = {
    getUsers: () => apiRequest<{
        users: Array<{
            id: number;
            username: string;
            email: string;
            images_cnt: number;
            audios_cnt: number;
        }>
    }>('/api/admin/users'),

    getMedia: () => apiRequest<{
        images: Array<{ id: number; filename: string; user_id: number }>;
        audios: Array<{ id: number; filename: string; user_id: number }>;
    }>('/api/admin/media')
};
