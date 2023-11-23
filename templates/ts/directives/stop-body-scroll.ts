import Alpine from "alpinejs"
import { enableBodyScroll, stopBodyScroll } from "@/templates/ts/scroll.ts"

// If there are nested uses of this we need to only re-enable scroll when all
// of them are done with, so we use this to keep track of that
// TODO: this could alternatively be done in scroll.ts, and would then work for non-directive uses too
let count = 0

function inc() {
    if (count === 0) {
        // Going from 0 to >0, means we need to stop it
        stopBodyScroll()
    }
    count++
}

function dec() {
    count--
    if (count < 0) {
        count = 0
    }
    if (count === 0) {
        // Going from >0 to 0 means we need to re-enable it again
        enableBodyScroll()
    }
}

/**
 * A directive to stop body scroll while this element is present. When the element
 * is removed, scroll will be restored again.
 *
 * The purpose is for modal dialogs so the background does not scroll when the modal
 * is open.
 *
 * Usage:
 *
 *  <div x-stop-body-scroll></div>
 */
Alpine.directive('stop-body-scroll', (
    el,
    { },
    { cleanup },
) => {
    // This means we are not displayed on the page (e.g. a parent is display: none), so
    // it means it's likely being used via hiding/showing an element, not adding/removing
    // an element. This directive only supports the adding/removing element use case.
    // If used by hiding/showing the element, you have to manage the body scroll yourself
    // or use x-stop-body-scroll-if="condition"
    if (!el.offsetParent) return
    inc()
    cleanup(() => dec())
})

/**
 * A directive to stop body scroll while a condition is true.
 *
 * The purpose is for things like modals/menus/etc. that are shown/hidden, e.g. using x-show
 * rather than the element being present or not.
 *
 * Usage:
 *
 *  <div x-stop-body-scroll-if="open"></div>
 */
Alpine.directive('stop-body-scroll-if', (
    _,
    { expression },
    { evaluateLater, effect, cleanup },
) => {
    const getValue = evaluateLater(expression)
    let stop = false
    effect(() => {
        getValue(raw => {
            const value = Boolean(raw)
            if (value) {
                inc()
            } else {
                // Only act if we previously have stopped scroll with this element
                // (avoids calling dec() when first initialized)
                if (stop) dec()
            }
            stop = value
        })
    })
    cleanup(() => {
        if (stop) dec()
    })
})