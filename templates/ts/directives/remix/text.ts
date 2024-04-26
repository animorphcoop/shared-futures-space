import { Canvas, ITextProps, Textbox } from "fabric"
import {
  RemixScope,
  RemixTextScene,
  RemixTextSceneEntry,
} from "@/templates/ts/directives/remix/types.ts"

export interface RemixTextFabric {
  scope: RemixScope
  container: HTMLDivElement
}

export function useText({ scope, container }: RemixTextFabric) {
  const canvasEl: HTMLCanvasElement = document.createElement("canvas")
  container.appendChild(canvasEl)
  const defaultWidth = 280

  const canvas = new Canvas(canvasEl)

  const textboxes: Textbox[] = []

  function add(value: string = "") {
    const textbox = createTextbox(value, {
      top: sceneHeight / 2,
      left: sceneWidth / 2,
    })
    canvas.setActiveObject(textbox)
    textbox.enterEditing()
  }

  canvas.on("mouse:down", (event) => {
    if (
      scope.text.action === "remove" &&
      event.target &&
      event.target instanceof Textbox
    ) {
      const idx = textboxes.indexOf(event.target)
      if (idx !== -1) {
        textboxes.splice(idx, 1)
      }
      canvas.remove(event.target)
      updateObjectCount()
    }
  })

  canvas.on("mouse:dblclick", (event) => {
    if (!event.target) {
      // Add a new textbox!
      const position = event.scenePoint
      const textbox = createTextbox("", {
        top: position.y,
        left: position.x,
      })
      canvas.setActiveObject(textbox)
      textbox.enterEditing()
    }
  })

  const sceneWidth = 1920
  const sceneHeight = 1080

  const scale = container.clientWidth / sceneWidth

  canvas.setDimensions({
    width: sceneWidth * scale,
    height: sceneHeight * scale,
  })
  canvas.setZoom(scale)

  function createTextbox(value: string, options: Partial<ITextProps>) {
    // Defaults
    const text = new Textbox(value, {
      originX: "center",
      width: defaultWidth,
      fontSize: 40,
      textAlign: "center",
      cornerColor: "rgb(151, 89, 255)",
      borderColor: "rgb(151, 89, 255)",
      backgroundColor: "#FAFFC6",
      fontFamily: "sans",
      ...options,
    })
    text.setControlsVisibility({
      mt: false,
      mb: false,
    })

    canvas.add(text)
    textboxes.push(text)
    updateObjectCount()
    scope.text.action = "move"
    return text
  }

  function fitStageIntoParentContainer() {
    const scaleRatio = container.clientWidth / sceneWidth

    const newWidth = canvas.getWidth() * scaleRatio

    canvas.setDimensions({
      width: newWidth,
      height: newWidth / (16 / 9),
    })

    const containerWidth = container.offsetWidth
    const scale = containerWidth / sceneWidth

    canvas.setDimensions({
      width: sceneWidth * scale,
      height: sceneHeight * scale,
    })
    canvas.setZoom(scale)
  }

  window.addEventListener("resize", fitStageIntoParentContainer)

  function activate() {
    container.style.pointerEvents = ""
  }

  function deactivate() {
    container.style.pointerEvents = "none"
    container.style.cursor = ""
    canvas.discardActiveObject()
    canvas.renderAll()
  }

  function dispose() {
    deactivate()
    window.removeEventListener("resize", fitStageIntoParentContainer)
    container.removeChild(canvasEl)
  }

  function setEnabled(enabled: boolean) {
    if (enabled) {
      activate()
    } else {
      deactivate()
    }
  }

  function exportTextbox(textbox: Textbox): RemixTextSceneEntry {
    return {
      text: textbox.text,
      top: textbox.top,
      left: textbox.left,
      angle: textbox.angle,
      width: textbox.width,
      height: textbox.height,
      scale: textbox.scaleX,
    }
  }

  function exportScene(): RemixTextScene {
    return {
      textboxes: textboxes.map(exportTextbox),
    }
  }

  async function importScene(data: RemixTextScene) {
    for (const box of data.textboxes) {
      createTextbox(box.text, {
        top: box.top,
        left: box.left,
        width: box.width,
        height: box.height,
        angle: box.angle,
        scaleX: box.scale,
        scaleY: box.scale,
      })
    }
  }

  function clearScene() {
    canvas.clear()
    textboxes.length = 0
    updateObjectCount()
  }

  function updateObjectCount() {
    scope.text.objectCount = textboxes.length
  }

  function onSnapshot() {
    canvas.discardActiveObject()
    canvas.renderAll()
  }

  function getCanvas() {
    return container?.querySelector(
      "canvas.lower-canvas",
    ) as HTMLCanvasElement | null
  }

  return {
    add,
    dispose,
    setEnabled,
    exportScene,
    importScene,
    clearScene,
    onSnapshot,
    getCanvas,
  }
}
