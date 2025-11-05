import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// TODO: delete?
// function crossOriginIsolationMiddleware(_ : any, res: any, next: any) {
//   //res.setHeader('Cross-Origin-Opener-Policy', 'same-origin-allow-popups');
//   //res.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
//   res.setHeader('Access-Control-Allow-Origin', '*');
//   res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
//   res.setHeader('Cross-Origin-Opener-Policy', 'same-origin-allow-popups');
//   res.setHeader('referrer-policy', 'strict-origin-when-cross-origin');
//   next();
// }

// const crossOriginIsolation = {
//   name: 'cross-origin-isolation',
//   configureServer: (server: any) => {
//     server.middlewares.use(crossOriginIsolationMiddleware);
//   },
//   configurePreviewServer: (server: any) => {
//     server.middlewares.use(crossOriginIsolationMiddleware);
//   },
// };

// https://vite.dev/config/
export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: 'static',
    sourcemap: true,  // Enable for debugging
    minify: 'esbuild', // Minify with esbuild
    // minify: 'terser', // Minify with Terser
    // terserOptions: {
    //   compress: {
    //     drop_console: true  // Remove console.logs in prod
    //   }
    // }
  },
  server: {
    watch: {
      usePolling: true,
    },
    host: '0.0.0.0',
    port: 5173,
  },
  plugins: [
    vue(),
    vueDevTools()
    // crossOriginIsolation
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
