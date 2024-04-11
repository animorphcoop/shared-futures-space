import { DirectiveUtilities, ElementWithXAttributes } from "alpinejs"

import anime from "animejs/lib/anime.es.js"

import {
  AmbientLight,
  Camera,
  Color,
  DirectionalLight,
  Object3D,
  PerspectiveCamera,
  Scene,
  TextureLoader,
  Vector2,
  WebGLRenderer,
  WebGLRendererParameters,
} from "three"
import { getModel, ModelInfo } from "./models.ts"

import bg from "./bg.jpg?url"
import { useTransform } from "@/templates/ts/directives/remix/transform.ts"
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js"
import { RenderPass } from "three/addons/postprocessing/RenderPass.js"
import { OutlinePass } from "three/addons/postprocessing/OutlinePass.js"
import { OutputPass } from "three/addons/postprocessing/OutputPass.js"
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js"
import { FXAAShader } from "three/addons/shaders/FXAAShader.js"
import {
  RemixDrawScene,
  useDraw,
} from "@/templates/ts/directives/remix/draw.ts"
import { throwNotImplementedError } from "@/templates/ts/directives/remix/utils.ts"
import { useText } from "@/templates/ts/directives/remix/text.ts"
import {
  RemixTextScene,
  useTextFabric,
} from "@/templates/ts/directives/remix/text-fabric.ts"
import { renderColorRamp } from "maplibre-gl/src/util/color_ramp.ts"

export interface RemixObject {
  modelName: string
  position: { x: number; y: number; z: number }
  rotation: { y: number }
  scale: number
}

export interface RemixScene {
  objects: RemixObject[]
  text?: RemixTextScene
  draw?: RemixDrawScene
}

export type RemixMode = "draw" | "text" | "build"

export type RemixTransformAction = "move" | "rotate" | "scale" | "remove"

export interface RemixScope {
  loadingCount: number
  modelInfos: ModelInfo[]
  objects: string[]
  mode: RemixMode
  transformAction: RemixTransformAction
  addObject: (modelName: string) => Promise<Object3D>
  importScene: (scene: RemixScene) => void
  exportScene: () => RemixScene
  createSnapshot: () => void
  draw: {
    mode: "draw" | "erase"
    colour: string
    strokeWidth: number
    palette: string[]
  }
}

