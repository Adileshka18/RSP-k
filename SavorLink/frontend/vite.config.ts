import path from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

const API_PROXY_PATHS = [
  '/auth',
  '/products',
  '/cart',
  '/orders',
  '/chats',
  '/enterprises',
  '/favorites',
  '/users',
  '/docs',
  '/openapi.json',
]

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8002'

  const proxy = Object.fromEntries(
    API_PROXY_PATHS.map((route) => [
      route,
      {
        target: proxyTarget,
        changeOrigin: true,
      },
    ]),
  )

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      strictPort: true,
      hmr: {
        host: '127.0.0.1',
        protocol: 'ws',
      },
      proxy,
    },
  }
})
