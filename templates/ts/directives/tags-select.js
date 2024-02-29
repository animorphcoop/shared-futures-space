"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var alpinejs_1 = require("alpinejs");
/**
 *  A directive to handle the tag selecting logic
 *
 *  The value of the attribute should be the field name, e.g.:
 *
 *     <div x-tags-select="my-tag-field">
 *
 *  We use that to find the right label to update...
 */
alpinejs_1.default.directive('tags-select', function (el, _a) {
    var expression = _a.expression;
    var maxTagCount = 3;
    var fieldName = expression;
    var fieldId = "id_".concat(fieldName);
    // Label subtext is an *optional* field that let's us add extra info next to the form label
    var labelSubtextEl = document.querySelector("[for=\"".concat(fieldId, "\"] .label__subtext"));
    // The input is our hidden input to hold the value
    var inputEl = el.querySelector('input');
    if (!inputEl)
        return; // no input, bail out...
    // Start with existing tags set
    var selectedTags = new Set(parseTags(inputEl.value));
    // Ensure we set the initial value
    updateLabelSubtext();
    /**
     *
     * Find our tags and set them up!
     *
     * Tags are identified in the DOM by having the data-tag attribute, e.g.:
     *
     *      <button data-tag="co-ops">Co-operatives</button>
     *
     *  If it gets selected we'll add "data-selected", e.g.
     *
     *     <button data-tag="co-ops" data-selected>Co-operatives</button>
     *
     *  You can use this to set tailwind classes in the template, e.g.:
     *
     *     <button data-tag="co-ops" class="data-[selected]:bg-green-pale">Co-operatives</button>
     */
    el.querySelectorAll('[data-tag]').forEach(function (tagEl) {
        if (!(tagEl instanceof HTMLElement))
            return;
        var tagValue = tagEl.dataset.tag;
        if (!tagValue)
            return;
        // Set initial selected value
        if (selectedTags.has(tagValue)) {
            tagEl.dataset.selected = 'selected';
        }
        else {
            delete tagEl.dataset.selected;
        }
        tagEl.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            if (selectedTags.has(tagValue)) {
                delete tagEl.dataset.selected;
                selectedTags.delete(tagValue);
            }
            else if (selectedTags.size < maxTagCount) {
                tagEl.dataset.selected = 'selected';
                selectedTags.add(tagValue);
            }
            updateLabelSubtext();
            updateInputValue();
        });
    });
    function updateLabelSubtext() {
        if (!labelSubtextEl)
            return;
        var remaining = maxTagCount - selectedTags.size;
        labelSubtextEl.innerHTML = remaining > 0 ? "choose ".concat(remaining) : '';
    }
    function updateInputValue() {
        if (!inputEl)
            return;
        inputEl.value = formatTags(Array.from(selectedTags));
    }
});
// These parse/formatting utilities work in tandem with the formatting django-taggit uses
// It's basically comma separated double-quoted values, with optional trailing comma.
// See https://github.com/jazzband/django-taggit/blob/master/taggit/utils.py
// e.g. `"tag one", "tag two", `
function formatTags(tagValues) {
    return tagValues.map(function (tagValue) { return JSON.stringify(tagValue); }).join(', ');
}
function parseTags(value) {
    if (!value)
        return [];
    value = value.trim();
    if (value.endsWith(',')) {
        value = value.substring(0, value.length - 1);
    }
    return JSON.parse("[".concat(value, "]"));
}
