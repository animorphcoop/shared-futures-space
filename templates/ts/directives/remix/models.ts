import { REVISION } from "three"
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js"
import { GLTF, GLTFLoader } from "three/addons/loaders/GLTFLoader.js"

// TODO: tidy this up a bit as we don't need the import bit now...

const loader = new GLTFLoader()

// Draco loader enables us to load compressed models
const dracoLoader = new DRACOLoader()
// We can't bundle these draco files directly with vite as they get loaded not through vite
// TODO: could probably do a vite plugin to copy them into location...
const decoderPath = `https://cdn.jsdelivr.net/npm/three@0.${REVISION}.0/examples/jsm/libs/draco/`
dracoLoader.setDecoderPath(decoderPath)
loader.setDRACOLoader(dracoLoader)

export interface ModelInfo {
  name: string
  previewUrl: string
  modelUrl: string
}

// name -> url (that we can pass to our GLTFLoader)
const modelInfos: { [name: string]: ModelInfo } = {}
const models: { [name: string]: Promise<GLTF> } = {}

export async function getModel(modelName: string): Promise<GLTF> {
  if (modelName in models) return await models[modelName]
  const modelInfo = modelInfos[modelName]
  if (!modelInfo) throw new Error(`don't know model ${modelName}`)
  // Put the promise in here, so if we request it twice quickly, we still only load it once
  const promise = loader.loadAsync(modelInfos[modelName].modelUrl)
  models[modelName] = promise
  return await promise
}

export default modelInfos
