import Alpine from "alpinejs";

import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import pin from './map_pin.png'
import circle from './map_circle.png'

interface MapOptions {
    apiKey: string
    markers: {
        name: string
        icon: 'pin' | 'circle'
        coordinates: [number, number]
    }[]
}

/**
 *  A directive to show a map. Usage:
 *
 *      <div x-map="{ markers: [] }"
 *           @click-marker="console.log('you clicked on marker', $event.detail)"
 *           @click-map="console.log('you clicked the map')"></div>
 *
 *  See the MapOptions interface for what you can put in there
 */
Alpine.directive('map', (
    el,
    { expression },
    { cleanup, evaluate },
) => {

    const options = evaluate(expression) as MapOptions
    console.log('map options!', options)
    const markers = options?.markers ?? []
    const apiKey = options?.apiKey

    const map = new maplibregl.Map({
        container: el,
        // style: `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_API_KEY}`,
        // My customized map
        style: `https://api.maptiler.com/maps/697dfe25-8087-42f1-a3f9-73983704eebf/style.json?key=${apiKey}`,
        center: [-5.9213, 54.5996],
        zoom: 15,
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
            }
        });

        map.addLayer({
            'id': 'markers',
            'type': 'symbol',
            'source': 'markers',
            'layout': {
                'icon-image': ["get", "icon"],
                'icon-size': 1
            }
        });

        map.on('click', e => {
            const feature = map.queryRenderedFeatures(e.point, {
                layers: ['markers'],
            })?.[0]
            if (feature) {
                const marker = JSON.parse(feature.properties.marker)
                el.dispatchEvent(new CustomEvent("click-marker", { detail: marker }))
            }
            else {
                el.dispatchEvent(new CustomEvent("click-map"))
            }
        })
    })

    cleanup(() => map.remove())
})