import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // In dev mode, proxy all backend routes so the frontend at :5173 can
    // reach the FastAPI server at :8000 without CORS issues and without
    // hardcoding the backend URL.
    proxy: {
      '/api':        'http://localhost:8000',
      '/generate':   'http://localhost:8000',
      '/education':  'http://localhost:8000',
      '/workspace':  'http://localhost:8000',
      '/download':   'http://localhost:8000',
      '/health':     'http://localhost:8000',
    },
  },
  build: {
    outDir: 'dist',
  },
})
