/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#007BFF',
        accent: '#2ECC71',
        navy: '#034078',
      },
    },
  },
  plugins: [],
}
