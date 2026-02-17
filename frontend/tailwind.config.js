/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        medical: {
          primary: "#0F766E",
          "primary-light": "#14B8A6",
          secondary: "#1E40AF",
          "secondary-light": "#3B82F6",
        },
        severity: {
          critical: "#DC2626",
          high: "#EA580C",
          medium: "#F59E0B",
          low: "#3B82F6",
        },
        success: "#16A34A",
      },
    },
  },
  plugins: [],
};
