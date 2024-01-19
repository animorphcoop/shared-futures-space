import Alpine from "alpinejs";

import maplibregl, {GeoJSONSource, PaddingOptions, RequireAtLeastOne} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import pin from './map_pin.png'
import circle from './map_circle.png'
import CSS from 'csstype'

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
    cursor?: CSS.Properties['cursor']
    padding?: Padding
    autofit?: boolean // whether to
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

    let _map: maplibregl.Map
    cleanup(() => _map?.remove())

    async function loadImage(map: maplibregl.Map, id: string, url: string) {
        return new Promise((resolve, reject) => {
            map.loadImage(url, (err, image) => {
                if (err) return reject(err)
                // @ts-expect-error
                map.addImage(id, image)
                resolve(null)
            })
        })
    }

    function getMap (options: MapOptions): Promise<maplibregl.Map> {
        if (_map) return Promise.resolve(_map)

        // Any initial options we set here
        // This means the first view of the map is as good as we can make it

        const {
            center,
            zoom,
            markers,
            autofit,
            padding,
        } = options

        const initialOptions: maplibregl.MapOptions = {
            container: el,
            // style: `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_API_KEY}`,
            // My customized map
            style: `https://api.maptiler.com/maps/697dfe25-8087-42f1-a3f9-73983704eebf/style.json?key=${MAPTILER_API_KEY}`,
            attributionControl: false,
        }

        if (autofit && markers && markers.length > 0) {
            // Set an initial bounds, although no option to set the padding too
            initialOptions.bounds = getBounds(markers)
        } else if (center) {
            initialOptions.center = center
        } else {
            initialOptions.center = DEFAULT_CENTER
        }

        initialOptions.zoom = zoom ?? DEFAULT_ZOOM

        const map = new maplibregl.Map(initialOptions)

        // This padding stays with the map, then we can add additional padding later
        // when we use fitBounds
        map.setPadding({ top: BASE_PADDING, right: BASE_PADDING, bottom: BASE_PADDING, left: BASE_PADDING })

        _map = map

        return new Promise(resolve => {
            map.on('load', async () => {
                await Promise.all([
                    loadImage(map, 'pin', pin),
                    loadImage(map, 'circle', circle),
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
                        el.dispatchEvent(new CustomEvent("click-marker", {detail}))
                    } else {
                        const {lng, lat} = e.lngLat
                        const detail = {coordinates: [lng, lat]}
                        el.dispatchEvent(new CustomEvent("click-map", {detail}))
                    }
                })

                resolve(map)
            })
        })
    }

    effect(() => {
        optionsLater(async value => {
            const options = value as MapOptions
            const {
                center,
                zoom,
                markers,
                cursor,
                padding,
                autofit,
            } = options

            const map = await getMap(options)

            // Any options that might be reactive, we set here

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
            setMarkers(map, markers ?? [], { padding, autofit })
        })
    })

    function setMarkers(map: maplibregl.Map, markers: MapMarker[], options: { padding?: Padding, autofit?: boolean } = {}) {
        const source = map.getSource('markers') as GeoJSONSource | undefined
        if (!source) return
        const {
            autofit,
            padding,
        } = options
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
        if (autofit && markers.length > 0) {
            map.fitBounds(getBounds(markers), {
                padding,
                // Ensure we don't go too crazy zooming in close
                maxZoom: DEFAULT_ZOOM,
            })
        }

    }
})

function getBounds(markers: MapMarker[]): maplibregl.LngLatBounds {
    const firstLngLat = new maplibregl.LngLat(markers[0].coordinates[0], markers[0].coordinates[1])
    const bounds = new maplibregl.LngLatBounds(firstLngLat)
    for (const marker of markers) {
        bounds.extend(marker.coordinates)
    }
    return bounds
}