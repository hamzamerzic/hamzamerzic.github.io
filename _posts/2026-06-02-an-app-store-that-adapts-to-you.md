---
layout: post
title: An app store that adapts to you
date: 2026-06-02 12:00:00
description: Möbius grew an app store. Install an app by pasting a URL, tweak it by asking, run it offline, save it to your home screen. The interesting part is not the store but that the agent does not build isolated apps, it grows a cross-app personal system that adapts to you over time.
thumbnail: assets/img/mobius/covers/cover-post3.jpg
thumbnail_2x: assets/img/mobius/covers/cover-post3-2x.jpg
categories: software
keywords: self-hosted AI agent, AI agent that builds apps, AI app store, personal AI operating system, self-hosted PWA, agent-built mini-apps, Claude Code, Codex, Möbius
giscus_comments: true
related_posts: false
published: true
---

<details class="tldr">
<summary><strong>TL;DR.</strong> Möbius grew an app store, and the store is the on-ramp. The real point is that the agent does not build isolated apps, it grows a cross-app personal system that adapts to you. Apps share a storage layer and a permission model, so the agent can compose them and reshape the whole thing around you over time. You install by pasting a URL, tweak by asking, run offline, save to your home screen, and break things cheaply because the system is built around recovery.</summary>

<ul>
<li><strong>The store</strong> is a curated starter pack, not a registry. A Möbius app is a public repo with a <code>mobius.json</code> and an <code>index.jsx</code> entry point. Sharing one means sharing a URL.</li>
<li><strong>The bigger idea</strong> is a system, not a pile of apps. Shared storage and a shared permission model let the agent compose your apps and grow them around you.</li>
<li><strong>Updates</strong> are URL-keyed. Bump the version upstream, the store shows "Update available", reinstalling patches the code and keeps your data.</li>
<li><strong>Recovery</strong> makes breaking cheap. Atomic installs that cannot half-land, a <code>/recover</code> route, and a git history of your whole instance.</li>
<li><strong>Offline plus home screen.</strong> Apps install to your home screen as standalone PWAs and keep working with no network. Writes queue and sync when you reconnect.</li>
<li><strong>The honest edges.</strong> The full cross-app compose flow and per-app rollback are not built yet, and I say so where it matters.</li>
</ul>

</details>

This is the third post about [Möbius]({{ '/mobius/' | relative_url }}),
a personalized AI agent you self-host. The [first
post]({{ '/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }})
is about the agent building the tools you ask for and editing the
interface around them. The [second]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }})
is about the loop the developers use to make the agent better at building them. This
one is about what those apps became once they stopped being one-offs and grew a place to live.

The through-line is that Möbius has one job, to be as useful to you as it can. This post hands you the same reshaping power, with an app store as the on-ramp.

The store is the small idea. The bigger one is that the agent does not build isolated apps. It grows a cross-app personal system that adapts to you. Your apps share a storage layer and a permission model, so the agent can compose them and reshape the whole thing around you over time. The store is how it starts. The agent living across all your apps is the point.

The primitives that make this work are small on purpose. An app is not a binary you trust and cannot inspect; it is a single file of source the agent (or you) can rewrite in place. An update is a new version of that file. Installing is a transaction the platform can roll back. The rest of this post walks those primitives one at a time, and marks where each is solid versus where it is still a plan.

## The store is a starter pack, not a registry

The app store is itself a Möbius app. On first boot the platform installs it through the exact same path you use for everything else, the first sign there is no privileged install channel hiding somewhere.

