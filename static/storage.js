/**
 * StorageService for Dare-Roulette
 * Handles cross-platform storage (Mobile: Capacitor Preferences, Web: LocalStorage)
 */
class StorageService {
    _isCapacitor() {
        return (typeof Capacitor !== 'undefined' &&
            Capacitor.Plugins &&
            Capacitor.Plugins.Preferences);
    }

    /**
     * Save a value to storage
     * @param {string} key 
     * @param {string} value 
     */
    async set(key, value) {
        try {
            const stringValue = String(value);
            if (this._isCapacitor()) {
                console.log('StorageService: Saving to Capacitor Preferences', key);
                await Capacitor.Plugins.Preferences.set({
                    key: key,
                    value: stringValue
                });
            } else {
                console.log('StorageService: Saving to localStorage', key);
                localStorage.setItem(key, stringValue);
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
            if (this._isCapacitor()) {
                console.log('StorageService: Reading from Capacitor Preferences', key);
                const result = await Capacitor.Plugins.Preferences.get({ key: key });
                return result.value;
            } else {
                console.log('StorageService: Reading from localStorage', key);
                return localStorage.getItem(key);
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
            if (this._isCapacitor()) {
                await Capacitor.Plugins.Preferences.remove({ key: key });
            } else {
                localStorage.removeItem(key);
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
            if (this._isCapacitor()) {
                await Capacitor.Plugins.Preferences.clear();
            } else {
                localStorage.clear();
            }
        } catch (error) {
            console.error('StorageService clear error:', error);
        }
    }
}

// Create and expose global instance
window.storageService = new StorageService();
