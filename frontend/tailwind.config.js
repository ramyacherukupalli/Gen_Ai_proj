/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        soft: "0 18px 45px -25px rgb(15 23 42 / 0.35)",
      },
    },
  },
  plugins: [],
};