<figure class="mb-diagram">
  <div class="mb-catalog">
    <div class="mb-app">
      <img class="mb-app__icon" src="{{ '/assets/img/mobius/app-icons/news.png' | relative_url }}" alt="News app icon" loading="lazy" />
      <div class="mb-app__body">
        <div class="mb-app__head">
          <span class="mb-app__name">News</span>
          <span class="mb-node__tag">runs daily</span>
        </div>
        <span class="mb-app__desc">An AI-curated morning digest, written for you by a background job at 10:00.</span>
      </div>
    </div>
    <div class="mb-app">
      <img class="mb-app__icon" src="{{ '/assets/img/mobius/app-icons/gym.png' | relative_url }}" alt="Workout app icon" loading="lazy" />
      <div class="mb-app__body">
        <div class="mb-app__head">
          <span class="mb-app__name">Workout</span>
          <span class="mb-node__tag">on-device</span>
        </div>
        <span class="mb-app__desc">A natural-language workout logger. Type "3×5 deadlift at 100kg" and it parses the sets, all on your device.</span>
      </div>
    </div>
    <div class="mb-app">
      <img class="mb-app__icon" src="{{ '/assets/img/mobius/app-icons/atlas.png' | relative_url }}" alt="Atlas app icon" loading="lazy" />
      <div class="mb-app__body">
        <div class="mb-app__head">
          <span class="mb-app__name">Atlas</span>
          <span class="mb-node__tag">offline</span>
        </div>
        <span class="mb-app__desc">A draggable 3D globe; tap the countries you have been to and watch the count climb toward 195.</span>
      </div>
    </div>
    <div class="mb-app">
      <img class="mb-app__icon" src="{{ '/assets/img/mobius/app-icons/mind.png' | relative_url }}" alt="Memory app icon" loading="lazy" />
      <div class="mb-app__body">
        <div class="mb-app__head">
          <span class="mb-app__name">Memory</span>
          <span class="mb-node__tag">memory</span>
        </div>
        <span class="mb-app__desc">An Obsidian-style graph of everything the agent has learned, every interaction and lesson, made browsable.</span>
      </div>
    </div>
    <div class="mb-app">
      <img class="mb-app__icon" src="{{ '/assets/img/mobius/app-icons/latex.png' | relative_url }}" alt="LaTeX app icon" loading="lazy" />
      <div class="mb-app__body">
        <div class="mb-app__head">
          <span class="mb-app__name">LaTeX</span>
          <span class="mb-node__tag">AI</span>
        </div>
        <span class="mb-app__desc">An Overleaf-style editor with a file drawer and a real tectonic engine, where an AI sub-agent writes <code>.tex</code> as you watch it typeset.</span>
      </div>
    </div>
    <div class="mb-app">
      <img class="mb-app__icon" src="{{ '/assets/img/mobius/app-icons/dreaming.png' | relative_url }}" alt="Reflection app icon" loading="lazy" />
      <div class="mb-app__body">
        <div class="mb-app__head">
          <span class="mb-app__name">Reflection</span>
          <span class="mb-node__tag">nightly</span>
        </div>
        <span class="mb-app__desc">Overnight, Möbius reviews the day's work and leaves a one-page morning brief.</span>
      </div>
    </div>
  </div>
  <figcaption>The curated catalog, the starter-pack apps the in-app store installs.</figcaption>
</figure>

What is in it today is a hand-picked set, not a gate you have to
pass:

<div class="table-wrap" markdown="1">

| App          | What it does                                                                                                                                        |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **News**     | A daily AI-curated digest. A background job wakes at 10:00, runs the agent with web search only, and writes the morning's report.                   |
| **Workout**  | A natural-language workout logger. Type what you did, like "3×5 deadlift at 100kg", and it parses the sets. No agent, no cloud, all on your device. |
| **Atlas**    | A draggable 3D globe; tap the countries you have been to and the count climbs toward 195.                                                           |
| **Memory**   | An Obsidian-style graph of everything the agent has learned, every interaction and lesson, made browsable.                                          |
| **LaTeX**    | An Overleaf-style editor with a file drawer and a real tectonic engine; an AI sub-agent writes `.tex` while you watch it typeset.                   |
| **Reflection** | Overnight, the agent reviews the day's work and leaves a one-page morning brief, so it starts the next day a little sharper.                       |

</div>

