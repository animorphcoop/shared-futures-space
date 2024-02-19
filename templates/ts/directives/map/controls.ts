import maplibregl, {IControl} from "maplibre-gl";
import homeSVG from "@/templates/ts/directives/map/home.svg";

export class FilterControl implements IControl {
    el?: HTMLDivElement

    onAdd(map: maplibregl.Map) {
        const div = document.createElement('div')
        div.classList.add('maplibregl-ctrl')
        const button = document.createElement('button')
        button.classList.add('button', 'button-on-colour')
        button.textContent = 'Filter'
        button.addEventListener('click', () => {
            map.getContainer().dispatchEvent(new CustomEvent('click-filter'))
        })
        div.appendChild(button)
        this.el = div
        return this.el
    }

    onRemove() {
        this.el?.remove()
    }
}

export class HomeControl implements IControl {
    current: CurrentOptions
    defaultZoom: number
    el?: HTMLDivElement

    constructor(current: CurrentOptions, defaultZoom: number) {
        this.current = current
        this.defaultZoom = defaultZoom
    }

    onAdd(map: maplibregl.Map) {
        const div = document.createElement('div')
        div.classList.add('maplibregl-ctrl')

        const button = document.createElement('button')
        button.classList.add('button', 'button-on-colour')

        button.addEventListener('click', () => {
            map.flyTo({
                center: this.current.options.home,
                zoom: this.defaultZoom
            })
        })

        const icon = document.createElement('img')
        icon.src = homeSVG

        button.appendChild(icon)
        div.appendChild(button)

        this.el = div
        return this.el
    }

    onRemove() {
        this.el?.remove()
    }
}