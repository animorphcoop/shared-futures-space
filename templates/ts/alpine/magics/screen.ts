import Alpine from 'alpinejs';
import screen from '../../screen.ts';

/**
 * An alpine "magic" variable. Just the screen object...
 *
 * You can use it as $screen inside alpine directives, e.g.
 *
 *     <div x-data="{selected: $screen.isDesktop ? 1 : null}"></div>
 *
 * It's kept updated with resizes, but not reactive (i.e. it won't cause
 * the alpine directive to re-evaluate proactively).
 */
Alpine.magic('screen', () => {
    return screen;
})