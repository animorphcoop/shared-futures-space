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
import modelInfos, { getModel, ModelInfo } from "./models.ts"

import bg from "./bg.jpg?url"
import { useTransform } from "@/templates/ts/directives/remix/transform.ts"
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js"
import { RenderPass } from "three/addons/postprocessing/RenderPass.js"
import { OutlinePass } from "three/addons/postprocessing/OutlinePass.js"
import { OutputPass } from "three/addons/postprocessing/OutputPass.js"
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js"
import { FXAAShader } from "three/addons/shaders/FXAAShader.js"

export interface RemixObject {
  modelName: string
  position: { x: number; y: number; z: number }
  rotation: { y: number }
  scale: number
}

export interface RemixScene {
  objects: RemixObject[]
}

export type RemixTransformMode = "move" | "rotate" | "scale" | "remove"

export interface RemixAPI {
  loadingCount: number
  modelInfos: ModelInfo[]
  objects: string[]
  remixTransformMode: RemixTransformMode
  remixSetTransformMode: (mode: RemixTransformMode) => void
  remixAdd: (modelName: string) => Promise<Object3D>
  remixImport: (scene: RemixScene) => void
  remixExport: () => RemixScene
  remixSnapshot: () => void
}

const notImplemented = () => {
  throw new Error("Not implemented!")
}

export function emptyRemix(): RemixAPI {
  return {
    loadingCount: 0,
    modelInfos: Object.values(modelInfos),
    objects: [],
    remixTransformMode: "move",
    remixSetTransformMode: notImplemented,
    remixAdd: notImplemented,
    remixImport: notImplemented,
    remixExport: notImplemented,
    remixSnapshot: notImplemented,
  }
}

export interface RemixSetup {
  el: ElementWithXAttributes
  data: RemixAPI
  cleanup: DirectiveUtilities["cleanup"]
}

export async function setup({ el, data, cleanup }: RemixSetup) {
  const objects: Object3D[] = []

  let snap = false

  data.modelInfos = Object.values(modelInfos)
  data.remixSnapshot = () => {
    snap = true
  }

  async function add(
    modelName: string,
    animate: boolean = true,
  ): Promise<Object3D> {
    try {
      setMode("move")
      data.loadingCount++
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
      --data.loadingCount
    }
  }

  data.remixAdd = add

  data.remixExport = () => {
    const exportData: RemixScene = {
      objects: [],
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

  data.remixImport = async (importScene: RemixScene) => {
    // Clear out old objects
    for (const object of objects) {
      scene.remove(object)
    }
    objects.length = 0
    try {
      data.loadingCount++
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
    } finally {
      --data.loadingCount
    }
  }

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

  const canvas = el.querySelector("canvas")
  const rendererOptions: WebGLRendererParameters = {
    antialias: true,
  }
  if (canvas) {
    rendererOptions.canvas = canvas
  }
  const renderer = new WebGLRenderer(rendererOptions)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.setSize(el.clientWidth, el.clientWidth / aspectRatio)
  if (!canvas) {
    el.appendChild(renderer.domElement)
  }

  const {
    composer,
    outlinePass,
    dispose: disposeComposer,
  } = useOutlineComposer(scene, camera, renderer)

  const { setMode: setTransformMode, dispose: disposeTransform } = useTransform(
    {
      objects,
      camera,
      domElement: renderer.domElement,
      onSelect(selectedObjects) {
        outlinePass.selectedObjects = selectedObjects
      },
      onRemove(toRemove) {
        anime({
          targets: toRemove.map((obj) => obj.scale),
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
    },
  )

  function setMode(mode: RemixTransformMode) {
    data.remixTransformMode = mode
    setTransformMode(mode)
  }

  data.remixSetTransformMode = setMode

  cleanup(() => {
    disposeTransform()
    disposeComposer()
  })

  function resizeRenderer() {
    renderer.setSize(el.clientWidth, el.clientWidth / aspectRatio)
  }

  window.addEventListener("resize", resizeRenderer)
  cleanup(() => {
    window.removeEventListener("resize", resizeRenderer)
  })

  function animate() {
    requestAnimationFrame(animate)
    // renderer.render(scene, camera)
    composer.render()
    if (snap) {
      snap = false
      const dataURL = renderer.domElement.toDataURL()
      const img = new Image()
      img.src = dataURL
      document.body.appendChild(img)
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

  function updateResolution() {
    const width = domElement.clientWidth
    const height = domElement.clientHeight
    // TODO: hmm the resolution doesn't seem to go back up
    // renderer.setSize(el.clientWidth, el.clientWidth / aspectRatio)
    outlinePass.resolution.set(width, height)
    effectFXAA.uniforms["resolution"].value.set(1 / width, 1 / height)
  }

  window.addEventListener("resize", updateResolution)
  function dispose() {
    window.removeEventListener("resize", updateResolution)
  }

  return {
    dispose,
    composer,
    outlinePass,
  }
}
