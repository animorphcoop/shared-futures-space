/*
 We would just import 'htmx.org/dist/ext/alpine-morph.js'

 BUT that uses global "htmx" which isn't available in module land.

 So this is just copied in from htmx.org/dist/ext/alpine-morph.js
 and then htmx/Alpine imports added.

 There may be another way to do it...
*/

import htmx from "htmx.org"
import Alpine from "alpinejs"

htmx.defineExtension('alpine-morph', {
    isInlineSwap: function (swapStyle) {
        return swapStyle === 'morph';
    },
    handleSwap: function (swapStyle, target, fragment) {
        if (swapStyle === 'morph') {
            if (fragment.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {
                Alpine.morph(target, fragment.firstElementChild, {});
                return [target];
            } else {
                Alpine.morph(target, fragment.outerHTML, {});
                return [target];
            }
        }
    }
});