import { defineConfig } from "vite"
import { resolve } from "path"
import { globSync } from 'glob'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [],
    root: resolve("."),
    base: "/static/",
    server: {
        host: "localhost",
        port: 3000,
        open: false,
    },
    resolve: {
        alias: {
          /* Must be equivalent to aliases in tsconfig.json */
          '@': resolve('.'),
        },
        resolve: {
            extensions: [".js", ".vue", ".json"],
        },
    },
    build: {
        outDir: "sfs/static/build",
        assetsDir: "",
        manifest: true,
        emptyOutDir: true,
        target: "es2017",
        rollupOptions: {
            input: Object.fromEntries(
                /* We define ALL the ts files as entries

                   Although some are just imported from other ts files
                   so do not need to be entries of their own.

                   What we *really* want is for it to look through the templates
                   and pull out uses of vite_asset tags. That seems plausible.

                   For prod build those entries get written to:
                     sfs/static/build/manifest.json

                   .. and vite_asset reads from there.

                   It *might* be that it's just fine loading them all
                   like this though :)

                 */
                globSync('templates/**/*.ts').map(filename =>
                    [filename, filename]
                )
            ),
            output: {
                chunkFileNames: undefined,
            },
        },
    },
});