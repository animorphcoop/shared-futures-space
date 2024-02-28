export interface Settings {
    MAPTILER_API_KEY: string
}

// window.settings is set in base.html
// @ts-expect-error
const settings = (window.settings ?? {}) as Settings

export const MAPTILER_API_KEY = settings.MAPTILER_API_KEY
export const MAPTILER_STYLE_URL = `https://api.maptiler.com/maps/63bf10e6-2086-435f-8831-98c897778596/style.json?key=${MAPTILER_API_KEY}`