Each of those is a public git repo in the [`mobius-os`](https://github.com/mobius-os) organization, named `app-<something>`, with a `mobius.json` manifest, an `index.jsx` entry point, and a 1024×1024 icon. The smallest apps are that single file; larger ones pull in a few more, but the manifest plus an entry point is the whole contract. There is no submission queue and no registry to be blessed by. "Publishing" an app means making a repo public and sharing its manifest URL. The list above is a starter pack I picked. The install button takes any manifest URL you paste, and the store warns, but does not stop you, when it comes from a host it has not seen before.

<figure class="mb-diagram">
  <div class="mb-stack mb-files">
    <div class="mb-layer kernel">
      <span class="mb-layer__name"><code>index.jsx</code></span>
      <span class="mb-layer__role">the app itself, one React component the agent wrote</span>
    </div>
    <div class="mb-layer">
      <span class="mb-layer__name"><code>mobius.json</code></span>
      <span class="mb-layer__role">the manifest: name, version, what it may reach</span>
    </div>
    <div class="mb-layer">
      <span class="mb-layer__name"><code>icon.png</code></span>
      <span class="mb-layer__role">a 1024×1024 icon</span>
    </div>
    <div class="mb-layer ghost">
      <span class="mb-layer__name"><code>job.js</code><span class="mb-badge">optional</span></span>
      <span class="mb-layer__role">a background job, if the app has one</span>
    </div>
  </div>
  <figcaption>What an app is, in full. One component, a manifest, an icon, an optional job. No build config, no server, no framework to learn; make the repo public and its URL is installable.</figcaption>
</figure>

### What "install" actually does

When you tap Install, the work happens on the server in one transaction. The platform fetches the manifest (because that URL can point anywhere, it refuses private networks and cloud metadata endpoints and re-checks every redirect), then the app's source, icon, background job, and any starter data it ships. It compiles off to the side and goes live only after the database row commits, so a half-written app is never something you can open. If anything fails, the whole thing rolls back and leaves nothing behind.

That all-or-nothing property is the foundation for the next two sections. It lets an update patch your app in place, and it lets recovery treat any break as something to undo.

## Updates: version bumps you can see, data you keep

An installed app remembers the URL it came from, and that URL is its identity. Not its name, not a version number, the URL. The store periodically checks each app's upstream manifest, and when the version there is newer than yours it shows an "Update available" pill.

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

One sharp edge is worth naming. If you ask the agent to _customize_ an installed app and then tap Update, the update overwrites those customizations; there is no three-way merge. For a single-owner system that is a defensible default and a real trade-off. The direction I want is one git repo per installed app, so an update becomes a merge that carries your edits forward and a conflict becomes a chat where the agent resolves it. Designed, not built.

## Recovery: breaking is allowed because it is reversible

An agent that can rewrite its own interface will eventually ship a CSS rule that hides the composer or a layout change that buries the drawer. The answer is not to wrap it in guardrails so it can never slip. The answer is to make mistakes cheap to undo. Recovery has three layers:

- **A failed install cannot half-land.** The atomic transaction from
  earlier restores the previous working version of the app from a
  snapshot.
- **`/recover` is the bookmark you keep.** It is a route rendered by
  a separate, server-side path the agent does not edit. It resets
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
      <span class="mb-node__sub">shell, themes, app source, schedules, where the agent reads the log and restores</span>
    </div>
  </div>
  <figcaption>Three independent safety nets, not a single rollback button. Breaking is cheap to undo, so the agent does not have to be wrapped in guardrails that stop it from being useful.</figcaption>
</figure>

There is no one-click "roll back this app to last week's version" button yet. Recovery today is uninstall-and-reinstall, plus `/recover`, plus the git history. When an update breaks something, you tell the agent what went wrong and it walks the commit log back to the working version, the third layer run for you.

<blockquote class="pull-quote">
Recovery paths should make agent mistakes cheap to inspect and repair.
</blockquote>

## Your home screen, with or without Möbius

An app you install is not trapped inside the chat. Each one is also served at its own address, with its own web manifest and icon, as a standalone progressive web app. Add it to your phone's home screen and it launches like any native app: full screen, no drawer, no chat. Workout opens straight to today's session; Atlas opens to the globe.

Run standalone, an app has no Möbius shell around it to supply shared libraries, so the page vendors its own copy of React from your server. Nothing it needs lives on a CDN, which is what lets it render with the network off, the subject of the next section.

## Offline, and the sync that catches up

"Works offline" is easy to claim and hard to land on a phone, so this is the part that got the most unglamorous engineering, and it holds.

When an app is marked offline-capable, a service worker caches the shell and the app's code, so opening it with the network off renders the real app, not the browser's offline page. Storage works offline for _every_ app, not just the offline-capable ones. Reads come instantly from a local cache and refresh in the background; writes you make offline queue in a local outbox and sync the moment you reconnect.

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
  <figcaption>Log a set in airplane mode, mark a country from a plane, jot a note on the subway. The outbox catches up the moment you reconnect. Listing and chat deliberately stay online.</figcaption>
</figure>

Your data survives a dead connection, and I have checked it on a real phone, not a desktop pretending to be one. Two operations stay online by design (a cached _listing_ could resurrect things you deleted, and chat is online-only). Conflicts are last-write-wins per item, which is right for a single owner and needs more thought for a shared one.

## One system, not a pile of apps

Here is where the store stops being the point. Once your apps share a storage layer and a permission model, the agent is not stuck building each one in isolation. It can reach across them, compose them, and grow the whole thing around how you actually live.

**Tweaking an app you have is real and easy.** Open it, tell the agent what you want different (a darker palette, a new column, a weekly view instead of daily), and it edits the app's source in place and recompiles. No fork button, no project to set up; the app is one file, and the agent edits that file the same way it would write a new one.

**Composing several apps into a new one is the next rung, and the full flow is not built yet.** The idea is a health dashboard that reads across your workout tracker, calorie log, gratitude journal, and dream diary and surfaces the metrics you actually care about. The substrate exists. An app can declare that it reads another app's data, and the backend enforces the handshake on both sides. But almost nothing uses it today, each app's storage is scoped to itself by default, and there is no "build me an app that unifies these" flow. When I build it, this is the example I will build it against.

<figure class="mb-diagram">
  <div class="mb-lanes">
    <div class="mb-lanes__sources">
      <div class="mb-node"><span class="mb-node__title">Gym</span><span class="mb-node__sub">workouts, PRs</span></div>
      <div class="mb-node"><span class="mb-node__title">Calories</span><span class="mb-node__sub">intake</span></div>
      <div class="mb-node"><span class="mb-node__title">Gratitude</span><span class="mb-node__sub">daily notes</span></div>
      <div class="mb-node"><span class="mb-node__title">Sleep</span><span class="mb-node__sub">sleep, streaks</span></div>
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

What actually drives this adaptation are the two apps I have barely touched here, Memory and Reflection. Memory is what the agent has learned across every interaction and lesson, not a profile of you but a record of what works. Reflection is the overnight job that reviews the day's work and feeds new lessons back in. Together they are how the agent gets sharper at fitting your system to you over time. They get their own post, [your agent improves itself]({{ '/blog/2026/your-agent-improves-itself/' | relative_url }}).

## Building a good one, in practice

Two things make the difference when the goal is for the agent to build apps _well_, not just build them.

The first is the introspection loop from the [companion post on the harness]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}). Have the agent build one app, ask it _why_ it made the choices it did while the transcript is still in front of it, and fold the answer back into its system prompt. Iterating the instructions is the lever, and introspection is how I find the edit worth making.

