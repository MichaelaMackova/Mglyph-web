import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

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
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
