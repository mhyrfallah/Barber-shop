/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./barbershop/templates/**/*.html",
    "./barbershop/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        night: {
          DEFAULT: "#1A2332",
          soft: "#243044",
          deep: "#121820",
        },
        cream: {
          DEFAULT: "#FAF7F2",
          deep: "#F0EBE3",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          soft: "#F8F5F0",
        },
        coral: {
          DEFAULT: "#E07A5F",
          deep: "#C8664D",
          light: "#F4A898",
        },
        sage: {
          mist: "rgba(61, 90, 128, 0.10)",
          DEFAULT: "#3D5A80",
          deep: "#2C4360",
        },
        amber: {
          DEFAULT: "#F2CC8F",
          deep: "#E8B86D",
        },
        ink: "#1E1B18",
        muted: "#6B635B",
        line: "rgba(30, 27, 24, 0.08)",
        blossom: "#F4A7B9",
      },
      fontFamily: {
        display: ["Shippori Mincho", "serif"],
        body: ["Noto Sans JP", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        soft: "0 4px 24px rgba(26, 35, 50, 0.08)",
        card: "0 8px 32px rgba(26, 35, 50, 0.10)",
        glow: "0 0 40px rgba(224, 122, 95, 0.25)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
