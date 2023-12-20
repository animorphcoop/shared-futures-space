export interface Settings {
    MAPTILER_API_KEY: string
}

// window.settings is set in base.html
// @ts-expect-error
const settings = (window.settings ?? {}) as Settings

export const MAPTILER_API_KEY = settings.MAPTILER_API_KEY