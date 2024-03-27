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
    // Zooming on scroll can be annoying on more
    // content-like pages
    disableScrollZoom?: boolean
}

export interface CurrentOptions {
    options: MapOptions
    mapCentre?: MapCoordinates
}