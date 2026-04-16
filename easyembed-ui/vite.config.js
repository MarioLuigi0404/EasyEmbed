import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: { // Proxy API requests to the FastAPI backend to avoid CORS issues during development - change this when deploying to production!!
    proxy: {
      "/upload": "http://127.0.0.1:8000",
      "/status": "http://127.0.0.1:8000",
      "/files": "http://127.0.0.1:8000",
      "/media": "http://127.0.0.1:8000",
      "/login": "http://127.0.0.1:8000",
      "/me": "http://127.0.0.1:8000"
    }
  }
})
