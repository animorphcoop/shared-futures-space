import { RemixScope } from "@/templates/ts/directives/remix/remix.ts"

import {
  Canvas,
  Group,
  Rect,
  SerializedTextboxProps,
  TClassProperties,
  Textbox,
  TextboxProps,
} from "fabric"

import * as fabric from "fabric"

export interface RemixTextFabric {
  scope: RemixScope
  container: HTMLDivElement
}

export function useTextFabric({ scope, container }: RemixTextFabric) {
  const canvasEl: HTMLCanvasElement = document.createElement("canvas")
  container.appendChild(canvasEl)

  // canvasEl.style.width = `${container.clientWidth}px`
  // canvasEl.style.height = `${container.clientHeight}px`

  const canvas = new Canvas(canvasEl)

  const sceneWidth = 1920
  const sceneHeight = 1080

  const scale = container.clientWidth / sceneWidth

  canvas.setDimensions({
    width: sceneWidth * scale,
    height: sceneHeight * scale,
  })
  canvas.setZoom(scale)
  console.log("set zoom to", scale)

  const textValue = "omg it works"
  const text = new Textbox(textValue, {
    originX: "center",
    splitByGrapheme: true,
    width: 200,
    top: 20,
    left: 150,
    fontSize: 40,
    // padding: 20,
    backgroundColor: "#FAFFC6",
    /*
    styles: fabric.util.stylesFromArray(
      [
        {
          style: {
            fontWeight: "bold",
            fontSize: 64,
          },
          start: 0,
          end: 9,
        },
      ],
      textValue,
    ),

     */
  })
  text.setControlsVisibility({
    mt: false,
    mb: false,
  })

  // const group = new Group([text], {
  //   left: 150,
  //   top: 100,
  //   backgroundColor: "#FAFFC6",
  // })
  canvas.add(text)

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

    // stage.width(sceneWidth * scale)
    // stage.height(sceneHeight * scale)
    // stage.scale({ x: scale, y: scale })
  }

  window.addEventListener("resize", fitStageIntoParentContainer)

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

  function setEnabled(enabled: boolean) {
    if (enabled) {
      activate()
    } else {
      deactivate()
    }
  }

  return {
    dispose,
    setEnabled,
  }
}
