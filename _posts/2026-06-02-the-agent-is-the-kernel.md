---
layout: post
title: The agent is the kernel
date: 2026-06-02 12:00:00
description: Möbius grew an app store. Install an app by pasting a URL, tweak it by asking, run it offline, save it to your home screen. The interesting part is not the store: it is what an editable, recoverable, single-owner operating system lets the agent do for you.
thumbnail: assets/img/mobius/covers/cover-post3.jpg
categories: software
keywords: self-hosted AI agent, AI agent that builds apps, AI app store, personal AI operating system, self-hosted PWA, agent-built mini-apps, Claude Code, Codex, Möbius
giscus_comments: true
related_posts: false
published: true
---

<details class="tldr">
<summary><strong>TL;DR.</strong> Möbius now has an app store: a handful of installable mini-apps, each a public git repo with a manifest. You install one by pasting a URL, tweak it by asking the agent, save it to your home screen, and use it offline. The store is the visible part; the point is an operating system you own and can reshape, where breaking something is cheap to undo because the system is built around recovery.</summary>

<ul>
<li><strong>The store</strong> is a curated starter pack, not a registry. A Möbius app is just a public repo with a <code>mobius.json</code> and an <code>index.jsx</code> entry point. Sharing one means sharing a URL.</li>
<li><strong>Updates</strong> are URL-keyed: bump the version upstream, the store shows "Update available", reinstalling patches the code and keeps your data.</li>
<li><strong>Recovery</strong> is the philosophy made concrete: atomic installs that cannot half-land, a <code>/recover</code> route, and a git history of your whole instance. Breaking is allowed because it is reversible.</li>
<li><strong>Offline + home screen.</strong> Apps install to your home screen as standalone PWAs and keep working with no network; writes queue and sync when you reconnect.</li>
<li><strong>The honest edges.</strong> Cross-app composition and per-app rollback are not built yet. I will say so where it matters.</li>
</ul>

</details>

This is the third post about [Möbius]({{ '/mobius/' | relative_url }}),
a personalized AI agent you self-host. The [first
post]({{ '/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }})
is about the agent building the tools you ask for and editing the
interface around them. The [second]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }})
is about the loop that makes it slowly better at doing that. This
one is about what happened when those apps stopped being one-offs
and grew a place to live.

Calling it an app store undersells it. The store is the surface you
tap; underneath it is a small operating system where the agent turns a
request into software, and the apps, the data, the shell, and the
rules are yours to keep, move, rewrite, or throw away.

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/os-hero.png' | relative_url }}"
       alt="The Möbius OS landing page: the headline 'The agent is the kernel.' over a description of a self-hosted PWA where mini-apps are installed, customized, and rebuilt from a single chat surface."
       loading="lazy" style="max-width:330px; width:100%; height:auto; border-radius:0.7rem;" />
  <figcaption class="caption mt-2">The framing, stated plainly on the project's own front page.</figcaption>
</figure>

## The agent is the kernel

In a normal operating system the kernel is the privileged core: it
owns the hardware, schedules the work, and everything you use runs on
top of it. Möbius keeps that shape and swaps the core. The privileged
thing in the middle is not a scheduler: it is the agent. You describe
what you want; it writes the app, installs it, schedules its
background jobs, and wires it into the shell. The apps are user space.
The chat is the system call.

<figure class="mb-diagram">
  <div class="mb-stack">
    <div class="mb-layer"><span class="mb-layer__name">Your apps</span><span class="mb-layer__role">user space · News, Gym, Visited, …</span></div>
    <div class="mb-layer"><span class="mb-layer__name">The shell</span><span class="mb-layer__role">chat · canvas · drawer · theme</span></div>
    <div class="mb-layer kernel"><span class="mb-layer__name">The agent</span><span class="mb-layer__role">turns a request into running software</span></div>
    <div class="mb-layer"><span class="mb-layer__name">Your server &amp; data</span><span class="mb-layer__role">one container · git history · storage</span></div>
  </div>
  <figcaption>The stack, with the agent where the kernel usually sits. The chat is the system call: you describe a thing, the agent builds it into the layer above, and it lands on the hardware you own at the bottom.</figcaption>
