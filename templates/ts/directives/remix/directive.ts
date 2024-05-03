import Alpine from "alpinejs"
import { defaultRemixScope } from "@/templates/ts/directives/remix/remix.ts"
import modelInfos, {
  ModelInfo,
} from "@/templates/ts/directives/remix/models.ts"
import { RemixScope } from "@/templates/ts/directives/remix/types.ts"

export interface RemixDirectiveOptions {
  background: string // background image URL
  models: ModelInfo[] // available three models
  scene: object // scene to start with
}

Alpine.directive(
  "remix",
  async (el, { expression }, { cleanup, evaluate, effect }) => {
    const config = evaluate(expression) as RemixDirectiveOptions
    if (config.models) {
      for (const model of config.models) {
        modelInfos[model.name] = model
      }
    }
    const scope = Alpine.reactive<RemixScope>(defaultRemixScope())
    scope.background = config.background
    scope.scene = config.scene
    scope.modelInfos = Object.values(modelInfos)

    const destroyScope = Alpine.addScopeToNode(el, scope as any)
    cleanup(() => destroyScope())

    const { setup } = await import("./remix.ts")
    await setup({ el, scope, effect, cleanup })
  },
)
