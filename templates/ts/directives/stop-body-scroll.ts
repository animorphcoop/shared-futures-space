import Alpine from "alpinejs"
import { enableBodyScroll, stopBodyScroll } from "@/templates/ts/scroll.ts"

// If there are nested uses of this we need to only re-enable scroll when all
// of them are done with, so we use this to keep track of that
// TODO: this could alternatively be done in scroll.ts, and would then work for non-directive uses too
let count = 0

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
    // If used by hiding/showing the element, you have to manage the body scroll yourself...
    if (!el.offsetParent) return

    if (count === 0) {
        stopBodyScroll()
    }
    count += 1
    cleanup(() => {
        count -= 1
        if (count === 0) {
            enableBodyScroll()
        }
    })
})