import Konva from "konva"
import {
  RemixDrawAction,
  RemixScope,
} from "@/templates/ts/directives/remix/types.ts"

export interface RemixDraw {
  scope: RemixScope
  container: HTMLDivElement
}

export interface RemixDrawSceneEntry {
  colour: string
  width: number
  points: number[]
  action: RemixDrawAction
}

export interface RemixDrawScene {
  lines: RemixDrawSceneEntry[]
}

export function useDraw({ scope, container }: RemixDraw) {
  const sceneWidth = 1920
  const sceneHeight = 1080

  const lines: Konva.Line[] = []

  const stage = new Konva.Stage({
    container,
    width: sceneWidth,
    height: sceneHeight,
  })

  container.style.pointerEvents = "none"

  const layer = new Konva.Layer()
  stage.add(layer)

  let isDrawing = false
  let activeLine: Konva.Line

  stage.on("mousedown touchstart", () => {
    isDrawing = true

    const position = getPointerPosition(stage)

    activeLine = new Konva.Line({
      stroke: scope.draw.colour,
      strokeWidth: scope.draw.strokeWidth,
      globalCompositeOperation:
        scope.draw.action === "draw" ? "source-over" : "destination-out",
      // round cap for smoother lines
      lineCap: "round",
      lineJoin: "round",
      // add point twice, so we have some drawings even on a simple click
      points: [position.x, position.y, position.x, position.y],
    })
    layer.add(activeLine)
    lines.push(activeLine)
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
    const newPoints = activeLine.points().concat([position.x, position.y])
    activeLine.points(newPoints)
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

  function exportLine(line: Konva.Line): RemixDrawSceneEntry {
    return {
      colour: line.stroke(),
      width: line.strokeWidth(),
      points: line.points(),
      action:
        line.globalCompositeOperation() === "source-over" ? "draw" : "erase",
    }
  }

  function exportScene(): RemixDrawScene {
    return {
      lines: lines.map(exportLine),
    }
  }

  async function importScene(scene: RemixDrawScene) {
    for (const entry of scene.lines) {
      const line = new Konva.Line({
        stroke: entry.colour,
        strokeWidth: entry.width,
        globalCompositeOperation:
          entry.action === "draw" ? "source-over" : "destination-out",
        // round cap for smoother lines
        lineCap: "round",
        lineJoin: "round",
        // add point twice, so we have some drawings even on a simple click
        points: entry.points,
      })
      layer.add(line)
      lines.push(line)
    }
  }

  function clearScene() {
    lines.length = 0
    layer.destroyChildren()
  }

  function dispose() {
    deactivate()
    window.removeEventListener("resize", fitStageIntoParentContainer)
  }

  function getCanvas() {
    return container?.querySelector("canvas")
  }

  return {
    dispose,
    setEnabled,
    exportScene,
    importScene,
    clearScene,
    getCanvas,
  }
}

function getPointerPosition(stage: Konva.Stage): Konva.Vector2d {
  if (!stage) throw new Error("no stage!")
  const position = stage.getPointerPosition()
  if (!position) throw new Error("could not get position")
  const stageTransform = stage.getAbsoluteTransform().copy()
  return stageTransform.invert().point(position)
}

function useFitStageIntoParentContainer(
  stage: Konva.Stage,
  container: HTMLDivElement,
  sceneWidth: number,
  sceneHeight: number,
) {
  return () => {
    const containerWidth = container.offsetWidth
    const scale = containerWidth / sceneWidth
    stage.width(sceneWidth * scale)
    stage.height(sceneHeight * scale)
    stage.scale({ x: scale, y: scale })
  }
}