</figure>

That changes what the primitives are. An app is not a binary you
trust and cannot inspect; it is a single file of source the agent (or
you) can rewrite in place. An update is a new version of that file.
Installing is a transaction the platform can roll back. The rest of
this post is those primitives, one at a time, and where each is solid
versus still aspirational.

## The store is a starter pack, not a registry

The app store is itself a Möbius app. On first boot the platform
installs it through the exact same path you will use for everything
else: the first sign that there is no privileged install channel
hiding somewhere.

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/store-catalog.png' | relative_url }}"
       alt="The Möbius OS curated app catalog: cards for News, Visited, Gym, LaTeX, and Dreaming, each with an icon, version number, description, and capability badges such as 'Works offline' and 'Runs daily'."
       loading="lazy" style="max-width:340px; width:100%; height:auto; border-radius:0.7rem;" />
  <figcaption class="caption mt-2">The curated catalog: the same starter-pack apps the in-app store installs.</figcaption>
</figure>

What is in it today is a hand-picked set, not a gate you have to
pass:

<div class="table-wrap" markdown="1">

| App          | What it does                                                                                                                        |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **News**     | A daily AI-curated digest. A background job wakes at 10:00, runs the agent with web search only, and writes the morning's report.   |
| **Visited**  | A draggable 3D globe; tap the countries you have been to and the count climbs toward 195.                                           |
| **Gym**      | A training-program tracker: push/pull/legs, rest timer, a personal-record table, a heatmap. No agent, no cloud, all on your device. |
| **LaTeX**    | A math-first editor where an AI sub-agent writes `.tex` while you watch the typeset output render live.                             |
| **Dreaming** | A nightly job that reads yesterday's activity and writes you a one-page morning report, with a streak counter.                      |

</div>

