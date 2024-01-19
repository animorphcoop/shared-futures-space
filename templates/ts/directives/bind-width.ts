import Alpine from "alpinejs";

Alpine.directive('bind-width', (
    el,
    { expression }, { evaluate, cleanup },
) => {

    const observer = new ResizeObserver(entries => {
        for (const entry of entries) {
            evaluate(`${expression} = ${entry.contentRect.width}`)
        }
    })

    observer.observe(el)

    cleanup(() => observer.disconnect())
})