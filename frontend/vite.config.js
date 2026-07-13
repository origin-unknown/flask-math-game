import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/socket.io/': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
        ws: true,
      },
    }
  },
  plugins: [svelte()],
  build: {
    outDir: '../backend/src/static',
    emptyOutDir: true
  }
})
