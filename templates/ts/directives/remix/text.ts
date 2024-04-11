import Konva from "konva"
import {
  getPointerPosition,
  useFitStageIntoParentContainer,
} from "@/templates/ts/directives/remix/konva-utils.ts"
import Alpine from "alpinejs"
import { RemixScope } from "@/templates/ts/directives/remix/remix.ts"

export interface RemixText {
  scope: RemixScope
  container: HTMLDivElement
}

export function useText({ scope, container }: RemixText) {
  const sceneWidth = 1920
  const sceneHeight = 1080

  const objects: Konva.Group[] = []

  const stage = new Konva.Stage({
    container,
    width: sceneWidth,
    height: sceneHeight,
  })

  container.style.pointerEvents = "none"

  const layer = new Konva.Layer()
  stage.add(layer)

  var textNode = new Konva.Text({
    text: "Some text here",
    x: 50,
    y: 80,
    fontSize: 60,
    draggable: true,
    width: 500,
  })

  layer.add(textNode)

  const tr = new Konva.Transformer({
    node: textNode,
    enabledAnchors: ["middle-left", "middle-right"],
    // set minimum width of text
    boundBoxFunc: function (oldBox, newBox) {
      newBox.width = Math.max(30, newBox.width)
      return newBox
    },
  })

  textNode.on("transform", function () {
    // reset scale, so only with is changing by transformer
    textNode.setAttrs({
      width: textNode.width() * textNode.scaleX(),
      scaleX: 1,
    })
  })

  layer.add(tr)

  stage.on("click", (event) => {
    if (event.target === stage) {
      const { x, y } = getPointerPosition(stage)

      console.log("click!", event.target)
      const padding = 30

      const foop = Alpine.reactive({
        x: 0,
        width: 500,
        height: 0,
      })

      // https://codesandbox.io/p/sandbox/react-konva-editable-resizable-text-55kyv?file=%2Fsrc%2FStickyNote.jsx%3A34%2C34
      var group = new Konva.Group({
        x,
        y,
        draggable: true,
        width: foop.width,
        height: foop.height,
      })

      const rect = new Konva.Rect({
        x: 0,
        y: 0,
        width: foop.width,
        height: foop.height,
        fill: "#FAFFC6",
        cornerRadius: 10,
        shadowBlur: 50,
        shadowOffset: { x: 30, y: 30 },
        shadowColor: "#666666",
      })

      var textNode = new Konva.Text({
        text: "new text node",
        x: padding,
        y: padding,
        fontSize: 40,
        // draggable: true,
        width: foop.width - padding * 2,
        // height: initialHeight,
        // sceneFunc(context, shape) {
        //   context.fillStyle = "rgb(255,255,204)"
        //   context.fillRect(0, 0, shape.width(), shape.height())
        //   ;(shape as Konva.Text)._sceneFunc(context)
        // },
      })

      const tr = new Konva.Transformer({
        node: textNode,
        rotateEnabled: false,
        enabledAnchors: ["middle-left", "middle-right"],
        // set minimum width of text
        boundBoxFunc: (_, newBox) => {
          newBox.width = Math.max(30, newBox.width)
          return newBox
        },
      })

      group.add(rect)
      group.add(textNode)
      group.add(tr)

      objects.push(group)

      foop.width = textNode.width() + padding * 2
      foop.height = textNode.height() + padding * 2

      textNode.on("transform", function () {
        // console.log("transform", textNode.x(), textNode.y())
        const textWidth = textNode.width() * textNode.scaleX()
        const textHeight = textNode.height() * textNode.scaleY()
        const x = textNode.x()
        // const transformX = textNode.x() - 30
        // console.log("transformX", transformX)
        textNode.setAttrs({
          // x: 0,
          width: textWidth,
          scaleX: 1,
        })
        // foop.x += transformX
        console.log("x", x)

        foop.x = x - padding
        foop.width = textWidth + padding * 2
        foop.height = textHeight + padding * 2

        // group.setAttrs({ width, height })
        // rect.setAttrs({ width, height })
      })

      // TODO: switch to the one that cleans up?
      Alpine.effect(() => {
        const width = foop.width
        const height = foop.height
        group.setAttrs({ width, height })
        rect.setAttrs({ width, height })
      })

      Alpine.effect(() => {
        console.log("setting rect x to", foop.x)
        rect.setAttrs({ x: foop.x })
      })

      // layer.add(tr)

      // group.add(textNode)
      layer.add(group)
    } else if (event.target instanceof Konva.Text) {
      console.log("clicked some text!")
    }
  })

  function activate() {
    container.style.pointerEvents = ""
  }

  function deactivate() {
    container.style.pointerEvents = "none"
    container.style.cursor = ""
  }

  const fitStageIntoParentContainer = useFitStageIntoParentContainer(
    stage,
    container,
    sceneWidth,
    sceneHeight,
  )
  fitStageIntoParentContainer()
  window.addEventListener("resize", fitStageIntoParentContainer)

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
