import markerRiverFinishedSVG from '@/templates/ts/directives/map/icons/river-finished.svg'
import markerResourceSVG from '@/templates/ts/directives/map/icons/resource.svg'
import markerResourceApproximateSVG from '@/templates/ts/directives/map/icons/resource--approximate.svg'
import markerIdeaSVG from '@/templates/ts/directives/map/icons/idea.svg'
import markerRiverSVG from '@/templates/ts/directives/map/icons/river.svg'
import markerRiverApproximateSVG from '@/templates/ts/directives/map/icons/river--approximate.svg'
import {MarkerType} from "@/templates/ts/directives/map/types.ts";

type Icons = {
    [key in MarkerType]: {
        default: string,
        approximate?: string
    }
}

export const icons: Icons = {
    river: {
        default: markerRiverSVG,
        approximate: markerRiverApproximateSVG,
    },
    'river-finished': {
      default: markerRiverFinishedSVG,
    },
    resource: {
        default: markerResourceSVG,
        approximate: markerResourceApproximateSVG,
    },
    idea: {
        default: markerIdeaSVG,
    },
}