import {Object3D, Vector2} from "three";

export function findGroup(
    obj: Object3D,
    group: Object3D | null = null,
) {
    // @ts-expect-error
    if (obj.isGroup) group = obj
    if (obj.parent === null) return group
    return findGroup(obj.parent, group)
}

export function updatePointer(
    domElement: Element,
    event: PointerEvent,
    pointer: Vector2,
) {
    const rect = domElement.getBoundingClientRect()
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    pointer.y = (-(event.clientY - rect.top) / rect.height) * 2 + 1
}
