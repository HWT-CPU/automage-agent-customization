import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        focus: '0 0 0 1px rgba(56, 189, 248, 0.45), 0 0 0 8px rgba(56, 189, 248, 0.06)',
      },
    },
  },
  plugins: [],
} satisfies Config
