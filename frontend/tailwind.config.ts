import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        theme: {
          surface: "var(--theme-surface, #ffffff)",
          elevated: "var(--theme-surface-elevated, #f4f4f5)",
          muted: "var(--theme-surface-muted, #e4e4e7)",
          text: "var(--theme-text-primary, #09090b)",
          textMuted: "var(--theme-text-muted, #71717a)",
          primary: "var(--theme-primary, #18181b)",
          primaryForeground: "var(--theme-primary-foreground, #ffffff)",
          accent: "var(--theme-accent, #71717a)",
          border: "var(--theme-border, #e4e4e7)",
          veg: "var(--theme-dietary-veg, #16a34a)",
          nonVeg: "var(--theme-dietary-nonveg, #dc2626)",
          egg: "var(--theme-dietary-egg, #d97706)",
        },
      },
      fontFamily: {
        heading: ["var(--theme-font-heading, sans-serif)"],
        body: ["var(--theme-font-body, sans-serif)"],
        price: ["var(--theme-font-price, monospace)"],
      },
      borderRadius: {
        theme: "var(--theme-radius, 0.5rem)",
      },
    },
  },
  plugins: [],
};
export default config;
