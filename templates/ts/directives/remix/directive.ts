import Alpine from "alpinejs";
import {RemixAPI} from "@/templates/ts/directives/remix/remix.ts";

/*
  Remix directive

  Loads all the remix libraries async, so we don't get
  them unless we are actually using the directive
 */
Alpine.directive('remix', async (el, directive, utilities) => {
  const { cleanup } = utilities

  const data = Alpine.reactive<RemixAPI>({
    loadingCount: 0,
    modelInfos: [],
    objects: [],
    remixAdd: () => {throw new Error("Not implemented!")},
    remixImport: () => {},
    remixExport: () => ({ objects: [] }),
    remixSnapshot: () => {},
  })

  const destroyScope = Alpine.addScopeToNode(el, data)
  cleanup(() => destroyScope())

  const { callback } = await import('./remix.ts')
  callback(el, directive, utilities, data)
})