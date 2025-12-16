import { writable, derived } from 'svelte/store';
import { authApi } from '$lib/api';

interface User {
    username: string;
    email?: string;
}

interface AuthState {
    user: User | null;
    loading: boolean;
    checked: boolean;
}

function createAuthStore() {
    const { subscribe, set, update } = writable<AuthState>({
        user: null,
        loading: true,
        checked: false
    });

    return {
        subscribe,

        async check() {
            update(s => ({ ...s, loading: true }));
            try {
                const data = await authApi.check();
                set({
                    user: data.authenticated ? { username: data.username! } : null,
                    loading: false,
                    checked: true
                });
                return data.authenticated;
            } catch {
                set({ user: null, loading: false, checked: true });
                return false;
            }
        },

        async login(username: string, password: string) {
            const result = await authApi.login(username, password);
            if (result.status === 'success') {
                set({ user: { username }, loading: false, checked: true });
            }
            return result;
        },

        async signup(username: string, email: string, password: string) {
            const result = await authApi.signup(username, email, password);
            if (result.status === 'success') {
                set({ user: { username }, loading: false, checked: true });
            }
            return result;
        },

        async logout() {
            await authApi.logout();
            set({ user: null, loading: false, checked: true });
        },

        reset() {
            set({ user: null, loading: false, checked: false });
        }
    };
}

export const auth = createAuthStore();
export const isAuthenticated = derived(auth, $auth => $auth.user !== null);
export const isAdmin = derived(auth, $auth => $auth.user?.username === 'admin');
export const currentUser = derived(auth, $auth => $auth.user);
