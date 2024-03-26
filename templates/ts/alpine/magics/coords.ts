

import Alpine from 'alpinejs'
import {MapCoordinates} from "@/templates/ts/directives/map/types.ts"

const POINT_RE = /POINT\s*\(\s*([0-9.-]+)\s*([0-9.-]+)\s*\)/

/**
 * An alpine "magic" function.
 *
 * Converts from point to co-ords.
 *
 * e.g.
 *  from: "SRID=4326;POINT (-5.904734677122434 54.5993016753645)"
 *  to: [ -5.906794613646412, 54.59393145818788 ]
 */
Alpine.magic('pointToCoords', () => {
    return (point?: string): MapCoordinates | null => {
        if (!point) return null
        const m = POINT_RE.exec(point)
        if (m) return [parseFloat(m[1]), parseFloat(m[2])]
        return null
    }
})

/**
 *  ... and the other way around
 */
Alpine.magic('coordsToPoint', () => {
    return (coords?: MapCoordinates): string => {
        if (!coords) return ''
        return `SRID=4326;POINT (${coords.join(' ')})`
    }
})