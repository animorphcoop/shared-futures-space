import { DirectiveUtilities, ElementWithXAttributes } from "alpinejs"
import { useDraw } from "@/templates/ts/directives/remix/draw.ts"
import { throwNotImplementedError } from "@/templates/ts/directives/remix/utils.ts"
import { useText } from "@/templates/ts/directives/remix/text.ts"
import { useBuild } from "@/templates/ts/directives/remix/build.ts"
import {
  RemixScene,
  RemixScope,
} from "@/templates/ts/directives/remix/types.ts"

export function defaultRemixScope(): RemixScope {
  return {
    loadingCount: 0,
    modelInfos: [],
    importScene: throwNotImplementedError,
    exportScene: throwNotImplementedError,
    createSnapshot: throwNotImplementedError,
    mode: "build",
    build: {
      add: throwNotImplementedError,
      action: "move",
      objectCount: 0,
    },
    draw: {
      action: "draw",
      colour: "#DBEDB5",
      strokeWidth: 10,
      palette: [
        "#F5F5F5",
        "#D9D9D9",
        "#000000",
        "#DBEDB5",
        "#D98585",
        "#9AC1E5",
        "#378799",
        "#9A500C",
      ],
      clear: throwNotImplementedError,
    },
    text: {
      action: "move",
      add: throwNotImplementedError,
      objectCount: 0,
    },
  }
}

export interface RemixSetup {
  el: ElementWithXAttributes
  scope: RemixScope
  effect: DirectiveUtilities["effect"]
  cleanup: DirectiveUtilities["cleanup"]
}

export async function setup({ el, scope, cleanup, effect }: RemixSetup) {
  let snapshot = false

  scope.createSnapshot = () => {
    snapshot = true
  }

  let drawContainer = el.querySelector(
    "div.remix__draw",
  ) as HTMLDivElement | null
  if (!drawContainer) throw new Error('Missing <div class="remix__draw"></div>')

  let textContainer = el.querySelector(
    "div.remix__text",
  ) as HTMLDivElement | null
  if (!textContainer) throw new Error('Missing <div class="remix__text"></div>')

  const build = useBuild({ scope, container: el })
  const draw = useDraw({ scope, container: drawContainer })
  const text = useText({ scope, container: textContainer })

  scope.build.add = build.add
  scope.text.add = text.add
  scope.draw.clear = draw.clearScene

  effect(() => {
    build.setEnabled(scope.mode === "build")
    text.setEnabled(scope.mode === "text")
    draw.setEnabled(scope.mode === "draw")
  })

  cleanup(() => {
    build.dispose()
    draw.dispose()
    text.dispose()
  })

  scope.exportScene = () => {
    return {
      build: build.exportScene(),
      text: text.exportScene(),
      draw: draw.exportScene(),
    } as RemixScene
  }

  scope.importScene = async (importScene: RemixScene) => {
    try {
      scope.loadingCount++

      build.clearScene()
      text.clearScene()
      draw.clearScene()

      if (importScene.build) {
        await build.importScene(importScene.build)
      }
      if (importScene.text) {
        await text.importScene(importScene.text)
      }
      if (importScene.draw) {
        await draw.importScene(importScene.draw)
      }
    } finally {
      --scope.loadingCount
    }
  }

  function animate() {
    requestAnimationFrame(animate)
    build.animate()
    if (snapshot) {
      // We have to do the snapshot in this loop immediately after render()
      // otherwise the three.js canvas data is not available

      snapshot = false
      buildSnapshot()
    }
  }

  function buildSnapshot() {
    text.onSnapshot()
    const outputCanvas = document.createElement("canvas")

    const buildCanvas = build.getCanvas()
    const textCanvas = text.getCanvas()
    const drawCanvas = draw.getCanvas()
    outputCanvas.width = buildCanvas.width
    outputCanvas.height = buildCanvas.height

    const context = outputCanvas.getContext("2d")
    if (context && drawCanvas && textCanvas) {
      context.drawImage(buildCanvas, 0, 0)
      context.drawImage(drawCanvas, 0, 0)
      context.drawImage(textCanvas, 0, 0)
      downloadCanvas(outputCanvas, "snapshot.png")
    }
  }

  animate()
}

function downloadCanvas(canvas: HTMLCanvasElement, filename: string) {
  canvas.toBlob((blob) => {
    if (!blob) return
    const objectURL = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = objectURL
    a.download = filename
    function click() {
      a.removeEventListener("click", click)
      setTimeout(() => {
        URL.revokeObjectURL(objectURL)
      }, 200)
    }
    a.addEventListener("click", click)
    a.click()
  })
}
