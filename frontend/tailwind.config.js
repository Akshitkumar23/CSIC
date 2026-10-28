import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        institutional: {
          navy: '#14253D',
          navyDark: '#0B1624',
          navyLight: '#1B3252',
          blue: '#1D4ED8',
          blueHover: '#1E40AF',
          bg: '#F1F4F8',
          surface: '#FFFFFF',
          border: '#D8E0EA',
          textPrimary: '#101828',
          textSecondary: '#475467',
          verifiedGreen: '#027A48',
          verifiedBg: '#ECFDF3',
          verifiedBorder: '#A6F4C5',
          policyAmber: '#B54708',
          policyBg: '#FFFAEB',
          policyBorder: '#FEDF89',
        },
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#14253D',
        },
        navy: {
          800: '#1B3252',
          900: '#14253D',
          950: '#0B1624',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [typography],
}