Each of those is a public git repo in the [`mobius-os`](https://github.com/mobius-os)
organization, named `app-<something>`, with a `mobius.json` manifest,
an `index.jsx` entry point, and a 1024×1024 icon. The smallest apps
are that single file; larger ones pull in a few more, but the manifest
plus an entry point is the whole contract. There is no submission
queue, no review board, no registry to be blessed by. "Publishing" an
app means making a repo public and sharing the URL to its manifest.
The curated list above is a starter pack I picked; the install button
takes any manifest URL you paste, and the store warns, but does not
stop you, if it comes from a host it has not seen before.

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/app-repo.png' | relative_url }}"
       alt="The app-gym repository on GitHub: a flat list of files including mobius.json, index.jsx, and icon.png alongside a README and a couple of support files."
       loading="lazy" style="max-width:100%; height:auto;" />
  <figcaption class="caption mt-2">One app's repo. The manifest, the entry point, and the icon are the contract; everything else is the app's own code. Here the agent has been rebuilding the Gym tracker.</figcaption>
</figure>

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/app-gallery.jpg' | relative_url }}"
       alt="Three Möbius apps running on a phone, side by side: a habit tracker with streaks and weekly grids, a notes app with markdown and wikilinks, and a Snake game."
       loading="lazy" style="max-width:100%; height:auto; border-radius:0.5rem;" />
  <figcaption class="caption mt-2">Not mock-ups: three of the apps, running on a phone. A habit tracker, a markdown notebook, and a game, each a single public repo you install by pasting its URL.</figcaption>
</figure>

### What "install" actually does

When you tap Install, the work happens on the server, in one
transaction. The platform fetches the manifest (and because that URL
can point anywhere, it will not fetch into private networks or cloud
metadata endpoints, and it re-checks every redirect), then the app's
source, icon, background job if it has one, and any starter data it
ships. It compiles off to the side and promotes the result to "live"
only after the database row commits, so a half-written app is never
something you can open. If anything fails, the whole thing rolls back
and leaves nothing half-installed behind.

That all-or-nothing property is the foundation for the next two
sections: it is what lets an update patch your app in place, and it
is what lets recovery treat any break as something to undo.

## Updates: version bumps you can see, data you keep

An installed app remembers the URL it came from. That URL is its
identity: not its name, not a version number, the URL. The store
periodically checks each app's upstream manifest, and if the version
there is newer than yours, it shows an "Update available" pill.

Tapping Update reinstalls from the same URL. The backend switches into
update mode and patches the parts that should change (the code,
description, permissions, icon, schedule), then recompiles and
remounts. Your data is not in that list. **Starter data is only seeded
for keys that do not exist yet**, so an update can ship new defaults
without trampling your logged workouts, your visited countries, your
notes.

<figure class="mb-diagram">
  <div class="mb-flow">
    <div class="mb-node">
      <span class="mb-node__title">Upstream repo</span>
      <span class="mb-node__sub">a new version is pushed to <code>mobius.json</code></span>
    </div>
    <span class="mb-arrow">→</span>
    <div class="mb-node">
      <span class="mb-node__title">Update available</span>
      <span class="mb-node__sub">the store sees a newer version than yours</span>
    </div>
    <span class="mb-arrow">→</span>
    <div class="mb-node">
      <span class="mb-node__title">Reinstall, same URL</span>
      <span class="mb-node__tag">mode = update</span>
      <span class="mb-node__sub">matched by URL, not name or version</span>
    </div>
    <span class="mb-arrow">→</span>
    <div class="mb-node accent">
      <span class="mb-node__title">Code patched, data kept</span>
      <span class="mb-node__sub">new defaults seed only missing keys</span>
    </div>
  </div>
  <figcaption>An update is a reinstall from the same URL. The platform patches the source, description, permissions, icon, and schedule, and leaves the data you have created untouched.</figcaption>
</figure>

One sharp edge I would rather name than hide: if you ask the agent to
_customize_ an installed app and then tap Update, the update overwrites
those customizations. There is no three-way merge. For a single-owner
system that is a defensible default, but it is a real trade-off. The
direction I want is one git repo per installed app, so an update
becomes a merge that carries your edits forward and a conflict becomes
a chat where the agent resolves it. That is designed, not built.

## Recovery: breaking is allowed because it is reversible

An agent that can rewrite its own interface will eventually ship a CSS
rule that hides the composer or a layout change that buries the drawer.
The answer is not to wrap it in enough guardrails that it can never
make a mistake. The answer is to make mistakes cheap to undo. Recovery
has three layers:

- **A failed install cannot half-land.** The atomic transaction from
  earlier restores the previous working version of the app from a
  snapshot. You do not get a corrupted app; you get the old one back.
- **`/recover` is the bookmark you keep.** It is a route rendered by
  a separate, server-side codepath the agent does not edit. It resets
  the shell to its baseline while keeping your chats, apps, and data.
  If a theme paints text the same color as the background, that page
  still works, because it does not go through the shell at all.
- **Your whole instance is a git repo.** The agent commits the changes
  it makes to your shell, themes, app source, and schedules. When
  something breaks, the recovery path is the one a developer would use:
  read the log, find the change, restore it, except the agent does
  the reading.

<figure class="mb-diagram">
  <div class="mb-flow">
    <div class="mb-node">
      <span class="mb-node__tag">layer 1</span>
      <span class="mb-node__title">Atomic install</span>
      <span class="mb-node__sub">a broken update cannot half-land; the previous version is restored from a snapshot</span>
    </div>
    <div class="mb-node">
      <span class="mb-node__tag">layer 2</span>
      <span class="mb-node__title"><code>/recover</code></span>
      <span class="mb-node__sub">a server-side page the agent cannot edit; resets the shell, keeps chats, apps, and data</span>
    </div>
    <div class="mb-node">
      <span class="mb-node__tag">layer 3</span>
      <span class="mb-node__title">Your instance is a git repo</span>
      <span class="mb-node__sub">shell, themes, app source, schedules: the agent reads the log and restores</span>
    </div>
  </div>
  <figcaption>Three independent safety nets, not a single rollback button. Breaking is cheap to undo, so the agent does not have to be wrapped in guardrails that stop it from being useful.</figcaption>
</figure>

There is no one-click "roll back this app to last week's version"
button; recovery today is uninstall-and-reinstall, plus `/recover`,
plus the git history. So when an update breaks something, you tell the
agent what went wrong and it walks the commit log back to the working
version: the recovery path the third layer describes, run for you.

<blockquote class="pull-quote">
Recovery paths should make agent mistakes cheap to inspect and repair.
</blockquote>

## Your home screen, with or without Möbius

An app you install is not trapped inside the chat. Each one is also
served at its own address, with its own web manifest and icon, as a
standalone progressive web app. Add it to your phone's home screen and
it launches like any native app: full screen, no drawer, no chat. Gym
opens straight to today's workout; Visited opens to the globe.

Run standalone, an app has no Möbius shell around it to supply shared
libraries, so the standalone page vendors its own copy of React from
your own server. Nothing it needs lives on a CDN, which is exactly
what lets it render with the network off, the subject of the next
section.

## Offline, and the sync that catches up

This is the part I spent the most unglamorous engineering on, because
"works offline" is easy to claim and hard to actually land on a phone.

When an app is marked offline-capable, a service worker caches the
shell and the app's code, so opening it with the network off still
renders the real app, not the browser's offline page. And storage
works offline for _every_ app, not just the offline-capable ones:
reads come instantly from a local cache and refresh in the background,
and writes you make offline queue in a local outbox and sync to your
server the moment you reconnect.

<figure class="mb-diagram">
  <div class="mb-flow">
    <div class="mb-node">
      <span class="mb-node__title">Offline</span>
      <span class="mb-node__sub">app + storage served from a local cache; the real app renders with no network</span>
    </div>
    <span class="mb-arrow">→</span>
    <div class="mb-node">
      <span class="mb-node__title">You make changes</span>
      <span class="mb-node__sub">writes land in a local outbox; reads reflect them immediately</span>
    </div>
    <span class="mb-arrow">↻<span class="mb-arrow__label">reconnect</span></span>
    <div class="mb-node accent">
      <span class="mb-node__title">Synced</span>
      <span class="mb-node__sub">the outbox drains to your server; last-write-wins per item</span>
    </div>
  </div>
  <figcaption>Log a set in airplane mode, mark a country from a plane, jot a note on the subway: the outbox catches up the moment you reconnect. Listing and chat deliberately stay online.</figcaption>
</figure>

So your own data survives a dead connection. A couple of operations
stay online by design (a cached _listing_ could resurrect things you
deleted, and chat is online-only), and conflicts are last-write-wins
per item, which is right for a single owner and needs more thought for
a shared one. But the common case works, and I have checked it on a
real phone, not a desktop pretending to be one.

## Tweaking an app, and the composition I have not built

**Tweaking an app you have is real and easy.** Open it, tell the agent
what you want different (a darker palette, a new column, a weekly view
instead of daily), and it edits the app's source in place and
recompiles. No fork button, no project to set up; the app is one file,
and the agent edits that file the same way it would write a new one. It
is the same loop as building from scratch, pointed at something that
already exists.

**Composing several apps into a new one is not a feature yet.** The
idea is a health dashboard that reads across your workout tracker,
calorie log, gratitude journal, and dream diary and surfaces the
metrics you actually care about. The substrate exists: an app can
declare that it reads another app's data, and the backend enforces the
handshake on both sides. But almost nothing uses it today, each app's
storage is scoped to itself by default, and there is no "build me an
app that unifies these" flow. The foundation is there; the feature is
not. When I build it, this is the example I will build it against.

<figure class="mb-diagram">
  <div class="mb-lanes">
    <div class="mb-lanes__sources">
      <div class="mb-node"><span class="mb-node__title">Gym</span><span class="mb-node__sub">workouts, PRs</span></div>
      <div class="mb-node"><span class="mb-node__title">Calories</span><span class="mb-node__sub">intake</span></div>
      <div class="mb-node"><span class="mb-node__title">Gratitude</span><span class="mb-node__sub">daily notes</span></div>
      <div class="mb-node"><span class="mb-node__title">Dreaming</span><span class="mb-node__sub">sleep, streaks</span></div>
    </div>
    <div class="mb-lanes__join">⟶</div>
    <div class="mb-node ghost">
      <span class="mb-badge">not built yet</span>
      <span class="mb-node__title">Health dashboard</span>
      <span class="mb-node__sub">reads across your apps and surfaces the metrics you care about</span>
    </div>
  </div>
  <figcaption>The composition I want and have not built. The dashed box is a promise, not a feature.</figcaption>
</figure>

## Building a good one, in practice

Two things made the difference when the goal is for the agent to build
apps _well_, not just build them.

The first is the introspection loop from the [companion post on the
harness]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}):
have the agent build one app, ask it _why_ it made the choices it did
while the transcript is still in front of it, and fold the answer back
into its system prompt. Iterating the instructions is the lever, and
introspection is how I find the edit worth making.

