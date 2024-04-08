import {Object3D, Camera, Intersection, Object3DEventMap} from "three"
import { Plane, Raycaster, Vector2, Vector3 } from "three"
import { findGroup } from "./utils.ts"

export function useTransform({
    objects,
    camera,
    domElement,
    onSelect,
}: {
    objects: Object3D[]
    camera: Camera
    domElement: HTMLCanvasElement
    onSelect: (selected: Object3D[]) => void
}) {
    domElement.style.touchAction = "none" // disable touch scroll

    let mode: "translate" | "rotate" | "scale" = "translate"
    const rotateSpeed = 6
    // const scaleSpeed = 40

    const plane = new Plane()
    const raycaster = new Raycaster()
    // Make the raycaster a bit "fuzzier"
    // https://threejs.org/docs/#api/en/core/Raycaster.params
    // TODO: hmm doesn't actually seem to work...
    // This example seems to do it though:
    // https://threejs.org/examples/?q=raycas#webgl_interactive_lines
    raycaster.params.Line.threshold = 100
    raycaster.params.Points.threshold = 100

    // This one looks interesting for removing things
    // https://threejs.org/examples/?q=rthraycas#webgl_interactive_voxelpainter

    const pointer = new Vector2()
    const previousPointer = new Vector2()
    // const offset = new Vector3()
    const diff = new Vector2()
    const intersection = new Vector3()
    const worldPosition = new Vector3()
    // const inverseMatrix = new Matrix4()

    // New things
    // const planeNormal = new Vector3(0, 1, 0) // plane's normal
    // const mouse = new Vector2()
    const shift = new Vector3() // distance between position of an object and points of intersection with the object
    const pNormal = new Vector3(0, 1, 0) // plane's normal
    const planeIntersect = new Vector3() // point of intersection with the plane
    const pIntersect = new Vector3() // point of intersection with an object (plane's point)

    const originalPointer = new Vector2()
    const originalScale = new Vector3()
    // const scaleTmp = new Vector3()
    // const removeZ = new Vector3()

    /*
    const worldPositionStart = new Vector3()
    const worldQuaternionStart = new Quaternion()
    const worldScaleStart = new Vector3()
    const pointStart = new Vector3()
    const pointEnd = new Vector3()

     */

    const up = new Vector3()
    const right = new Vector3()

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
            mode = "rotate"
        } else if (event.ctrlKey) {
            mode = "scale"
        } else {
            mode = "translate"
        }
        intersections.length = 0
        raycaster.setFromCamera(pointer, camera)
        raycaster.intersectObjects(objects, recursive, intersections)
        if (intersections.length > 0) {
            selected = findGroup(intersections[0].object)

            if (selected) {
                domElement.style.cursor = "grabbing"
                pIntersect.copy(intersections[0].point)
                plane.setFromNormalAndCoplanarPoint(pNormal, pIntersect)
                shift.subVectors(
                    selected.position,
                    intersections[0].point,
                )

                if (raycaster.ray.intersectPlane(plane, intersection)) {
                    if (mode === "translate") {
                    } else if (mode === "rotate") {
                        // the controls only support Y+ up
                        up.set(0, 1, 0).applyQuaternion(camera.quaternion).normalize()
                        right.set(1, 0, 0).applyQuaternion(camera.quaternion).normalize()
                    } else if (mode === "scale") {
                        originalPointer.copy(pointer)
                        originalScale.copy(selected.scale)
                    }
                }
            }
        }
        previousPointer.copy(pointer)
    }

    function onPointerMove(event: PointerEvent) {
        updatePointer(event)
        raycaster.setFromCamera(pointer, camera)

        if (selected) {
            if (mode === "translate") {
                if (raycaster.ray.intersectPlane(plane, intersection)) {
                    // selected.position.copy(
                    //   intersection.sub(offset).applyMatrix4(inverseMatrix),
                    // )
                    // selected.position.addVectors(intersection, shift)
                    // console.log("selected position", selected.position)

                    raycaster.ray.intersectPlane(plane, planeIntersect)
                    selected.position.addVectors(planeIntersect, shift)
                }

                // raycaster.ray.intersectPlane(plane, planeIntersect)
                // dragObject.position.addVectors(planeIntersect, shift)
            } else if (mode === "rotate") {
                diff.subVectors(pointer, previousPointer).multiplyScalar(rotateSpeed)
                // both world, goes wierd!
                // selected.rotateOnWorldAxis(up, diff.x)
                // selected.rotateOnWorldAxis(right.normalize(), -diff.y)

                // both local, goes wierd!
                // selected.rotateY(diff.x)
                // selected.rotateX(-diff.y)

                // moving cursor left or right to always rotate object
                // on it's local y axis
                // selected.rotateY(diff.x)
                // // whereas moving cursor up and down rotates relative to world
                // selected.rotateOnWorldAxis(right.normalize(), -diff.y)

                // Or much simpler! Just modify the rotation values :)
                selected.rotation.y += diff.x
                // selected.rotation.x -= diff.y
            } else if (mode === "scale") {
                diff.subVectors(pointer, originalPointer)
                selected.scale.copy(originalScale).multiplyScalar(diff.y + 1)
            }

            // dispatchEvent({ type: "drag", object: selected })

            previousPointer.copy(pointer)
        } else {
            // hover support

            if (event.pointerType === "mouse" || event.pointerType === "pen") {
                intersections.length = 0

                raycaster.setFromCamera(pointer, camera)
                raycaster.intersectObjects(objects, recursive, intersections)

                if (intersections.length > 0) {
                    const object = findGroup(intersections[0].object)
                    if (object) {
                        plane.setFromNormalAndCoplanarPoint(
                            camera.getWorldDirection(plane.normal),
                            worldPosition.setFromMatrixPosition(object.matrixWorld),
                        )

                        if (hovered !== object && hovered !== null) {
                            // scope.dispatchEvent({ type: "hoveroff", object: hovered })

                            domElement.style.cursor = "auto"
                            hovered = null
                        }

                        if (hovered !== object) {
                            // scope.dispatchEvent({ type: "hoveron", object: object })

                            domElement.style.cursor = "grab"
                            hovered = object
                        }
                    }
                } else {
                    if (hovered !== null) {
                        // scope.dispatchEvent({ type: "hoveroff", object: _hovered })

                        domElement.style.cursor = "auto"
                        hovered = null
                    }
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
        if (selected) {
            selected = null
            onSelect([])
        }
        domElement.style.cursor = hovered ? "grab" : "auto"
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
    }
}
