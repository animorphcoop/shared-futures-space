import {Object3D} from "three"

export function findGroup(
    obj: Object3D,
    group: Object3D | null = null,
) {
    // @ts-expect-error
    if (obj.isGroup) group = obj
    if (obj.parent === null) return group
    return findGroup(obj.parent, group)
}

