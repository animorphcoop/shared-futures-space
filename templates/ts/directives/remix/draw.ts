import Konva from "konva"
import { RemixScope } from "@/templates/ts/directives/remix/remix.ts"

export interface RemixDraw {
  scope: RemixScope
  container: HTMLDivElement
}

export function useDraw({ scope, container }: RemixDraw) {
  const sceneWidth = 1920
  const sceneHeight = 1080

  const stage = new Konva.Stage({
    container,
    width: sceneWidth,
    height: sceneHeight,
  })

  container.style.pointerEvents = "none"

  const layer = new Konva.Layer()
  stage.add(layer)

  let isDrawing = false
  let drawMode = "brush"
  let lastLine: Konva.Line

  function getPointerPosition(): Konva.Vector2d | null {
    const position = stage.getPointerPosition()
    if (!position) return null
    const stageTransform = stage.getAbsoluteTransform().copy()
    return stageTransform.invert().point(position)
  }

  stage.on("mousedown touchstart", () => {
    isDrawing = true

    const position = getPointerPosition()
    if (!position) return

    lastLine = new Konva.Line({
      stroke: scope.draw.colour,
      strokeWidth: scope.draw.strokeWidth,
      globalCompositeOperation:
        drawMode === "brush" ? "source-over" : "destination-out",
      // round cap for smoother lines
      lineCap: "round",
      lineJoin: "round",
      // add point twice, so we have some drawings even on a simple click
      points: [position.x, position.y, position.x, position.y],
    })
    layer.add(lastLine)
  })

  stage.on("mouseup touchend", () => {
    isDrawing = false
  })

  // and core function - drawing
  stage.on("mousemove touchmove", (e) => {
    if (!isDrawing) {
      return
    }

    // prevent scrolling on touch devices
    e.evt.preventDefault()

    const position = getPointerPosition()
    if (!position) return
    const newPoints = lastLine.points().concat([position.x, position.y])
    lastLine.points(newPoints)
  })

  function fitStageIntoParentContainer() {
    const containerWidth = container.offsetWidth
    const scale = containerWidth / sceneWidth
    stage.width(sceneWidth * scale)
    stage.height(sceneHeight * scale)
    stage.scale({ x: scale, y: scale })
  }

  fitStageIntoParentContainer()

  window.addEventListener("resize", fitStageIntoParentContainer)

  function setEnabled(enabled: boolean) {
    if (enabled) {
      activate()
    } else {
      deactivate()
    }
  }
  function activate() {
    container.style.pointerEvents = ""
    container.addEventListener("pointermove", onPointerMove)
    container.addEventListener("pointerdown", onPointerDown)
    container.addEventListener("pointerleave", onPointerCancel)
    container.addEventListener("pointerup", onPointerCancel)
  }

  function deactivate() {
    container.style.pointerEvents = "none"

    container.removeEventListener("pointermove", onPointerMove)
    container.removeEventListener("pointerdown", onPointerDown)
    container.removeEventListener("pointerup", onPointerCancel)
    container.removeEventListener("pointerleave", onPointerCancel)
    container.style.cursor = ""
  }

  function onPointerMove(event: PointerEvent) {}

  function onPointerDown(event: PointerEvent) {}

  function onPointerCancel(event: PointerEvent) {}

  function dispose() {
    deactivate()
    window.removeEventListener("resize", fitStageIntoParentContainer)
  }

  return {
    dispose,
    setEnabled,
  }
}
