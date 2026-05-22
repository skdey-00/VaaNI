/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        banking: {
          50: '#eef8ff',
          100: '#d8eeff',
          200: '#b9e0ff',
          300: '#89cdff',
          400: '#52b0ff',
          500: '#2a8eff',
          600: '#1570f5',
          700: '#0d58e1',
          800: '#1148b6',
          900: '#143f8f',
          950: '#102857',
        },
        surface: {
          DEFAULT: '#18181b',
          raised: '#1f1f23',
          overlay: '#27272a',
          sunken: '#09090b',
        },
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'waveform': 'waveform 1s ease-in-out infinite',
      },
      keyframes: {
        waveform: {
          '0%, 100%': { transform: 'scaleY(0.5)' },
          '50%': { transform: 'scaleY(1)' },
        }
      }
    },
  },
  plugins: [],
}
