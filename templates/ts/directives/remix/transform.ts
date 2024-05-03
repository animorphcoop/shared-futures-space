import { Object3D, Camera, Intersection, Object3DEventMap } from "three"
import { Plane, Raycaster, Vector2, Vector3 } from "three"
import { findGroup } from "./utils.ts"
import { Property } from "csstype"
import {
  RemixBuildAction,
  RemixScope,
} from "@/templates/ts/directives/remix/types.ts"

function getCursor(mode: RemixBuildAction, hover: boolean): Property.Cursor {
  if (mode === "rotate") {
    return "ew-resize"
  } else if (mode === "scale") {
    return "row-resize"
  } else if (mode === "remove") {
    return "pointer"
  } else if (mode === "move") {
    return hover ? "grab" : "grabbing"
  }
  return "default"
}

export interface RemixTransform {
  scope: RemixScope
  objects: Object3D[]
  camera: Camera
  canvas: HTMLCanvasElement
  onSelect: (selected: Object3D[]) => void
  onRemove: (selected: Object3D[]) => void
}

/**
 * Handles the transformations in the three.js scene:
 * - moving
 * - rotating
 * - scaling
 * - removing
 *
 * Responsible for listening for the pointer events, and making the appropriate
 * transformations.
 */
export function useTransform({
  scope,
  objects,
  camera,
  canvas,
  onSelect,
  onRemove,
}: RemixTransform) {
  canvas.style.touchAction = "none" // disable touch scroll

  function setEnabled(enabled: boolean) {
    if (enabled) {
      activate()
    } else {
      onPointerCancel()
      deactivate()
    }
  }

  let originalAction: RemixBuildAction | null

  function setAction(value: RemixBuildAction) {
    scope.build.action = value
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

  const intersections: Intersection<Object3D<Object3DEventMap>>[] = []

  function activate() {
    canvas.addEventListener("pointermove", onPointerMove)
    canvas.addEventListener("pointerdown", onPointerDown)
    canvas.addEventListener("pointerup", onPointerCancel)
    canvas.addEventListener("pointerleave", onPointerCancel)
  }

  function deactivate() {
    canvas.removeEventListener("pointermove", onPointerMove)
    canvas.removeEventListener("pointerdown", onPointerDown)
    canvas.removeEventListener("pointerup", onPointerCancel)
    canvas.removeEventListener("pointerleave", onPointerCancel)
    canvas.style.cursor = ""
  }

  function dispose() {
    deactivate()
  }

  function updatePointer(event: PointerEvent) {
    const rect = canvas.getBoundingClientRect()
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    pointer.y = (-(event.clientY - rect.top) / rect.height) * 2 + 1
  }

  function onPointerDown(event: PointerEvent) {
    updatePointer(event)
    if (event.shiftKey) {
      originalAction = scope.build.action
      scope.build.action = "move"
    } else if (event.ctrlKey) {
      originalAction = scope.build.action
      scope.build.action = "rotate"
    } else if (event.altKey) {
      originalAction = scope.build.action
      scope.build.action = "scale"
    }
    intersections.length = 0
    raycaster.setFromCamera(pointer, camera)
    raycaster.intersectObjects(objects, recursive, intersections)
    if (intersections.length > 0) {
      selected = findGroup(intersections[0].object)
      if (selected) {
        canvas.style.cursor = getCursor(scope.build.action, false)
        if (scope.build.action === "move") {
          planeIntersect.copy(intersections[0].point)
          plane.setFromNormalAndCoplanarPoint(planeNormal, planeIntersect)
          shift.subVectors(selected.position, intersections[0].point)
        } else if (scope.build.action === "scale") {
          originalScale.copy(selected.scale)
        } else if (scope.build.action === "remove") {
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
      if (scope.build.action === "move") {
        if (raycaster.ray.intersectPlane(plane, intersection)) {
          raycaster.ray.intersectPlane(plane, planeIntersect)
          selected.position.addVectors(planeIntersect, shift)
        }
      } else if (scope.build.action === "rotate") {
        diff.subVectors(pointer, previousPointer).multiplyScalar(rotateSpeed)
        // "x" is horizontal mouse movement, which we turn into rotation on the "y" axis
        selected.rotation.y += diff.x
      } else if (scope.build.action === "scale") {
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
              canvas.style.cursor = "auto"
              hovered = null
            }
            if (hovered !== object) {
              canvas.style.cursor = getCursor(scope.build.action, true) // "grab"
              hovered = object
            }
          }
        } else if (hovered !== null) {
          canvas.style.cursor = "auto"
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
    if (originalAction) {
      scope.build.action = originalAction
      originalAction = null
    }
    if (selected) {
      selected = null
      onSelect([])
    }
    canvas.style.cursor = hovered ? getCursor(scope.build.action, true) : "auto"
    const select = hovered ?? selected
    if (select) {
      onSelect([select])
    } else {
      onSelect([])
    }
  }

  return {
    dispose,
    setAction,
    setEnabled,
  }
}