export function defaultRemixScope(): RemixScope {
  return {
    loadingCount: 0,
    modelInfos: [],
    objects: [],
    mode: "text",
    transformAction: "move",
    addObject: throwNotImplementedError,
    importScene: throwNotImplementedError,
    exportScene: throwNotImplementedError,
    createSnapshot: throwNotImplementedError,
    draw: {
      mode: "draw",
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
  const objects: Object3D[] = []

  let snapshot = false

  scope.createSnapshot = () => {
    snapshot = true
  }

  async function add(
    modelName: string,
    animate: boolean = true,
  ): Promise<Object3D> {
    try {
      scope.transformAction = "move"
      scope.loadingCount++
      const model = await getModel(modelName)
      const instance = model.scene.clone()
      instance.userData.modelName = modelName
      if (animate) {
        instance.scale.set(0, 0, 0)
      }
      scene.add(instance)
      objects.push(instance)

      if (animate) {
        anime({
          targets: [instance.scale],
          x: 1,
          y: 1,
          z: 1,
          easing: "easeInOutSine",
          duration: 300,
        })
      }

      return instance
    } finally {
      --scope.loadingCount
    }
  }

  scope.addObject = add

  const aspectRatio = 16 / 9

  const texture = new TextureLoader().load(bg)

  const scene = new Scene()
  scene.background = texture

  const lightColour = 0xeeeeee
  const light = new AmbientLight(lightColour, 0.6)
  scene.add(light)

  const directionalLight = new DirectionalLight(lightColour, 2.4)
  scene.add(directionalLight)

  const camera = new PerspectiveCamera(30, aspectRatio, 0.1, 1000)

  camera.position.set(0, 2, 16)
  camera.lookAt(scene.position)

  scene.add(camera)

  let buildCanvas = el.querySelector(
    "canvas.remix__build",
  ) as HTMLCanvasElement | null
  const rendererOptions: WebGLRendererParameters = {
    antialias: true,
  }
  if (buildCanvas) {
    rendererOptions.canvas = buildCanvas
  }
  const renderer = new WebGLRenderer(rendererOptions)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.setSize(el.clientWidth, el.clientWidth / aspectRatio)
  // renderer.setSize(1920, 1080)
  if (!buildCanvas) {
    el.appendChild(renderer.domElement)
    buildCanvas = renderer.domElement
  }

  const {
    composer,
    outlinePass,
    dispose: disposeComposer,
    updateSize: updateComposerSize,
  } = useOutlineComposer(scene, camera, renderer)

  const {
    setEnabled: setTransformEnabled,
    setAction: _setTransFormAction,
    dispose: disposeTransform,
  } = useTransform({
    objects,
    camera,
    canvas: buildCanvas,
    onSelect(selectedObjects) {
      outlinePass.selectedObjects = selectedObjects
    },
    onRemove(toRemove) {
      anime({
        targets: toRemove.map((object) => object.scale),
        x: 0,
        y: 0,
        z: 0,
        easing: "easeInOutSine",
        duration: 300,
        complete() {
          scene.remove(...toRemove)
        },
      })
    },
  })

  let drawContainer = el.querySelector(
    "div.remix__draw",
  ) as HTMLDivElement | null
  if (!drawContainer) throw new Error('Missing <div class="remix__draw"></div>')

  let textContainer = el.querySelector(
    "div.remix__text",
  ) as HTMLDivElement | null
  if (!textContainer) throw new Error('Missing <div class="remix__text"></div>')

  const {
    setEnabled: setDrawEnabled,
    dispose: disposeDraw,
    importScene: importSceneDraw,
    exportScene: exportSceneDraw,
    clearScene: clearSceneDraw,
  } = useDraw({
    scope,
    container: drawContainer,
  })

  // const { setEnabled: setTextEnabled, dispose: disposeText } = useText({
  //   scope,
  //   container: textContainer,
  // })

  const {
    setEnabled: setTextEnabled,
    dispose: disposeText,
    exportScene: exportSceneText,
    importScene: importSceneText,
    clearScene: clearSceneText,
    onSnapshot: onSnapshotText,
  } = useTextFabric({
    scope,
    container: textContainer,
  })

  effect(() => {
    setTransformEnabled(scope.mode === "build")
    setTextEnabled(scope.mode === "text")
    setDrawEnabled(scope.mode === "draw")
  })

  effect(() => {
    _setTransFormAction(scope.transformAction)
  })

  cleanup(() => {
    disposeTransform()
    disposeDraw()
    disposeText()
    disposeComposer()
  })

  function resizeRenderer() {
    // renderer.setSize(el.clientWidth, el.clientWidth / aspectRatio)
    const width = el.clientWidth
    const height = el.clientWidth / aspectRatio
    renderer.setSize(width, height)
    updateComposerSize(width, height)
  }

  window.addEventListener("resize", resizeRenderer)
  cleanup(() => {
    window.removeEventListener("resize", resizeRenderer)
  })

  scope.exportScene = () => {
    const exportData: RemixScene = {
      objects: [],
      text: exportSceneText(),
      draw: exportSceneDraw(),
    }
    for (const object of objects) {
      const { position, rotation } = object
      exportData.objects.push({
        modelName: object.userData.modelName,
        position: { x: position.x, y: position.y, z: position.z },
        rotation: { y: rotation.y },
        scale: object.scale.x, // we always scale them all the same
      })
    }
    return exportData
  }

  scope.importScene = async (importScene: RemixScene) => {
    // Clear out old objects
    for (const object of objects) {
      scene.remove(object)
    }
    objects.length = 0
    try {
      scope.loadingCount++
      await Promise.all(
        importScene.objects.map(async (importObject) => {
          const object = await add(importObject.modelName, false)
          const { position, scale, rotation } = importObject
          object.position.set(position.x, position.y, position.z)
          object.rotation.set(0, rotation.y, 0)
          //object.scale.set(scale, scale, scale)
          object.scale.set(0, 0, 0)
          anime({
            targets: [object.scale],
            x: scale,
            y: scale,
            z: scale,
            easing: "easeInOutSine",
            duration: 300,
          })
        }),
      )

      clearSceneText()
      clearSceneDraw()

      // Text
      if (importScene.text) {
        importSceneText(importScene.text)
      }
      if (importScene.draw) {
        importSceneDraw(importScene.draw)
      }
    } finally {
      --scope.loadingCount
    }
  }

  function animate() {
    requestAnimationFrame(animate)
    // renderer.render(scene, camera)
    composer.render()
    if (snapshot) {
      snapshot = false
      onSnapshotText()
      const outputCanvas = document.createElement("canvas")
      const textCanvas = textContainer?.querySelector(
        "canvas.lower-canvas",
      ) as HTMLCanvasElement | null
      const drawCanvas = drawContainer?.querySelector("canvas")
      console.log("textCanvas", textCanvas)
      const buildCanvas = renderer.domElement
      outputCanvas.width = buildCanvas.width
      outputCanvas.height = buildCanvas.height

      const context = outputCanvas.getContext("2d")
      if (context && drawCanvas && textCanvas) {
        context.drawImage(buildCanvas, 0, 0)
        context.drawImage(drawCanvas, 0, 0)
        context.drawImage(textCanvas, 0, 0)

        const dataURL = outputCanvas.toDataURL()
        const img = new Image()
        img.src = dataURL
        document.body.appendChild(img)
      }
    }
  }

  animate()
}

function useOutlineComposer(
  scene: Scene,
  camera: Camera,
  renderer: WebGLRenderer,
) {
  const composer = new EffectComposer(renderer)

  const renderPass = new RenderPass(scene, camera)
  composer.addPass(renderPass)

  const domElement = renderer.domElement

  renderPass.setSize(domElement.clientWidth, domElement.clientHeight)

  const outlinePass = new OutlinePass(
    new Vector2(domElement.clientWidth, domElement.clientHeight),
    scene,
    camera,
  )
  outlinePass.visibleEdgeColor = new Color(0xffffff)
  composer.addPass(outlinePass)

  const outputPass = new OutputPass()
  composer.addPass(outputPass)

  const effectFXAA = new ShaderPass(FXAAShader)

  effectFXAA.uniforms["resolution"].value.set(
    1 / domElement.clientWidth,
    1 / domElement.clientHeight,
  )
  composer.addPass(effectFXAA)

  function updateSize(width: number, height: number) {
    composer.setSize(width, height)
    effectFXAA.uniforms["resolution"].value.set(1 / width, 1 / height)
  }

  function dispose() {}

  return {
    dispose,
    composer,
    outlinePass,
    updateSize,
  }
}
