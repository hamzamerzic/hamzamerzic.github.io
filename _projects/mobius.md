---
layout: page
title: Möbius
description: A self-hosted PWA where an AI agent builds the app it lives in
img: assets/img/moebius.png
permalink: /mobius/
importance: 1
category: software
---

<p>
  <strong>Möbius</strong> is a self-hosted PWA that starts as a chat
  interface and a blank canvas. You describe what you want — a news
  aggregator, a habit tracker, a 3D ISS viewer — and the agent inside
  builds it as a small app right inside the chat, without a page
  reload. Each app can store
  data, run on a schedule, fetch from the web, and use AI on its
  own. The agent can also change the platform itself: theme, layout,
  shell features.
</p>

<p>
  It runs in a single Docker container, installs to your phone like
  a native app, and your data stays on a server you control.
</p>

<p>
  Source, deploy buttons, and full docs live on GitHub.
</p>

<div class="row mt-4">
  <div class="col-sm">
    <a class="btn btn-outline-primary" href="https://github.com/hamzamerzic/mobius" target="_blank" rel="noopener">
      View on GitHub
    </a>
  </div>
</div>

<p class="mt-4">
  More on the design ideas and the self-improvement loop behind it
  in these blog posts:
</p>

<ul>
  <li><a href="{{ '/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }}">An app that builds itself</a></li>
  <li><a href="{{ '/blog/2026/the-self-improvement-harness/' | relative_url }}">The self-improvement harness behind it</a></li>
</ul>
