import Alpine from "alpinejs";

import maplibregl, {GeoJSONSource} from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

// *WARNING* this is a hacky "pre-release" version
// See the README.md I wrote at ./maplibre-gl-svg/README.md
import {SvgManager} from "./maplibre-gl-svg";

import { MAPTILER_STYLE_URL } from '../../settings.ts'
import { FilterControl, HomeControl } from "@/templates/ts/directives/map/controls.ts";
import {
    CurrentOptions,
    MapCoordinates,
    MapMarker,
    MapOptions,
    MarkerType,
    Padding
} from "@/templates/ts/directives/map/types.ts";
import {icons} from "@/templates/ts/directives/map/icons.ts";

const DEFAULT_CENTER: MapCoordinates = [-5.9213, 54.5996]
const DEFAULT_ZOOM = 12
const BASE_PADDING = 80 // always have at least this much padding


/**
 *  A directive to show a map. Usage:
 *
 *      <div x-map="{ markers: [] }"
 *           @click-marker="console.log('you clicked on marker', $event.detail)"
 *           @click-map="console.log('you clicked the map at coords', $event.detail)"
 *           @zoom-end="console.log('zoom is now', $event.detail)"></div>
 *
 *  See the MapOptions interface for what you can put in there
 */
Alpine.directive('map', (
    el,
    { expression },
    { cleanup, evaluateLater, effect },
) => {
    const optionsLater = evaluateLater(expression)

    // So we can refer to the options from anywhere...
    const current: CurrentOptions = { options: {} }


    let _map: maplibregl.Map
    cleanup(() => _map?.remove())

    function getMap (options: MapOptions): Promise<maplibregl.Map> {
        if (_map) return Promise.resolve(_map)

        // Any initial options we set here
        // This means the first view of the map is as good as we can make it

        const {
            home,
            center,
            zoom,
            markers,
            autofit,
        } = options

        function getStyleURL(): string {
            if (MAPTILER_STYLE_URL) {
                return MAPTILER_STYLE_URL
            } else {
                console.warn('USING MAPLIBRE DEMOTILES PLEASE SET MAPTILER_STYLE_URL / MAPTILER_API_KEY')
                // Just a basic view so *something* shows up...
                return "https://demotiles.maplibre.org/style.json"
            }
        }

        const initialOptions: maplibregl.MapOptions = {
            container: el,
            style: getStyleURL(),
            attributionControl: false,
        }

        if (autofit && markers && markers.length > 0) {
            // Set an initial bounds, although no option to set the padding too
            initialOptions.bounds = getBounds(markers)
        } else if (center) {
            initialOptions.center = center
        } else if (home) {
            initialOptions.center = home.center
            initialOptions.zoom = home.zoom
        } else {
            initialOptions.center = DEFAULT_CENTER
        }

        initialOptions.zoom = zoom ?? DEFAULT_ZOOM

        const map = new maplibregl.Map(initialOptions)

        const svgManager = new SvgManager(map)

        map.dragRotate.disable()
        map.touchZoomRotate.disable()
        map.addControl(
            new maplibregl.NavigationControl({ showCompass: false }),
            'top-right'
        )
        if (current.options.filterControl) {
            map.addControl(new FilterControl(), 'top-left')
        }

        if (current.options.home) {
            map.addControl(new HomeControl(current, DEFAULT_ZOOM), 'top-left')
        }

        // This padding stays with the map, then we can add additional padding later
        // when we use fitBounds
        map.setPadding({ top: BASE_PADDING, right: BASE_PADDING, bottom: BASE_PADDING, left: BASE_PADDING })

        _map = map

        return new Promise(resolve => {
            map.on('load', async () => {
                // These images map 1-to-1 with the marker "type" field

                const promises = []

                for (const name of Object.keys(icons)) {
                    const icon = icons[name as MarkerType]
                    promises.push(svgManager.add(name, icon.default))
                    if (icon.approximate) {
                        promises.push(svgManager.add(name + '--approximate', icon.approximate))
                    }
                }

                await Promise.all(promises)

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
                        // TODO: hmm, decide how to do the scaling here... also should only be for approximate ones
                        // it doesn't seem to scale the svgs very well :/
                        // 'icon-size': ['interpolate', ['linear'], ['zoom'], 15, 1, 22, 10],
                        // This means markers do not fade in
                        'icon-allow-overlap': true
                    }
                })

                map.on('zoomend', () => {
                    el.dispatchEvent(new CustomEvent("zoom-end", {detail: { zoom: map.getZoom() }}))
                })

                const initialCursor = map.getCanvas().style.cursor

                map.on('mousemove', 'markers', e => {
                    if (e.features) {
                        map.getCanvas().style.cursor = 'pointer'
                    }
                })

                map.on('mouseleave', 'markers', () => {
                    if (current.options.cursor) {
                        map.getCanvas().style.cursor = current.options.cursor
                    } else {
                        map.getCanvas().style.cursor = initialCursor
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
            current.options = options
            const {
                home,
                center,
                zoom,
                markers,
                types,
                cursor,
                padding,
                autofit,
            } = options

            function getMarkers(): MapMarker[] {
                if (!markers) return []
                if (!types || types.length === 0) return markers
                return markers.filter(marker => types.includes(marker.type))
            }

            const map = await getMap(options)

            // Any options that might be reactive, we set here

            if (cursor) {
                map.getCanvas().style.cursor = cursor
            }
            let mapCentre = center ?? home?.center

            // Only move if it actually changed
            if (mapCentre && (!current.mapCentre || mapCentre[0] !== current.mapCentre[0] || mapCentre[1] !== current.mapCentre[1])) {
                current.mapCentre = mapCentre
                const currentZoom = map.getZoom()
                map.flyTo({
                    center: mapCentre,
                    // in order:
                    // 1. specified zoom
                    // 2. current zoom if we're more zoomed in than default
                    // 3. default zoom
                    zoom: zoom ?? (DEFAULT_ZOOM > currentZoom ? DEFAULT_ZOOM : currentZoom),
                })
            }
            drawMarkers(map, getMarkers(), { padding, autofit })
        })
    })

    function getMarkerIcon (marker: MapMarker) {
        const icon = icons[marker.type]
        if (marker.approximate && icon.approximate) {
            return marker.type + '--approximate'
        }
        return marker.type
    }

    function drawMarkers(map: maplibregl.Map, markers: MapMarker[], options: { padding?: Padding, autofit?: boolean } = {}) {
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
                    type: marker.type,
                    icon: getMarkerIcon(marker),
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