/**
 * StorageService for Dare-Roulette
 * Handles cross-platform storage (Mobile: Capacitor Preferences, Web: SessionStorage)
 */
class StorageService {
    constructor() {
        // Check if Capacitor environment and Preferences plugin are available
        this.isCapacitor = typeof Capacitor !== 'undefined' &&
            Capacitor.Plugins &&
            Capacitor.Plugins.Preferences;
    }

    /**
     * Save a value to storage
     * @param {string} key 
     * @param {string} value 
     */
    async set(key, value) {
        try {
            const stringValue = String(value);
            if (this.isCapacitor) {
                await Capacitor.Plugins.Preferences.set({
                    key: key,
                    value: stringValue
                });
            } else {
                sessionStorage.setItem(key, stringValue);
            }
        } catch (error) {
            console.error('StorageService set error:', error);
        }
    }

    /**
     * Get a value from storage
     * @param {string} key 
     * @returns {Promise<string|null>}
     */
    async get(key) {
        try {
            if (this.isCapacitor) {
                const result = await Capacitor.Plugins.Preferences.get({ key: key });
                return result.value;
            } else {
                return sessionStorage.getItem(key);
            }
        } catch (error) {
            console.error('StorageService get error:', error);
            return null;
        }
    }

    /**
     * Remove a value from storage
     * @param {string} key 
     */
    async remove(key) {
        try {
            if (this.isCapacitor) {
                await Capacitor.Plugins.Preferences.remove({ key: key });
            } else {
                sessionStorage.removeItem(key);
            }
        } catch (error) {
            console.error('StorageService remove error:', error);
        }
    }

    /**
     * Clear all storage
     */
    async clear() {
        try {
            if (this.isCapacitor) {
                await Capacitor.Plugins.Preferences.clear();
            } else {
                sessionStorage.clear();
            }
        } catch (error) {
            console.error('StorageService clear error:', error);
        }
    }
}

// Create and expose global instance
window.storageService = new StorageService();
