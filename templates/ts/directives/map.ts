import Alpine from "alpinejs";

import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import pin from './map_pin.png'
import circle from './map_circle.png'

const MAPTILER_API_KEY = ""

Alpine.directive('map', (
    el,
    { },
    { cleanup },
) => {
    const map = new maplibregl.Map({
        container: el,
        // style: `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_API_KEY}`,
        // My customized map
        style: `https://api.maptiler.com/maps/697dfe25-8087-42f1-a3f9-73983704eebf/style.json?key=${MAPTILER_API_KEY}`,
        center: [-5.9213, 54.5996],
        zoom: 15,
        attributionControl: false,
    })

    const places = [
        {
            name: 'Foo',
            icon: 'pin',
            coordinates: [-5.9273, 54.5993],
        },
        {
            name: 'Bar',
            icon: 'pin',
            coordinates: [-5.9236, 54.6009]
        },
        {
            name: 'Baz',
            icon: 'circle',
            coordinates: [-5.9146, 54.6033],
        },
        {
            name: 'Bin',
            icon: 'circle',
            coordinates: [-5.9202, 54.5967],
        },
    ]

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

        map.addSource('places', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: places.map(place => ({
                    type: 'Feature',
                    properties: {
                        ...place,
                        icon: place.icon ?? 'pin',
                    },
                    geometry: {
                        type: 'Point',
                        coordinates: place.coordinates,
                    }
                }))
            }
        });

        map.addLayer({
            'id': 'places',
            'type': 'symbol',
            'source': 'places',
            'layout': {
                'icon-image': ["get", "icon"],
                'icon-size': 1
            }
        });

        map.on('click', e => {
            const feature = map.queryRenderedFeatures(e.point, {
                layers: ['places'],
            })?.[0]
            if (feature) {
                el.dispatchEvent(new CustomEvent("marker-click", { detail: feature.properties }))
            }
            else {
                el.dispatchEvent(new CustomEvent("map-click"))
            }
        })
    })

    cleanup(() => map.remove())
})