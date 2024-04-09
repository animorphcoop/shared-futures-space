export interface RemixDraw {
  canvas: HTMLCanvasElement
}

export function useDraw({ canvas }: RemixDraw) {
  function setEnabled(enabled: boolean) {
    if (enabled) {
      activate()
    } else {
      deactivate()
    }
  }
  function activate() {
    canvas.addEventListener("pointermove", onPointerMove)
    canvas.addEventListener("pointerdown", onPointerDown)
    canvas.addEventListener("pointerup", onPointerCancel)
    canvas.addEventListener("pointerleave", onPointerCancel)
  }

  function deactivate() {
    canvas.removeEventListener("pointermove", onPointerMove)
    canvas.removeEventListener("pointerdown", onPointerDown)
    canvas.removeEventListener("pointerup", onPointerCancel)
    canvas.removeEventListener("pointerleave", onPointerCancel)
    canvas.style.cursor = ""
  }

  function onPointerMove(event: PointerEvent) {}

  function onPointerDown(event: PointerEvent) {}

  function onPointerCancel(event: PointerEvent) {}

  function dispose() {
    deactivate()
  }

  return {
    dispose,
    setEnabled,
  }
}