The second is the design phase, where I do not let one model decide alone. I drive with Claude and use the [Codex plugin](https://github.com/openai/codex) to adversarially review the design before the build starts. Two models disagreeing about an interface, a data model, or an edge case surface the questions a single model skips. The build is cheap, so the leverage is in the design.

<figure class="mb-diagram">
  <div class="mb-lanes mb-lanes--pair">
    <div class="mb-lanes__sources">
      <div class="mb-node accent">
        <div class="mb-node__head">
          <span class="agent-mark agent-mark--claude" aria-hidden="true"></span>
          <span class="mb-node__title">Claude · the driver</span>
        </div>
        <span class="mb-node__sub">proposes the design and writes the code, holding the whole plan in view</span>
      </div>
      <div class="mb-node">
        <div class="mb-node__head">
          <span class="agent-mark agent-mark--codex" aria-hidden="true"></span>
          <span class="mb-node__title">Codex · the second opinion</span>
        </div>
        <span class="mb-node__sub">ensembles alternatives and reviews adversarially, asking where this breaks</span>
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

**Code empowers the agent; it does not police it.** When the agent needs to install an app, write to your shell, or schedule a job, the platform's job is to make that _possible and reversible_, not to second-guess it. Validators show up only where a failure would be silent and catastrophic; everywhere else the lever is a clear contract and a good recovery path, not a wall.

**Low floor, high ceiling, no walls.** A personal tracker that stores a little data and works offline should take one sentence, and an app that wants its own local database is free to reach for one. The one real wall right now is that apps cannot open arbitrary network connections to outside services, a deliberate security line I have not yet built a careful door through.

**You own all of it.** Your data is on a server you control. Your apps are files you can read. Your shell is a git repo you can revert. Nothing here is tuned to keep you engaged. The whole series has argued the opposite, an assistant whose one job is to be useful, that builds you the thing, gets out of the way, and leaves you holding something you can keep.

## Where this goes

An app store was the obvious next thing once the agent could build apps reliably. The less obvious thing is what it turns Möbius into. A system where the unit of software is small enough for the agent to write, own, and repair, where installing and breaking are reversible, and where the agent turns "I wish I had a thing that…" into a thing that is there the next time you open your phone, then keeps reshaping it around you.

The apps above are a starter pack; the interesting ones do not exist yet. If you [deploy an instance]({{ '/mobius/' | relative_url }}) and build something, or tear one of these apart and rebuild it as something better, that is exactly the point, and I would love to see it.

The source is on [GitHub](https://github.com/mobius-os/mobius), the
app repos are under [`mobius-os`](https://github.com/mobius-os), and the
deploy button gets you a working instance in about three minutes.
