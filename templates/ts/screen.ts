/**
 * A "screen" object with useful properties on it.
 *
 * It will keep itself up to date with changes, although it has no way to
 * publish changes reactively.
 *
 * If reactivity is needed, could use https://alpinejs.dev/advanced/reactivity
 */

const matchMediaDesktop = window.matchMedia('(min-width: 1024px)');

const screen = {
    isDesktop: matchMediaDesktop.matches,
}

matchMediaDesktop.addEventListener('change', () => {
    screen.isDesktop = matchMediaDesktop.matches;
})
export default screen