---
layout: post
title: Migration successful!
date: 2025-04-12 15:00:00
description: Goodbye WordPress!
thumbnail: assets/img/eagle-nebula.jpg
categories: general
giscus_comments: false
related_posts: false
---

Back in my master’s in robotics days, I built a few tools to simplify creating, debugging, and simulating models and robots. Robotics workflows are rarely smooth, but my philosophy has always been: if it’s painful to do once, try to do it only once.

So I Dockerized those tools and exposed them via [WordPress](https://wordpress.org/) on [DigitalOcean](https://www.digitalocean.com/). It began as a way to improve my research workflow, but soon I realized others might benefit too.

Fast forward eight years.

The site still works, and, to my surprise, over fifty people a month still use these tools.

I knew it was time to give the site some attention, but I didn’t want to disrupt existing users.

What started as a quick cleanup turned into a [Google Cloud](https://cloud.google.com/) rabbit hole. In hindsight, using Docker was a great decision back then. Since each tool was already containerized and stateless, they fit perfectly on [Google Cloud Run](https://cloud.google.com/run). I cleaned up the code, split the services, and redeployed them on infrastructure that’s more stable, scalable, and free under Cloud Run’s generous tier. To [protect my budget](https://gist.github.com/hamzamerzic/8b834e56d2dc6a8f49bcb4047dd819df), I also set up a guardrail that stops serving if my monthly budget is reached.

The original toolbox lives on, now cleaner, faster, and more future-proof.

Find the tools under [Projects](https://hamzamerzic.info/projects/):

- 🔧 [Mesh Cleaner](https://hamzamerzic.info/mesh_cleaner/)
  Clean and process 3D mesh files for physics-based simulations.
- 🧿 [Model Viewer](https://hamzamerzic.info/3d-viz/)
  Visualize 3D models and robots directly in your browser.
- 🤖 [IKFast Generator](https://hamzamerzic.info/ikfast/)
  Generate analytic inverse-kinematics solvers from `.dae` files using OpenRAVE’s IKFast.

These tools were invaluable during my master’s—especially computing inertial properties for dozens of objects and cleaning up meshes for simulations. Later, during my research assistantship, I relied on the tools for inverse-kinematics work on robot manipulators. Fast, reliable tools like these really made a difference.

If you’re still using any of these—thank you. I hope the migration went smoothly. If not, feel free to reach out and let me know what’s broken.

For nostalgia, here’s a little album of the old site:

<!-- Swiper styles -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />

<!-- Custom styling -->
<style>
  .swiper {
    max-width: 720px;
    margin: 2rem auto;
    border-radius: 0.75rem;
    overflow: hidden;
  }
  .swiper-slide img {
    width: 100%;
    height: auto;
    aspect-ratio: 4 / 3;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  }
  .swiper-button-prev,
  .swiper-button-next {
    color: var(--global-theme-color);
    opacity: 0.4;
    transition: opacity 0.3s ease;
  }
  .swiper-button-prev:hover,
  .swiper-button-next:hover {
    opacity: 1;
  }
  .swiper-pagination-bullet {
    background: var(--global-theme-color);
  }
</style>

<!-- Swiper container -->
<div class="swiper mySwiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <img src="{{ '/assets/img/old-site-blog.png' | relative_url }}" alt="Old site blog" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/old-site-home.png' | relative_url }}" alt="Old site home" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/old-site-tools.png' | relative_url }}" alt="Old site tools" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/old-site-mesh-cleaner.png' | relative_url }}" alt="Old site mesh cleaner" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/old-site-ikfast.png' | relative_url }}" alt="Old site ikfast" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<!-- Swiper script -->
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<script>
  const swiper = new Swiper('.mySwiper', {
    loop: true,
    autoplay: { delay: 5000, disableOnInteraction: false },
    spaceBetween: 16,
    pagination: { el: '.swiper-pagination', clickable: true },
    navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
  });
</script>

<div class="caption mt-2">
  A peek at the OG website.
</div>
