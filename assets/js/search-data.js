// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "publications",
          description: "publications by categories in reversed chronological order.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "post-the-self-improvement-harness-behind-möbius",
        
          title: "The self-improvement harness behind Möbius",
        
        description: "An outer agent talks to an inner agent and tries to make it more helpful. Notes on what we measured, what surprised us, and where the bottleneck moved to.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/the-self-improvement-harness/";
          
        },
      },{id: "post-an-agent-that-adapts-to-you",
        
          title: "An agent that adapts to you",
        
        description: "A personalized AI agent you can self-host. It builds the tools you need, edits the interface around them, and adapts both its functionality and its presentation to how you actually use it.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/mobius-an-app-that-builds-itself/";
          
        },
      },{id: "post-eeml-2025-wrap-up",
        
          title: "EEML 2025 wrap up!",
        
        description: "BTS on Eastern European Machine Learning Summer School in Sarajevo.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2025/eeml-wrap-up/";
          
        },
      },{id: "post-migration-successful",
        
          title: "Migration successful!",
        
        description: "Goodbye WordPress!",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2025/website-migration/";
          
        },
      },{id: "projects-model-viewer",
          title: 'Model Viewer',
          description: "Visualize 3D models and robots directly in your browser",
          section: "Projects",handler: () => {
              window.location.href = "/3d-viz/";
            },},{id: "projects-blox",
          title: 'Blox',
          description: "A small, functional neural network library for JAX — built to keep JAX&#39;s strengths visible instead of paper over them",
          section: "Projects",handler: () => {
              window.location.href = "/blox/";
            },},{id: "projects-ikfast-generator",
          title: 'IKFast Generator',
          description: "Generate analytic Inverse Kinematics solvers based on OpenRAVE&#39;s IKFast",
          section: "Projects",handler: () => {
              window.location.href = "/ikfast/";
            },},{id: "projects-mesh-cleaner",
          title: 'Mesh Cleaner',
          description: "Clean and process 3D mesh files for use in physics-based simulation environments",
          section: "Projects",handler: () => {
              window.location.href = "/mesh_cleaner/";
            },},{id: "projects-möbius",
          title: 'Möbius',
          description: "A personalized AI agent you self-host, which builds the tools you need and the interface they sit in",
          section: "Projects",handler: () => {
              window.location.href = "/mobius/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%68%61%6D%7A%61%6D%65%72%7A%69%63+%77%65%62%73%69%74%65@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/hamzamerzic", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=6QDwijAAAAAJ", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/hamzamerzic", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