The second is the design phase, where I do not let one model decide
alone. I drive with Claude and use the [Codex
plugin](https://github.com/openai/codex) to adversarially review the
design before the build starts. Two models disagreeing about an
interface, a data model, or an edge case surfaces the questions a
single model tends to skip; the build is cheap, so the leverage is in
the design.

<figure class="mb-diagram">
  <div class="mb-lanes mb-lanes--pair">
    <div class="mb-lanes__sources">
      <div class="mb-node accent">
        <div class="mb-node__head">
          <svg class="agent-mark agent-mark--claude" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><g>
            <line x1="19.60" y1="16.00" x2="29.20" y2="16.00"/>
            <line x1="19.12" y1="17.80" x2="24.49" y2="20.90"/>
            <line x1="17.80" y1="19.12" x2="22.60" y2="27.43"/>
            <line x1="16.00" y1="19.60" x2="16.00" y2="25.80"/>
            <line x1="14.20" y1="19.12" x2="9.40" y2="27.43"/>
            <line x1="12.88" y1="17.80" x2="7.51" y2="20.90"/>
            <line x1="12.40" y1="16.00" x2="2.80" y2="16.00"/>
            <line x1="12.88" y1="14.20" x2="7.51" y2="11.10"/>
            <line x1="14.20" y1="12.88" x2="9.40" y2="4.57"/>
            <line x1="16.00" y1="12.40" x2="16.00" y2="6.20"/>
            <line x1="17.80" y1="12.88" x2="22.60" y2="4.57"/>
            <line x1="19.12" y1="14.20" x2="24.49" y2="11.10"/>
          </g></svg>
          <span class="mb-node__title">Claude · the driver</span>
        </div>
        <span class="mb-node__sub">proposes the design and writes the code, holding the whole plan in view</span>
      </div>
      <div class="mb-node">
        <div class="mb-node__head">
          <svg class="agent-mark agent-mark--codex" viewBox="0 0 14 14" fill="currentColor" aria-hidden="true"><path d="M10.931 3.34a.112.112 0 0 0-.069-.104l-.038-.007c-1.537.05-2.45.318-3.714 1.002v6.683c.48-.248.936-.44 1.414-.58.695-.203 1.417-.292 2.303-.305l.038-.008a.113.113 0 0 0 .066-.104V3.341ZM2.363 9.919c0 .064.051.11.105.111l.33.008c1.162.046 2.042.243 2.975.662-.403-.585-1.008-1.075-1.654-1.292a.991.991 0 0 1-.674-.941v-5.14a6.36 6.36 0 0 0-.59-.076l-.37-.02a.115.115 0 0 0-.122.111v6.577Zm9.455-.001a.998.998 0 0 1-.877.992l-.101.007c-.832.012-1.47.095-2.066.27-.599.174-1.176.448-1.883.863a.444.444 0 0 1-.449 0c-1.299-.763-2.229-1.07-3.689-1.125l-.299-.008a.997.997 0 0 1-.977-.998V3.342c0-.573.478-1.017 1.038-.999l.417.023c.188.015.35.037.513.062v-.754c0-.708.749-1.244 1.429-.903.984.492 1.836 1.449 2.15 2.505 1.216-.617 2.222-.884 3.771-.934l.105.003a.998.998 0 0 1 .918.996v6.576ZM4.332 8.466c0 .049.03.087.07.1l.24.091a4.319 4.319 0 0 1 1.581 1.176V3.721c-.164-.803-.799-1.617-1.584-2.07l-.162-.088c-.025-.012-.054-.013-.088.009a.12.12 0 0 0-.057.102v6.792Z"/></svg>
          <span class="mb-node__title">Codex · the second opinion</span>
        </div>
        <span class="mb-node__sub">ensembles alternatives and reviews adversarially: where does this break?</span>
      </div>
    </div>
    <div class="mb-lanes__join">⇄<div style="font-family:var(--global-font-mono);font-size:0.64rem;color:var(--global-text-color-light);margin-top:0.25rem;line-height:1.3">propose&nbsp;⇄&nbsp;refute,<br>a few rounds</div></div>
    <div class="mb-node accent">
      <span class="mb-node__title">A design that survived the critique</span>
      <span class="mb-node__sub">what's left once the disagreements are resolved, then the harness validates it in real use</span>
    </div>
  </div>
  <figcaption>How a good app gets designed, in practice: drive with Claude, pressure-test with Codex. The two argue across a few rounds; the design that comes out the other side is the one worth building, and the same introspection loop validates it once it ships.</figcaption>
</figure>

## The philosophy under all of it

**Code empowers the agent; it does not police it.** When the agent
needs to install an app, write to your shell, or schedule a job, the
platform's job is to make that _possible and reversible_, not to
second-guess it. Validators show up only where a failure would be
silent and catastrophic; everywhere else the lever is a clear contract
and a good recovery path, not a wall.

**Low floor, high ceiling, no walls.** A personal tracker that stores
a little data and works offline should take one sentence; the storage
primitive is a convenience, not a cage, and an app that wants its own
local database is free to reach for one. The one real wall right now
is that apps cannot open arbitrary network connections to outside
services: a deliberate security line I have not yet built a careful
door through.

**You own all of it.** Your data is on a server you control. Your apps
are files you can read. Your shell is a git repo you can revert.
Nothing here is tuned to keep you engaged; the whole series has been an
argument for the opposite: an assistant that builds you the thing,
gets out of the way, and leaves you holding something you can keep.

## Where this goes

An app store was the obvious next thing once the agent could build
apps reliably. The less obvious thing is what it turns Möbius into: a
place where the unit of software is small enough for the agent to
write, own, and repair, where installing and breaking are reversible,
and where the privileged core can turn "I wish I had a thing that…"
into a thing that is there the next time you open your phone.

The apps above are a starter pack; the interesting ones do not exist
yet. If you [deploy an instance]({{ '/mobius/' | relative_url }}) and
build something, or tear one of these apart and rebuild it as
something better, that is exactly the point, and I would love to see
it.

The source is on [GitHub](https://github.com/hamzamerzic/mobius), the
app repos are under [`mobius-os`](https://github.com/mobius-os), and the
deploy button gets you a working instance in about three minutes.
