import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f1f7ff',
          100: '#e2efff',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#0f172a',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
