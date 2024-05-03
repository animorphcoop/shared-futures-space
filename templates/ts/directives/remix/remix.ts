import { DirectiveUtilities, ElementWithXAttributes } from "alpinejs"
import { useDraw } from "@/templates/ts/directives/remix/draw.ts"
import { throwNotImplementedError } from "@/templates/ts/directives/remix/utils.ts"
import { useText } from "@/templates/ts/directives/remix/text.ts"
import { useBuild } from "@/templates/ts/directives/remix/build.ts"
import {
  RemixScene,
  RemixScope,
} from "@/templates/ts/directives/remix/types.ts"

/*
  The remix scope holds what we need to pass between the directive and the
  template. Anything that we need to reference in the template should be here.

  It gets created as a reactive object, so everything stays up to date nicely.

  The "throwNotImplementedError" is used for all the functions/methods because
  we need to initialize the scope early on when we define the directive.

  ... but we lazy load all the libraries, so don't have all the right context
  available at the time of scope initialization.
 */
export function defaultRemixScope(): RemixScope {
  return {
    background: "",
    loadingCount: 0,
    scene: undefined,
    modelInfos: [],
    importScene: throwNotImplementedError,
    exportScene: throwNotImplementedError,
    exportSnapshot: throwNotImplementedError,
    exportAll: throwNotImplementedError,
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

type SnapshotCallback = (snapshot: Blob) => void

export async function setup({ el, scope, cleanup, effect }: RemixSetup) {
  let drawContainer = el.querySelector(
    "div.remix__draw",
  ) as HTMLDivElement | null
  if (!drawContainer) throw new Error('Missing <div class="remix__draw"></div>')

  let textContainer = el.querySelector(
    "div.remix__text",
  ) as HTMLDivElement | null
  if (!textContainer) throw new Error('Missing <div class="remix__text"></div>')

  // Initialize all our different mode modules
  const build = useBuild({ scope, container: el })
  const draw = useDraw({ scope, container: drawContainer })
  const text = useText({ scope, container: textContainer })

  // Set a callback function here, and then we'll create a snapshot and call you back!
  let snapshotCallback: SnapshotCallback | null = null

  /* Wiring up the scope functions */

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

  scope.exportScene = () => {
    return {
      build: build.exportScene(),
      text: text.exportScene(),
      draw: draw.exportScene(),
    } as RemixScene
  }

  scope.exportSnapshot = () => {
    return new Promise((resolve) => {
      snapshotCallback = resolve
    })
  }

  scope.exportAll = async () => {
    const scene = scope.exportScene()
    const snapshot = await scope.exportSnapshot()
    return { scene, snapshot }
  }

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

  // Main animation loop
  function animate() {
    requestAnimationFrame(animate)
    build.animate()
    if (snapshotCallback) {
      // We have to do the snapshot in this loop immediately after render()
      // otherwise the three.js canvas data is not available
      createSnapshot().then((blob) => {
        if (snapshotCallback) {
          snapshotCallback(blob)
        }
        snapshotCallback = null
      })
    }
  }

  async function createSnapshot(): Promise<Blob> {
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
      return await toBlob(outputCanvas)
    }
    throw new Error("failed to create snapshot")
  }

  if (scope.scene) {
    // If we already have a scene, import it!
    scope.importScene(scope.scene)
  }

  animate()
}

async function toBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob)
      } else {
        reject()
      }
    })
  })
}

// @ts-expect-error just keeping it here for now, maybe useful!
function downloadBlob(blob: Blob, filename: string) {
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
}
