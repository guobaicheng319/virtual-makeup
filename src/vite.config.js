import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/uploads': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
    }
  },
  build: {
    outDir: '../public',
    emptyOutDir: false,
  }
})
