/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
import plugin from "tailwindcss/plugin.js"

import forms from "@tailwindcss/forms"
import typography from "@tailwindcss/typography"
import aspectRatio from "@tailwindcss/aspect-ratio"

export default {
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
        "./templates/**/*.html",
        "./apps/*/templates/**/*.html",

        /**
         * Typescript. Also process typescript files for dynamic classnames.
         */
        "./templates/**/*.ts",
        "./apps/*/templates/**/*.ts",

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your river structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the river. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your river structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            screens: {
                // Our definition of desktop
                // Ensure it's the same as defined in screen.ts
                desktop: '1024px',
            },
            colors: {
                transparent: "transparent",
                current: "currentColor",
                white: {
                    DEFAULT: "#FFFFFF",
                },
                grey: { // new, matching new Figma primitive colours
                    10: "#E5E5E5",
                    15: "#D9D9D9",
                    30: "#B2B2B2",
                    55: "#737373",
                    75: "#404040",
                },
                black: {
                    DEFAULT: "#000000",
                },
                purple: {
                    DEFAULT: "#9759FF",
                },
                turquoise: {
                    DEFAULT: "#79CBD0",
                },
                yellow: {
                    DEFAULT: "#FFFA8E",
                    light: "#FFFCC0",
                },
                red: {
                    DEFAULT: "#FF8686",
                    light: "#F2CACA",
                    focus: "#F66565",
                },
                blue: {
                    DEFAULT: "#CEDFF2",
                    light: "#E5F1F8",
                    blur: "#E5F1F880",
                },
                sky: {
                    DEFAULT: "#C4F5F8",
                    light: "#DFFFF6",
                },
                green: {
                    DEFAULT: "#C4F4E6",
                },
            },
            fontSize: {
                xxxs: ["0.5625rem", "0.75rem"],
                xxs: ["0.625rem", "0.625rem"],
                22: ["1.375rem", "1.75rem"],
            },
            spacing: {
                4.5: ["1.125rem"],
                7.5: ["1.875rem"],
            },
            boxShadow: {
                input: "0px 1px 1px 0px rgba(0, 0, 0, 0.15) inset",
                button: "1px 4px 6px 2px rgba(181, 181, 181, 0.22)",
                'map-detail': '7px 0px 6.5px 0px rgba(0, 0, 0, 0.25)',
            },
            backgroundImage: {
                "landing-enter": "linear-gradient(to bottom, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.4)), url('/static/images/landing/landing-temporary.png'), url('/static/images/landing/landing-temporary.png')",
                "north-belfast": "url('/static/images/landing/areas/northbelfast.jpg')",
                "east-belfast": "url('/static/images/landing/areas/eastbelfast.jpg')",
                "south-belfast": "url('/static/images/landing/areas/southbelfast.jpg')",
                "west-belfast": "url('/static/images/landing/areas/westbelfast.jpg')",
                "derrylondonderry": "url('/static/images/landing/areas/derrylondonderry.jpg')",
                "donegal": "url('/static/images/landing/areas/donegal.jpg')",
                "location": "url('/static/images/dashboard/location.png')",
            },
            opacity: {
                '55': '.55',
                '75': '.75',
            },
        },
        fontFamily: {
            "kanit-400": ["Kanit_Regular", "sans-serif"],
            "kanit-500": ["Kanit_Medium", "sans-serif"],
            "kanit-600": ["Kanit_SemiBold", "sans-serif"],
            "kanit-700": ["Kanit_Bold", "sans-serif"],
            "garamond-400": ["EB_Garamond_Regular", "serif"],
            "garamond-500": ["EB_Garamond_Medium", "serif"],
        },
    },
    safelist: [
        "h-3",
        "h-4",
        "h-5",
        "h-6",
        "h-7",
        "h-8",
        "h-7.5",
        "h-9",
        "bg-purple/25",
        "bg-north-belfast",
        "bg-east-belfast",
        "bg-south-belfast",
        "bg-west-belfast",
        "bg-derrylondonderry",
        "bg-donegal",
        "bg-location",
        "w-4.5",
        "w-7.5"
    ],
    variants: {
        extend: {},
    },
    plugins: [
        plugin(function ({addVariant}) {
            // Add a `third` variant, ie. `third:pb-0`
            addVariant("third-1", "&:nth-child(3n)");
            addVariant("third-2", "&:nth-child(3n+1)");
            addVariant("third-3", "&:nth-child(3n+2)");
            addVariant("borken", '&[borken="true"]');
        }),
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        forms,
        typography,
        aspectRatio,
    ],
};
