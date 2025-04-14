---
layout: post
title: "Migration Successful: Goodbye, WordPress!"
date: 2025-04-12 15:00:00
description: journey to modernize an old website
img: assets/img/old-page-landing.png
categories: general
giscus_comments: true
related_posts: false
---

Back in my robotics days, I built a few tools to make some of the tasks of creating, debugging, and simulating models for robotics a bit easier. These things are rarely smooth in robotics, but my philosophy has always been: if it’s painful to do once, try to do it only once.

So I Dockerized those tools and exposed them via a WordPress site hosted on [DigitalOcean](https://www.digitalocean.com/). It started as a way to make my research workflow easier, but I figured maybe others could benefit too.

Fast forward 8 years.

The site still works — and in hindsight, using Docker turned out to be a great decision. I was surprised to find that over 50 people a month still use these tools. (If you're one of them, say hi in the comments!)

I knew it was time to give the site some attention — but I didn’t want to break things for existing users.

What started as a quick cleanup turned into a GCP rabbit hole. I realized that since each tool was already containerized and stateless, they were a perfect fit for [Google Cloud Run](https://cloud.google.com/run). I cleaned up the code, split the services, and redeployed them on infrastructure that’s more stable, scalable, and free to run thanks to Cloud Run’s generous tier.

The original toolbox lives on — now cleaner, faster, and a bit more future-proof.

You can find the tools under [projects](https://hamzamerzic.info/projects/), running on modern infrastructure:

- 🔧 [Mesh Cleaner](https://hamzamerzic.info/mesh_cleaner/): Clean and process 3D mesh files for use in physics-based simulations.
- 🧿 [Model Viewer](https://hamzamerzic.info/3d-viz/): Visualize 3D models and robots directly in your browser.
- 🤖 [IKFast Generator](https://hamzamerzic.info/ikfast/): Generate analytic inverse kinematics solvers from `.dae` files using OpenRAVE’s IKFast.

These tools helped a lot during my master’s — especially computing inertial properties for dozens of objects, and cleaning up mesh models for use in simulations. Later, during my research assistantship at ETH, I used them again while working on inverse kinematics and robot manipulators. Having fast, reliable tools for that kind of work made a real difference.

If you're still using any of these today — thank you. I hope the migration went smoothly. And if not, feel free to reach out and let me know if something’s broken.

For nostalgia, I decided to keep a little album of what the old site looked like:

<style>
  .masonry-gallery {
    column-count: 2;
    column-gap: 1rem;
  }

  @media (min-width: 768px) {
    .masonry-gallery {
      column-count: 3;
    }
  }

  .masonry-gallery a {
    display: inline-block;
    margin-bottom: 1rem;
    width: 100%;
  }

  .masonry-gallery img {
    width: 100%;
    height: auto;
    border-radius: 0.5rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

<div id="oldSiteCarousel" class="carousel slide carousel-fade mb-4" data-bs-ride="carousel">
  <div class="carousel-inner">

    <div class="carousel-item active">
      <img src="{{ '/assets/img/old-site-blog.png' | relative_url }}" class="d-block w-100 rounded shadow-sm" alt="Old site blog">
    </div>

    <div class="carousel-item">
      <img src="{{ '/assets/img/old-site-home.png' | relative_url }}" class="d-block w-100 rounded shadow-sm" alt="Old site home">
    </div>

    <div class="carousel-item">
      <img src="{{ '/assets/img/old-site-tools.png' | relative_url }}" class="d-block w-100 rounded shadow-sm" alt="Old site tools">
    </div>

    <div class="carousel-item">
      <img src="{{ '/assets/img/old-site-mesh-cleaner.png' | relative_url }}" class="d-block w-100 rounded shadow-sm" alt="Old site mesh cleaner">
    </div>

    <div class="carousel-item">
      <img src="{{ '/assets/img/old-site-ikfast.png' | relative_url }}" class="d-block w-100 rounded shadow-sm" alt="Old site ikfast">
    </div>

  </div>

  <button class="carousel-control-prev" type="button" data-bs-target="#oldSiteCarousel" data-bs-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Previous</span>
  </button>

  <button class="carousel-control-next" type="button" data-bs-target="#oldSiteCarousel" data-bs-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Next</span>
  </button>
</div>

<div class="caption mt-2">
  A peek at the OG website. A little janky. A little beautiful.
</div>
