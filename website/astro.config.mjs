// @ts-check
import { defineConfig, fontProviders } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  experimental: {
    // https://docs.astro.build/en/reference/experimental-flags/fonts/
    fonts: [
      {
        provider: fontProviders.google(),
        name: 'Bodoni Moda',
        cssVariable: '--font-bodoni-moda',
        weights: [400, 600, 700],
      }
    ]
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
