import { defineConfig, loadEnv } from 'vite';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');
  const assetBase = env.VITE_ASSET_BASE || '/static/dist/';
  const rootDir = path.resolve(__dirname, 'frontend');

  return {
    root: rootDir,
    base: assetBase,
    build: {
      outDir: path.resolve(__dirname, 'frontend/static/dist'),
      emptyOutDir: true,
      assetsDir: 'assets',
      manifest: true,
      rollupOptions: {
        input: path.resolve(rootDir, 'src/main.ts'),
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash][extname]'
        }
      }
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'frontend/src')
      }
    }
  };
});
