import Konva from "konva"
import { RemixScope } from "@/templates/ts/directives/remix/remix.ts"
import {
  getPointerPosition,
  useFitStageIntoParentContainer,
} from "@/templates/ts/directives/remix/konva-utils.ts"

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

  stage.on("mousedown touchstart", () => {
    isDrawing = true

    const position = getPointerPosition(stage)

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

    const position = getPointerPosition(stage)
    const newPoints = lastLine.points().concat([position.x, position.y])
    lastLine.points(newPoints)
  })

  const fitStageIntoParentContainer = useFitStageIntoParentContainer(
    stage,
    container,
    sceneWidth,
    sceneHeight,
  )
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
  }

  function deactivate() {
    container.style.pointerEvents = "none"
    container.style.cursor = ""
  }

  function dispose() {
    deactivate()
    window.removeEventListener("resize", fitStageIntoParentContainer)
  }

  return {
    dispose,
    setEnabled,
  }
}
