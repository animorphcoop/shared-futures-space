import Alpine from "alpinejs";

import maplibregl, {GeoJSONSource} from 'maplibre-gl'
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

interface MapOptions {
    markers?: MapMarker[]
    center?: MapCoordinates
    zoom?: number
    cursor?: string // css cursor value, e.g. pointer
}

const DEFAULT_CENTER: MapCoordinates = [-5.9213, 54.5996]
const DEFAULT_ZOOM = 15

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
                console.log('setting options', options)
                const {
                    center,
                    zoom,
                    markers,
                    cursor,
                } = options
                if (cursor) {
                    map.getCanvas().style.cursor = cursor
                }
                if (center) {
                    // map.setCenter(center)
                    map.flyTo({
                        center: center,
                        zoom: zoom ?? DEFAULT_ZOOM,
                    })
                }
                if (markers) {
                    setMarkers(markers)
                }
            })
        })
    })

    function setMarkers(markers: MapMarker[]) {
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
    }

    cleanup(() => map.remove())
})