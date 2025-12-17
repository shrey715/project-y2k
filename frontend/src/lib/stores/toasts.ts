import { writable } from 'svelte/store';

export interface Toast {
    id: number;
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
    duration?: number;
}

function createToastStore() {
    const { subscribe, update } = writable<Toast[]>([]);
    let nextId = 0;

    return {
        subscribe,
        show: (message: string, type: Toast['type'] = 'info', duration = 4000) => {
            const id = nextId++;
            const toast: Toast = { id, message, type, duration };

            update(toasts => [...toasts, toast]);

            if (duration > 0) {
                setTimeout(() => {
                    update(toasts => toasts.filter(t => t.id !== id));
                }, duration);
            }

            return id;
        },
        success: (message: string, duration = 4000) => {
            return createToastStore().show(message, 'success', duration);
        },
        error: (message: string, duration = 6000) => {
            return createToastStore().show(message, 'error', duration);
        },
        dismiss: (id: number) => {
            update(toasts => toasts.filter(t => t.id !== id));
        },
        clear: () => {
            update(() => []);
        }
    };
}

export const toasts = createToastStore();
