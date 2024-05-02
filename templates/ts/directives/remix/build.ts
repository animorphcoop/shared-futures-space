import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js"
import { RenderPass } from "three/addons/postprocessing/RenderPass.js"
import { OutlinePass } from "three/addons/postprocessing/OutlinePass.js"
import { OutputPass } from "three/addons/postprocessing/OutputPass.js"
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js"
import { FXAAShader } from "three/addons/shaders/FXAAShader.js"

import {
  AmbientLight,
  Camera,
  Color,
  DirectionalLight,
  Object3D,
  PerspectiveCamera,
  Scene,
  SRGBColorSpace,
  TextureLoader,
  Vector2,
  WebGLRenderer,
  WebGLRendererParameters,
} from "three"
import { getModel } from "@/templates/ts/directives/remix/models.ts"
import anime from "animejs/lib/anime.es"
import { useTransform } from "@/templates/ts/directives/remix/transform.ts"
import { ElementWithXAttributes } from "alpinejs"
import {
  RemixBuildObject,
  RemixBuildScene,
  RemixScope,
} from "@/templates/ts/directives/remix/types.ts"

export function useBuild({
  scope,
  container,
}: {
  scope: RemixScope
  container: ElementWithXAttributes
}) {
  const objects: Object3D[] = []

  const aspectRatio = 16 / 9

  async function add(
    modelName: string,
    animate: boolean = true,
  ): Promise<Object3D> {
    try {
      scope.build.action = "move"
      scope.loadingCount++
      const model = await getModel(modelName)
      const instance = model.scene.clone()
      instance.userData.modelName = modelName
      if (animate) {
        instance.scale.set(0, 0, 0)
      }
      instance.position.set(0, 0, 0)
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

  const texture = new TextureLoader().load(scope.background)
  texture.colorSpace = SRGBColorSpace

  const scene = new Scene()

  new TextureLoader().load(scope.background, (texture) => {
    texture.colorSpace = SRGBColorSpace
    scene.background = texture
  })

  const lightColour = 0xeeeeee
  const light = new AmbientLight(lightColour, 1.2)
  scene.add(light)

  const directionalLight = new DirectionalLight(lightColour, 3)
  scene.add(directionalLight)

  /* The camera parameters are important, to try and make the objects in the scene look
     like they are part of the background image

     You can't just change them, as previously saved scenes won't look as they did when they
     were saved.

     So, *if* you do need to change them, then we need to also implement a way to use the
     right parameters with a given scene.*/
  const camera = new PerspectiveCamera(30, aspectRatio, 0.1, 1000)
  camera.position.set(0, 2, 16)
  camera.lookAt(scene.position)
  camera.position.y = 4

  scene.add(camera)

  let buildCanvas = container.querySelector(
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
  renderer.setSize(container.clientWidth, container.clientWidth / aspectRatio)
  // renderer.setSize(1920, 1080)
  if (!buildCanvas) {
    container.appendChild(renderer.domElement)
    buildCanvas = renderer.domElement
  }

  const {
    composer,
    outlinePass,
    dispose: disposeComposer,
    updateSize: updateComposerSize,
  } = useOutlineComposer(scene, camera, renderer)

  const transform = useTransform({
    scope,
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
          for (const obj of toRemove) {
            const idx = objects.indexOf(obj)
            if (idx !== -1) {
              objects.splice(idx, 1)
            }
          }
        },
      })
    },
  })

  function setEnabled(value: boolean) {
    transform.setEnabled(value)
  }

  function resizeRenderer() {
    const width = container.clientWidth
    const height = container.clientWidth / aspectRatio
    renderer.setSize(width, height)
    updateComposerSize(width, height)
  }

  window.addEventListener("resize", resizeRenderer)

  function dispose() {
    objects.length = 0
    window.removeEventListener("resize", resizeRenderer)
    disposeComposer()
    transform.dispose()
  }

  function animate() {
    composer.render()
    scope.build.objectCount = objects.length
  }

  function getCanvas(): HTMLCanvasElement {
    return renderer.domElement
  }

  function clearScene() {
    // Clear out old objects
    for (const object of objects) {
      scene.remove(object)
    }
    objects.length = 0
  }

  function exportScene(): RemixBuildScene {
    const exportObjects: RemixBuildObject[] = []
    for (const object of objects) {
      const { position, rotation } = object
      exportObjects.push({
        modelName: object.userData.modelName,
        position: { x: position.x, y: position.y, z: position.z },
        rotation: { y: rotation.y },
        scale: object.scale.x, // we always scale them all the same
      })
    }
    return {
      objects: exportObjects,
    }
  }

  async function importScene(data: RemixBuildScene) {
    await Promise.all(
      data.objects.map(async (importObject) => {
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
  }

  return {
    animate,
    add,
    dispose,
    setEnabled,
    clearScene,
    exportScene,
    importScene,
    getCanvas,
  }
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
