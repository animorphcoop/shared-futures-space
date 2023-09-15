/**
 * Use to expose things globally
 *
 * e.g. expose({ blah: 'some text' })
 *
 * Will then be available globally as "blah"
 *
 * @param obj - an object of what you want to expose
 */
export function expose(obj: object) {
    Object.assign(window, obj)
}
