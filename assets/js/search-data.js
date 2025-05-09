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
        },{id: "post-migration-successful",
        
          title: "Migration Successful!",
        
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
