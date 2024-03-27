import CSS from "csstype";
import { PaddingOptions, RequireAtLeastOne } from "maplibre-gl";

export type MapCoordinates = [number, number] // longitude, latitude

export type MarkerType = 'river' | 'river-finished' | 'resource' | 'idea'

export interface MapMarker {
    name: string
    type: MarkerType
    coordinates: MapCoordinates
    approximate?: boolean
}

export type Padding = RequireAtLeastOne<PaddingOptions>

export interface MapOptions {
    types?: MarkerType[]
    home?: {
        center: MapCoordinates
        zoom: number
    }
    markers?: MapMarker[]
    center?: MapCoordinates
    zoom?: number
    cursor?: CSS.Properties['cursor']
    padding?: Padding
    autofit?: boolean
    filterControl?: boolean
    // Enable zooming when you scroll
    // Is annoying on content/landing-type pages
    // But useful in more focused places
    scrollZoom?: boolean
}

export interface CurrentOptions {
    options: MapOptions
    mapCentre?: MapCoordinates
}