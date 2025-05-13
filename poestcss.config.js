const globAll = require("glob-all"); // Make sure glob-all is used if complex patterns are needed later

module.exports = {
  plugins: [
    require("autoprefixer"), // Adds vendor prefixes to CSS for better browser compatibility
    require("purgecss")({
      // Content files to scan for CSS classes
      content: globAll.sync(["_site/**/*.html", "_site/**/*.js"], { nodir: true }), // Ensure globAll is used like this

      // CSS files to process are specified in your package.json script,
      // so the 'css' option here is not strictly needed when using postcss-cli per file.
      // We can remove it to avoid confusion:
      // css: ["_site/assets/css/main.css", "_site/assets/css/bootstrap.min.css"],

      defaultExtractor: (content) => content.match(/[\w-/:]+(?<!:)/g) || [],
      safelist: {
        standard: [
          // Your existing standard safelist is good, keep it:
          /^bg-/,
          /^text-/,
          /^border-/,
          /^font-/,
          /^fa-/,
          /^fab-/,
          /^fas-/,
          /^far-/,
          /^layout-/,
          /^fixed-top-nav/,
          /^sticky-bottom-footer/, // Added this as it's a body class you use
          /^container(-fluid)?/, // Adjusted for container and container-fluid
          /^row/,
          /^col(-[a-z0-9-]*)?/, // Made col selector more general
          /^(.*?)\.(is-|has-)/,
          /^navbar(-[a-z0-9-]*)?/, // Made navbar selector more general
          /^nav(-[a-z0-9-]*)?/, // Made nav selector more general
          /^dropdown(-[a-z0-9-]*)?/, // Made dropdown selector more general
          /^badge(-[a-z0-9-]*)?/, // Made badge selector more general
          /^btn(-[a-z0-9-]*)?/, // Made btn selector more general
          /^alert(-[a-z0-9-]*)?/, // Made alert selector more general
          /^modal(-[a-z0-9-]*)?/, // Made modal selector more general
          /^tooltip/, // Keep tooltip related classes
          /^popover/, // Keep popover related classes
          /^carousel(-[a-z0-9-]*)?/, // Made carousel selector more general
          /\bcollapse\b/, // Using word boundary for 'collapse'
          /\bshow\b/, // Using word boundary for 'show'
          /\bactive\b/, // Using word boundary for 'active'
          /\bdisabled\b/, // Using word boundary for 'disabled'
          /^img-fluid$/,
          /^rounded(-[a-z0-9-]*)?/,
          /^z-depth-/,
          /^fixed-top$/,
          /^sticky-top$/,
          /^page-item$/,
          /^page-link$/,
          // Table related classes (also see 'deep' below)
          /^table(-[a-z0-9-]*)?/,
          /^thead-/,
          /^tbody-/,
          /^tfoot-/,
          // Highlight.js
          /^\.hljs(-[a-zA-Z0-9_]+)?/, // Adjusted hljs selector
          /^highlight$/,
          /^language-/,
          // Giscus & other specific components
          /^giscus/,
          /^copy-code-button/,
          // Al-folio specific from your about.liquid if needed and not covered
          /profile-wrapper/,
          /profile/,
          /image-wrapper/,
          /social/,
          /contact-icons/,
          /text-container/,
          /mobile-name/,
          /desktop-name/,
          // Bootstrap spacing utilities
          /^(m|p)(t|b|l|r|x|y)?-[0-5]$/,
          /^(m|p)(t|b|l|r|x|y)?-auto$/,
          // Dark mode classes
          /^dark/,
          /data-theme/,
          /data-theme-setting/,
        ],
        deep: [
          /^table/,
          /^tr/,
          /^td/,
          /^th/,
          /^thead/,
          /^tbody/,
          /^tfoot/, // Keep table element selectors
          /^carousel-item/, // Example for Bootstrap carousel inner items
        ],
        greedy: [
          /token$/, // Keep highlight.js token classes
          /tooltip/, // Greedily keep anything with 'tooltip' for dynamic content
          /popover/, // Greedily keep anything with 'popover'
        ],
        keyframes: [], // Add keyframe names here if PurgeCSS removes them
        variables: [/^--global-/], // Keep your CSS custom properties starting with --global-
      },
    }),
  ],
};
