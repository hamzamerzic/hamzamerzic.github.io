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

> **TL;DR.** I moved my eight-year-old WordPress-on-DigitalOcean robotics-tools site (mesh cleaner, model viewer, IKFast generator) to a containerized Cloud Run setup. About fifty people a month still use the tools, so the goal was preserving what works and future-proofing it, not rebuilding for its own sake.

During my master's in robotics, I built a few small tools for the parts of model and robot work I kept doing by hand: mesh cleanup, 3D model viewing, inverse-kinematics generation. I Dockerized them and exposed them via [WordPress](https://wordpress.org/) on [DigitalOcean](https://www.digitalocean.com/), originally as a way to tighten my own research loop, then opened up because a few other people seemed to want them.

Eight years later, the site was still running. To my surprise, over fifty people a month still used the tools. It was time to give the site some attention, without disrupting existing users.

What started as a cleanup became a migration to [Google Cloud Run](https://cloud.google.com/run). Each tool was already containerized and stateless, so the move was mostly mechanical: I split the services into separate Cloud Run deployments, cleaned up the code, and put a [budget guardrail](https://gist.github.com/hamzamerzic/8b834e56d2dc6a8f49bcb4047dd819df) in place that stops serving if my monthly budget is hit. The free tier on Cloud Run is generous enough that the tools should keep working for a long time without me touching them.

The original toolbox is still available, now as separate Cloud Run services with the same URLs.

Find the tools under [Projects](https://hamzamerzic.info/projects/):

- 🔧 [Mesh Cleaner](https://hamzamerzic.info/mesh_cleaner/)
  Clean and process 3D mesh files for physics-based simulations.
- 🧿 [Model Viewer](https://hamzamerzic.info/3d-viz/)
  Visualize 3D models and robots directly in your browser.
- 🤖 [IKFast Generator](https://hamzamerzic.info/ikfast/)
  Generate analytic inverse-kinematics solvers from `.dae` files using OpenRAVE’s IKFast.

These tools were the part of my master's I went back to constantly: computing inertial properties for dozens of objects, cleaning up meshes for simulations, and later, during my research assistantship, generating inverse-kinematics solvers for robot manipulators. Worth the time it took to package them properly back then.

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
