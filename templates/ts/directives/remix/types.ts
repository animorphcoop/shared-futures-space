import { RemixDrawScene } from "@/templates/ts/directives/remix/draw.ts"
import { ModelInfo } from "@/templates/ts/directives/remix/models.ts"
import { Object3D } from "three"

export interface RemixScope {
  loadingCount: number
  modelInfos: ModelInfo[]
  mode: RemixMode
  importScene: (scene: RemixScene) => void
  exportScene: () => RemixScene
  createSnapshot: () => void
  build: {
    action: RemixBuildAction
    objectCount: number
    add: (modelName: string) => Promise<Object3D>
  }
  draw: {
    action: RemixDrawAction
    colour: string
    strokeWidth: number
    palette: string[]
    clear: () => void
  }
  text: {
    action: RemixTextAction
    objectCount: number
    add: () => void
  }
}

export interface RemixBuildScene {
  objects: RemixBuildObject[]
}

export interface RemixTextScene {
  textboxes: RemixTextSceneEntry[]
}

export interface RemixTextSceneEntry {
  text: string
  top: number
  left: number
  width: number
  height: number
  angle: number
  scale: number
}

// Used for export/import
export interface RemixScene {
  build?: RemixBuildScene
  text?: RemixTextScene
  draw?: RemixDrawScene
}

export type RemixMode = "draw" | "text" | "build"

export type RemixBuildAction = "move" | "rotate" | "scale" | "remove"
export interface RemixBuildObject {
  modelName: string
  position: { x: number; y: number; z: number }
  rotation: { y: number }
  scale: number
}

export type RemixTextAction = "move" | "remove"

export type RemixDrawAction = "draw" | "erase"
