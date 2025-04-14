---
layout: post
title: Migration successful!
date: 2025-04-12 15:00:00
description: Goodbye Wordpress!
thumbnail: assets/img/old-site-blog.png
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
    border-radius: 0; /* Remove radius from inner images */
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  }

.swiper-button-prev {
    color: var(--global-theme-color);
}

.swiper-button-next {
    color: var(--global-theme-color);
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

  <!-- Navigation & pagination -->
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<!-- Swiper script -->
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

<script>
  const swiper = new Swiper('.mySwiper', {
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    spaceBetween: 16,
    pagination: {
      el: '.swiper-pagination',
      clickable: true,
    },
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
  });
</script>

<div class="caption mt-2">
  A peek at the OG website.
</div>
