---
layout: page
title: Möbius
description: A personalized AI agent you self-host, which builds the tools you need and the interface they sit in
img: assets/img/moebius.png
permalink: /mobius/
importance: 1
category: software
---

<style>
  .action-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin: 1.5rem 0 0.5rem;
  }
  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.15rem;
    font-size: 0.95em;
    font-weight: 500;
    line-height: 1.2;
    text-decoration: none !important;
    border-radius: 0.5rem;
    border: 1px solid transparent;
    transition: transform 0.15s ease, box-shadow 0.2s ease, background 0.2s ease;
  }
  .action-btn.primary {
    background: var(--global-theme-color);
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
  .action-btn.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.14);
    color: #fff !important;
  }
  .action-btn.ghost {
    background: transparent;
    color: var(--global-text-color) !important;
    border-color: rgba(127, 127, 127, 0.35);
  }
  .action-btn.ghost:hover {
    background: rgba(127, 127, 127, 0.08);
    border-color: var(--global-theme-color);
    color: var(--global-theme-color) !important;
    transform: translateY(-1px);
  }
  .action-btn i {
    font-size: 1.05em;
  }
</style>

<p class="lead">
  <strong>Möbius</strong> is a personalized AI agent you self-host.
  A chat on one side, a canvas on the other, and a coding agent
  inside that builds the tools you ask for as small apps right
  next to the chat (a news aggregator, a habit tracker, a 3D ISS
  viewer) without a page reload. Each app can store data, run on
  a schedule, fetch from the web, and use AI on its own. The same
  coding agent can also rewrite the interface itself: theme,
  layout, shell features.
</p>

<p class="mt-3 mb-4">
  It runs in a single Docker container, installs to your phone
  like a native app, and your data stays on a server you control.
</p>

<div class="row text-center my-4">
  <div class="col-md-6 mb-4">
    <figure>
      <video src="{{ '/assets/img/mobius/apps-cycle.mp4' | relative_url }}" width="240" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}" width="240" alt="Five apps Möbius has built in chat" />
      </video>
      <figcaption class="caption mt-2" style="font-size: 0.85em;">
        A few of the apps Möbius has built me in chat: an ISS
        tracker, a Brazil trip planner, a daily news digest, a
        Hacker News dashboard, an earthquake monitor, a habit
        tracker, and a drum machine.
      </figcaption>
    </figure>
  </div>
  <div class="col-md-6 mb-4">
    <figure>
      <video src="{{ '/assets/img/mobius/theme-cycle.mp4' | relative_url }}" width="240" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <img src="{{ '/assets/img/mobius/theme-00-baseline.png' | relative_url }}" width="240" alt="Möbius theme cycle" />
      </video>
      <figcaption class="caption mt-2" style="font-size: 0.85em;">
        Same instance, four prompts. The colors, fonts, and layout
        are CSS the agent wrote in response to a single sentence.
      </figcaption>
    </figure>
  </div>
</div>

<figure class="text-center my-4">
  <video src="{{ '/assets/img/mobius/theme-07-dynamic.mp4' | relative_url }}" width="240" autoplay loop muted playsinline poster="{{ '/assets/img/mobius/theme-07-dynamic-built.png' | relative_url }}" style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
    <img src="{{ '/assets/img/mobius/theme-07-dynamic-built.png' | relative_url }}" width="240" alt="Möbius dynamic theme in motion" />
  </video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    Motion works too: drifting bubbles, parallax silhouettes, and a slowly cycling warm-cool gradient, all added by the agent as part of the theme.
  </figcaption>
</figure>

<h3 class="mt-5">What you can do with it</h3>

<ul class="mt-3">
  <li><strong>Build apps from the chat.</strong> Describe what you want; the agent writes the code, mounts it, and you use it next to the conversation.</li>
  <li><strong>Install from an app store.</strong> A starter pack of apps you install by pasting a URL, update with a tap, and tweak by asking, all of it yours to keep.</li>
  <li><strong>Use them anywhere.</strong> Save an app to your home screen and run it standalone; it keeps working offline and syncs when you reconnect.</li>
  <li><strong>Reshape the shell.</strong> Themes, layout, navigation model, fonts, all editable by asking.</li>
  <li><strong>Pick your provider.</strong> Claude Code or Codex for the coding agent, Gemini for image generation. Toggle in settings.</li>
  <li><strong>Recover from anything.</strong> A <code>/recover</code> route resets the shell while keeping your chats, apps, and data.</li>
</ul>

<div class="action-row">
  <a class="action-btn primary" href="https://github.com/hamzamerzic/mobius" target="_blank" rel="noopener">
    <i class="fab fa-github"></i> View on GitHub
  </a>
  <a class="action-btn ghost" href="https://github.com/hamzamerzic/mobius#get-started" target="_blank" rel="noopener">
    <i class="fas fa-rocket"></i> Deploy in 3 minutes
  </a>
</div>

<hr class="my-5">

<h3>The story behind it</h3>

<p>
  More on the design ideas and the self-improvement loop behind
  Möbius in these companion posts:
</p>

<ul>
  <li><a href="{{ '/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }}"><strong>An agent that adapts to you</strong></a>: what Möbius is, and why an editable shell matters.</li>
  <li><a href="{{ '/blog/2026/the-self-improvement-harness/' | relative_url }}"><strong>The self-improvement harness behind it</strong></a>: how an outer agent makes the inner one progressively better at building.</li>
  <li><a href="{{ '/blog/2026/the-agent-is-the-kernel/' | relative_url }}"><strong>The agent is the kernel</strong></a>: the app store, updates and recovery, offline apps, and Möbius as an operating system you own.</li>
</ul>
