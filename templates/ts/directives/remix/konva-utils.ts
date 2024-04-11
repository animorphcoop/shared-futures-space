import Konva from "konva"

export function getPointerPosition(stage: Konva.Stage): Konva.Vector2d {
  if (!stage) throw new Error("no stage!")
  const position = stage.getPointerPosition()
  if (!position) throw new Error("could not get position")
  const stageTransform = stage.getAbsoluteTransform().copy()
  return stageTransform.invert().point(position)
}

export function useFitStageIntoParentContainer(
  stage: Konva.Stage,
  container: HTMLDivElement,
  sceneWidth: number,
  sceneHeight: number,
) {
  return () => {
    const containerWidth = container.offsetWidth
    const scale = containerWidth / sceneWidth
    stage.width(sceneWidth * scale)
    stage.height(sceneHeight * scale)
    stage.scale({ x: scale, y: scale })
  }
}
