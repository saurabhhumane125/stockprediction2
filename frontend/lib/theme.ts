export const theme = {

  colors: {

    background: "#EDF1F5",

    surface: "#FFFFFF",

    surfaceSecondary: "#F7F9FC",

    text: "#11131A",

    textSecondary: "#5B6473",

    primary: "#0066FF",

    primaryHover: "#0057DB",

    accent: "#B4FF00",

    accentSecondary: "#C3D809",

    danger: "#FF3B3B",

    border: "#D7DEE7",

  },

  radius: {

    xs: "8px",

    sm: "12px",

    md: "16px",

    lg: "20px",

    xl: "28px",

    full: "999px",

  },

  shadow: {

    sm: "0 2px 8px rgba(17,19,26,.05)",

    md: "0 8px 22px rgba(17,19,26,.08)",

    lg: "0 20px 50px rgba(17,19,26,.12)",

  },

  spacing: {

    xs: "4px",

    sm: "8px",

    md: "16px",

    lg: "24px",

    xl: "32px",

    xxl: "48px",

  },

} as const;

export type Theme = typeof theme;