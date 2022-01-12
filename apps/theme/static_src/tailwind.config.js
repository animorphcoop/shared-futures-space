/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
const colors = require('tailwindcss/colors')

module.exports = {
    /**
     * Stylesheet generation mode.
     *
     * Set mode to "jit" if you want to generate your styles on-demand as you author your templates;
     * Set mode to "aot" if you want to generate the stylesheet in advance and purge later (aka legacy mode).
     */


    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',
        '../../../templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            colors: {
                transparent: 'transparent',
                current: 'currentColor',
                white: {
                    DEFAULT: '#FFFFFF',
                },
                morph: {
                    lightest: '#eaebff',
                    light: '#999EFF',
                    DEFAULT: '#4E56FF',
                },
                morphalt: {
                    DEFAULT: '#E0F3AA',
                    dark: '#A4B87E',
                },
                gray: {
                    lightest: '#DCDCDC',
                    light: '#9C9C9C',
                    DEFAULT: 'rgba(0, 0, 0, 0.5)', //#777777
                },
                black: {
                    DEFAULT: '#000000',
                },
                train: {
                    DEFAULT: '#F2D7C4', //#E0F3AA
                    dark: '#C69E82', //#A4B87E
                },
                build: {
                    DEFAULT: '#BAD3E1',
                    dark: '#829CAA',
                },
                heal: {
                    DEFAULT: '#AFDFD4',
                    dark: '#77A69B',
                },
                correct: '#228b22',
                incorrect:'#fe2712',
            },
            fontSize: {
                '26': ['1.3em', '1.25em'],
                '43': ['2.15em', '1.255em'],
            },
        },

        fontFamily: {
            'light': ['SofiaPro_Light', 'sans-serif'],
            'regular': ['SofiaPro_Regular', 'sans-serif'],
            'semibold': ['SofiaPro_SemiBold', 'sans-serif'],
        },

    },
    variants: {
        extend: {},
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
