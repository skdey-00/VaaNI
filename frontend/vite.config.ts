import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
  define: {
    'import.meta.env.VITE_MOCK_MODE': JSON.stringify(process.env.VITE_MOCK_MODE || 'false'),
  },
})
