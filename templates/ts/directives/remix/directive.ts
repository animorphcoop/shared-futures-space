import Alpine from "alpinejs"
import { emptyRemix, RemixAPI } from "@/templates/ts/directives/remix/remix.ts"
import modelInfos, {
  ModelInfo,
} from "@/templates/ts/directives/remix/models.ts"

export interface RemixOptions {
  models: ModelInfo[]
}

/*
  Remix directive

  Loads all the remix libraries async, so we don't get
  them unless we are actually using the directive
 */
Alpine.directive("remix", async (el, { expression }, { cleanup, evaluate }) => {
  const config = evaluate(expression) as RemixOptions
  if (config.models) {
    for (const model of config.models) {
      modelInfos[model.name] = model
    }
  }
  const data = Alpine.reactive<RemixAPI>(emptyRemix())
  data.modelInfos = Object.values(modelInfos)

  const destroyScope = Alpine.addScopeToNode(el, data as any)
  cleanup(() => destroyScope())

  const { setup } = await import("./remix.ts")
  await setup({
    el,
    data,
    cleanup,
  })
})
