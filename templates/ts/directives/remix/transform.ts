import {Object3D, Camera, Intersection, Object3DEventMap} from "three"
import { Plane, Raycaster, Vector2, Vector3 } from "three"
import { findGroup } from "./utils.ts"
import {RemixTransformMode} from "@/templates/ts/directives/remix/remix.ts"
import {Property} from "csstype"

function cursorForMode(mode: RemixTransformMode, hover: boolean): Property.Cursor {
    if (mode === 'rotate') {
        return 'ew-resize'
    } else if (mode === 'scale') {
        return 'row-resize'
    } else if (mode === 'remove') {
        return 'pointer'
    } else if (mode === 'move') {
        return hover ? 'grab' : 'grabbing'
    }
    return 'default'
}

export function useTransform({
    objects,
    camera,
    domElement,
    onSelect,
    onRemove,
}: {
    objects: Object3D[]
    camera: Camera
    domElement: HTMLCanvasElement
    onSelect: (selected: Object3D[]) => void
    onRemove: (selected: Object3D[]) => void
}) {
    domElement.style.touchAction = "none" // disable touch scroll

    let mode: RemixTransformMode = "move"
    let originalMode: RemixTransformMode | null

    function setMode(newMode: RemixTransformMode) {
        mode = newMode
    }

    const rotateSpeed = 6

    const plane = new Plane()
    const raycaster = new Raycaster()
    // Make the raycaster a bit "fuzzier"
    // https://threejs.org/docs/#api/en/core/Raycaster.params
    // TODO: hmm doesn't actually seem to work...
    // This example seems to do it though:
    // https://threejs.org/examples/?q=raycas#webgl_interactive_lines
    raycaster.params.Line.threshold = 100
    raycaster.params.Points.threshold = 100

    const pointer = new Vector2()
    const diff = new Vector2()
    const intersection = new Vector3()

    const shift = new Vector3()
    const planeNormal = new Vector3(0, 1, 0)
    const planeIntersect = new Vector3()

    const previousPointer = new Vector2()
    const originalPointer = new Vector2()
    const originalScale = new Vector3()

    const recursive = true
    let selected: Object3D | null = null
    let hovered: Object3D | null = null

    const intersections: Intersection<
        Object3D<Object3DEventMap>
    >[] = []

    function activate() {
        domElement.addEventListener("pointermove", onPointerMove)
        domElement.addEventListener("pointerdown", onPointerDown)
        domElement.addEventListener("pointerup", onPointerCancel)
        domElement.addEventListener("pointerleave", onPointerCancel)
    }

    function deactivate() {
        domElement.removeEventListener("pointermove", onPointerMove)
        domElement.removeEventListener("pointerdown", onPointerDown)
        domElement.removeEventListener("pointerup", onPointerCancel)
        domElement.removeEventListener("pointerleave", onPointerCancel)
        domElement.style.cursor = ""
    }

    function dispose() {
        deactivate()
    }

    function updatePointer(event: PointerEvent) {
        const rect = domElement.getBoundingClientRect()
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
        pointer.y = (-(event.clientY - rect.top) / rect.height) * 2 + 1
    }

    function onPointerDown(event: PointerEvent) {
        updatePointer(event)
        if (event.shiftKey) {
            originalMode = mode
            mode = "move"
        } else if (event.ctrlKey) {
            originalMode = mode
            mode = "rotate"
        } else if (event.altKey) {
            originalMode = mode
            mode = "scale"
        }
        // if (event.shiftKey) {
        //     mode = "rotate"
        // } else if (event.ctrlKey) {
        //     mode = "scale"
        // } else {
        //     mode = "move"
        // }
        intersections.length = 0
        raycaster.setFromCamera(pointer, camera)
        raycaster.intersectObjects(objects, recursive, intersections)
        if (intersections.length > 0) {
            selected = findGroup(intersections[0].object)
            if (selected) {
                domElement.style.cursor = cursorForMode(mode, false)
                if (mode === "move") {
                    planeIntersect.copy(intersections[0].point)
                    plane.setFromNormalAndCoplanarPoint(planeNormal, planeIntersect)
                    shift.subVectors(
                        selected.position,
                        intersections[0].point,
                    )
                } else if (mode === "scale") {
                    originalScale.copy(selected.scale)
                } else if (mode === 'remove') {
                    onRemove([selected])
                }
            }
        }
        originalPointer.copy(pointer)
        previousPointer.copy(pointer)
    }

    function onPointerMove(event: PointerEvent) {
        updatePointer(event)
        raycaster.setFromCamera(pointer, camera)

        if (selected) {
            // transform selected
            if (mode === "move") {
                if (raycaster.ray.intersectPlane(plane, intersection)) {
                    raycaster.ray.intersectPlane(plane, planeIntersect)
                    selected.position.addVectors(planeIntersect, shift)
                }
            } else if (mode === "rotate") {
                diff.subVectors(pointer, previousPointer).multiplyScalar(rotateSpeed)
                // "x" is horizontal mouse movement, which we turn into rotation on the "y" axis
                selected.rotation.y += diff.x
            } else if (mode === "scale") {
                diff.subVectors(pointer, originalPointer)
                selected.scale.copy(originalScale).multiplyScalar(diff.y + 1)
            }

            previousPointer.copy(pointer)
        } else {
            // hover
            if (event.pointerType === "mouse" || event.pointerType === "pen") {
                intersections.length = 0

                raycaster.setFromCamera(pointer, camera)
                raycaster.intersectObjects(objects, recursive, intersections)

                if (intersections.length > 0) {
                    const object = findGroup(intersections[0].object)
                    if (object) {
                        if (hovered !== object && hovered !== null) {
                            domElement.style.cursor = "auto"
                            hovered = null
                        }
                        if (hovered !== object) {
                            domElement.style.cursor = cursorForMode(mode, true) // "grab"
                            hovered = object
                        }
                    }
                } else if (hovered !== null) {
                    domElement.style.cursor = "auto"
                    hovered = null
                }
            }
        }

        const select = hovered ?? selected
        if (select) {
            onSelect([select])
        } else {
            onSelect([])
        }

        previousPointer.copy(pointer)
    }

    function onPointerCancel() {
        if (originalMode) {
            mode = originalMode
            originalMode = null
        }
        if (selected) {
            selected = null
            onSelect([])
        }
        domElement.style.cursor = hovered ? cursorForMode(mode, true) : "auto"
        const select = hovered ?? selected
        if (select) {
            onSelect([select])
        } else {
            onSelect([])
        }
    }

    activate()

    return {
        dispose,
        setMode,
    }
}
