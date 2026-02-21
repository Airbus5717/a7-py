import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/a7-py/',
  server: {
    fs: {
      allow: [path.resolve(__dirname, '..')],
    },
  },
})
