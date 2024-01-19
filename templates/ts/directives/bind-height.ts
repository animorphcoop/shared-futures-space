import Alpine from "alpinejs";

/**
 * A directive you can use to bind a variable to an elements height, e.g.
 *
 *   <div x-data="{ height: 0 }">
 *       <div x-bind-height="height">
 *           some content
 *       </div>
 *   </div>
 *
 *   Here, "height" will always have the current height of the element.
 */
Alpine.directive('bind-height', (
    el,
    { expression }, { evaluate, cleanup },
) => {

    const observer = new ResizeObserver(entries => {
        for (const entry of entries) {
            evaluate(`${expression} = ${entry.contentRect.height}`)
        }
    })

    observer.observe(el)

    cleanup(() => observer.disconnect())
})