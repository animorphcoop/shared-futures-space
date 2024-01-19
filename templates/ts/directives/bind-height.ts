import Alpine from "alpinejs";

Alpine.directive('bind-height', (
    el,
    { expression }, { evaluate, cleanup },
) => {

    const observer = new ResizeObserver(entries => {
        for (const entry of entries) {
            evaluate(`${expression} = ${entry.contentRect.height}`)
        }
    })

    observer.observe(el)

    cleanup(() => observer.disconnect())
})