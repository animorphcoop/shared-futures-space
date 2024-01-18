import Alpine from "alpinejs";

import maplibregl, {GeoJSONSource, PaddingOptions, RequireAtLeastOne} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import pin from './map_pin.png'
import circle from './map_circle.png'

import { MAPTILER_API_KEY } from '../settings.ts'

type MapCoordinates = [number, number]

interface MapMarker {
    name: string
    icon: 'pin' | 'circle'
    coordinates: MapCoordinates
}

type Padding = RequireAtLeastOne<PaddingOptions>

interface MapOptions {
    markers?: MapMarker[]
    center?: MapCoordinates
    zoom?: number
    cursor?: string // css cursor value, e.g. pointer
    padding?: Padding
}

const DEFAULT_CENTER: MapCoordinates = [-5.9213, 54.5996]
const DEFAULT_ZOOM = 15
const BASE_PADDING = 80 // always have at least this much padding

/**
 *  A directive to show a map. Usage:
 *
 *      <div x-map="{ markers: [] }"
 *           @click-marker="console.log('you clicked on marker', $event.detail)"
 *           @click-map="console.log('you clicked the map at coords', $event.detail)"></div>
 *
 *  See the MapOptions interface for what you can put in there
 */
Alpine.directive('map', (
    el,
    { expression },
    { cleanup, evaluateLater, effect },
) => {
    const optionsLater = evaluateLater(expression)

    const map = new maplibregl.Map({
        container: el,
        // style: `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_API_KEY}`,
        // My customized map
        style: `https://api.maptiler.com/maps/697dfe25-8087-42f1-a3f9-73983704eebf/style.json?key=${MAPTILER_API_KEY}`,
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
        attributionControl: false,
    })

    async function loadImage(id: string, url: string) {
        return new Promise((resolve, reject) => {
            map.loadImage(url, (err, image) => {
                if (err) return reject(err)
                // @ts-expect-error
                map.addImage(id, image)
                resolve(null)
            })
        })
    }

    map.on('load', async () => {
        await Promise.all([
            loadImage('pin', pin),
            loadImage('circle', circle),
        ])

        map.addSource('markers', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: [],
            },
        })

        map.addLayer({
            'id': 'markers',
            'type': 'symbol',
            'source': 'markers',
            'layout': {
                'icon-image': ["get", "icon"],
                'icon-size': 1,
                // This means markers do not fade in
                'icon-allow-overlap': true
            }
        })

        map.on('click', e => {
            const feature = map.queryRenderedFeatures(e.point, {
                layers: ['markers'],
            })?.[0]
            if (feature) {
                const detail = JSON.parse(feature.properties.marker)
                el.dispatchEvent(new CustomEvent("click-marker", { detail }))
            }
            else {
                const { lng, lat } = e.lngLat
                const detail = { coordinates: [lng, lat] }
                el.dispatchEvent(new CustomEvent("click-map", { detail }))
            }
        })

        effect(() => {
            optionsLater(value => {
                const options = value as MapOptions
                const {
                    center,
                    zoom,
                    markers,
                    cursor,
                    padding,
                } = options
                if (cursor) {
                    map.getCanvas().style.cursor = cursor
                }
                if (center) {
                    const currentZoom = map.getZoom()
                    map.flyTo({
                        center: center,
                        // in order:
                        // 1. specified zoom
                        // 2. current zoom if we're more zoomed in than default
                        // 3. default zoom
                        zoom: zoom ?? (DEFAULT_ZOOM > currentZoom ? DEFAULT_ZOOM : currentZoom),
                    })
                }
                setMarkers(markers ?? [], padding)
            })
        })
    })

    function setMarkers(markers: MapMarker[], padding?: Padding) {
        const source = map.getSource('markers') as GeoJSONSource | undefined
        if (!source) return
        source.setData({
            type: 'FeatureCollection',
            features: markers.map(marker => ({
                type: 'Feature',
                properties: {
                    icon: marker.icon ?? 'pin',
                    marker: JSON.stringify(marker),
                },
                geometry: {
                    type: 'Point',
                    coordinates: marker.coordinates,
                }
            }))
        })
        if (markers.length > 1) {
            // Fit bounds automatically when multiple markers
            const firstLngLat = new maplibregl.LngLat(markers[0].coordinates[0], markers[0].coordinates[1])
            const bounds = markers.reduce(
                (bounds, marker) => bounds.extend(marker.coordinates),
                new maplibregl.LngLatBounds(firstLngLat)
            )
            map.fitBounds(bounds, {
                padding: addBasePadding(padding),
                // Ensure we don't go too crazy zooming in close
                maxZoom: DEFAULT_ZOOM,
            })
        }

    }

    cleanup(() => map.remove())
})

function addBasePadding(padding?: Padding): PaddingOptions {
    const resultPadding: PaddingOptions = {
        top: BASE_PADDING,
        bottom: BASE_PADDING,
        right: BASE_PADDING,
        left: BASE_PADDING,
    }
    if (padding) {
        const keys = ['top', 'bottom', 'right', 'left'] as const
        for (const key of keys) {
            resultPadding[key] += (padding?.[key] ?? 0)
        }
    }
    return resultPadding
}