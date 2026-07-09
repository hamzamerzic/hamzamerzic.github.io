---
layout: post
title: An app store that adapts to you
date: 2026-06-02 12:00:00
description: Möbius grew an app store. Install an app by pasting a URL, tweak it by asking, run it offline, save it to your home screen. The store is the on-ramp; the bigger shift is the agent growing a cross-app personal system that adapts to you over time.
thumbnail: assets/img/mobius/covers/cover-post3.jpg
thumbnail_2x: assets/img/mobius/covers/cover-post3-2x.jpg
categories: software
keywords: self-hosted AI agent, AI agent that builds apps, AI app store, personal AI operating system, self-hosted PWA, agent-built mini-apps, Claude Code, Codex, Möbius
giscus_comments: true
related_posts: false
published: true
---

<details class="tldr">
<summary><strong>TL;DR.</strong> Möbius grew an app store, and the store is the on-ramp. The bigger idea is that the agent grows a cross-app personal system around you, rather than a heap of one-off apps. Apps share a storage layer and a permission model, so the agent can compose them and reshape the whole thing around you over time. You install by pasting a URL, tweak by asking, run offline, save to your home screen, and break things cheaply because the system is built around recovery.</summary>

<ul>
<li><strong>The store</strong> is a curated starter pack rather than an open registry. A published app is a public repo with a <code>mobius.json</code> and an <code>index.jsx</code> entry point, and sharing one means sharing a URL.</li>
<li><strong>The bigger idea</strong> is one connected system. Shared storage and a shared permission model let the agent compose your apps and grow them around you.</li>
<li><strong>Updates</strong> are URL-keyed and three-way merged. Bump the version upstream, the store shows "Update available", and reinstalling merges the new code with any tweaks you made and keeps your data; on a real conflict the old version keeps running while the agent resolves it with you.</li>
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

Across the series, Möbius is built around one goal, being genuinely useful to you. The app store gives that goal an on-ramp. Because your apps share a storage layer and a permission model, the agent can compose them and reshape the whole system around how you actually live.

The primitives that make this work are small on purpose. You can inspect the source. The smallest app is one source file and a small manifest the agent (or you) can rewrite in place; larger apps add only a few more files. An update is a new version of those files. Installing is a transaction the platform can roll back. Some of those pieces are solid; others are still plans.

## The store starts as a starter pack

The app store is itself a Möbius app. On first boot the platform installs it through the exact same path you use for everything else, which keeps the install channel the same for the store and every other app.

<figure class="mb-diagram mb-diagram--image">
  <img class="mb-diagram__image" src="{{ '/assets/img/mobius/os/batteries-included.png' | relative_url }}" alt="The Möbius App Store Browse tab showing Skills, Tasks, Contribute, Notes, News, Memory, Reflection, and Editor installed in the starter catalog." loading="lazy" />
  <figcaption>The Batteries included starter catalog inside Möbius: system apps, everyday apps, and agent-facing tools all install through the same App Store path.</figcaption>
</figure>

Today it is a hand-picked set. You can install from outside it:

<div class="table-wrap" markdown="1">

| App            | What it does                                                                                                                  |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Skills**     | Browse and search the agent's installed skills and playbooks, so the system can explain what it knows how to do.              |
| **Tasks**      | See scheduled check-ins at a glance and keep background agent work visible instead of mysterious.                              |
| **Contribute** | Review GitHub-backed changes the agent has proposed upstream, with a path from local improvement to shared app work.           |
| **Notes**      | Markdown notes that render as you type, with checklists and durable local storage.                                             |
| **News**       | A daily AI-curated digest. A background job runs the agent with web search and writes the morning's report.                    |
| **Memory**     | A browsable graph of what Möbius has learned over time, the lessons worth keeping, and the connections between them.           |
| **Reflection** | Overnight, the agent reviews the day's work and leaves a one-page morning brief, so it starts the next day a little sharper.   |
| **Editor**     | Browse and edit files on your Möbius, with an agent-aware path into changing the system itself.                               |

</div>

Each of those is a public git repo in the [`mobius-os`](https://github.com/mobius-os) organization, named `app-<something>`, with a `mobius.json` manifest, an `index.jsx` entry point, and a 1024×1024 icon. The smallest apps are that single file; larger ones pull in a few more, but the manifest plus an entry point is the whole contract. An app the agent builds just for your own instance needs none of this; the manifest only matters once you want to publish one. Publishing means making a repo public and sharing its manifest URL. The list above is a starter pack I picked. The install button takes any manifest URL you paste, and the store warns and lets you continue when it comes from a host it has not seen before.

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

When you tap Install, the work happens on the server in one transaction. The platform fetches the manifest (because that URL can point anywhere, it refuses private networks and cloud metadata endpoints and re-checks every redirect), then the app's source, icon, background job, and any starter data it ships. It compiles off to the side and goes live only after the database row commits, so only a complete app can open. If anything fails, the whole thing rolls back and leaves nothing behind.

That all-or-nothing property lets an update patch your app in place, and it lets recovery treat any break as something to undo.

## Updates keep your data

An installed app remembers the URL it came from, and that URL is its identity. The name and version can change; the URL is what ties your copy to upstream. The store periodically checks each app's upstream manifest, and when the version there is newer than yours it shows an "Update available" pill.

Tapping Update reinstalls from the same URL. The backend switches into
update mode and patches the parts that should change (the code,
description, permissions, icon, schedule), then recompiles and
remounts. Your data stays out of that patch. **Starter data only seeds
missing keys**, so an update can ship new defaults without trampling
your logged workouts, your visited countries, your notes.

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

I am glad I built this part. Each installed app is its own git repo, so an update runs as a three-way merge. It avoids the blunt overwrite path. If the upstream author ships a new version and you have asked the agent to customize your copy, the merge carries your edits forward. When the two genuinely collide, your old version keeps running while the agent opens a chat to work the conflict through with you, so a bad merge leaves your working app alone. The smarter merge is still ahead, the one that reconciles by intent instead of by lines of text. The plumbing it would run on is already here.

## Recovery makes breaking cheap

Recovery works the way it does in the [first post]({{ '/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }}). The `/recover` page renders outside the shell so it loads even when the shell is broken, and your whole instance is a git repo the agent can walk back when you tell it what went wrong. The store adds one fallback of its own. Installs are atomic, so a failed or broken update lands fully or rolls back; the previous working version is restored from a snapshot, and a deleted app can be reinstalled from the same URL and come back with its data. A one-click "roll this app back to last week" button still needs building, so recovery today uses reinstall, `/recover`, and that git history.

## Your home screen works with or without Möbius

An app you install also lives outside the chat. Each one is served at its own address, with its own web manifest and icon, as a standalone progressive web app. Add it to your phone's home screen and it launches like any native app, full screen and without the drawer or chat. Workout opens straight to today's session; Atlas opens to the globe.

Run standalone, an app vendors its own copy of React from your server because it runs without the Möbius shell that normally supplies shared libraries. Everything it needs comes from your server, which lets it render with the network off.

## Offline work catches up

"Works offline" is easy to claim and hard to land on a phone. This part got the most unglamorous engineering, and it holds.

When an app is marked offline-capable, a service worker caches the shell and the app's code, so opening it with the network off renders the real app. Storage works offline for _every_ app, including ones without the offline-capable marker. Reads come instantly from a local cache and refresh in the background; writes you make offline queue in a local outbox and sync the moment you reconnect.

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

Your data survives a dead connection, and I have checked it on a real phone after the usual desktop-pretending-to-be-a-phone pass. Two operations stay online by design (a cached _listing_ could resurrect things you deleted, and chat is online-only). Conflicts are last-write-wins per item, which is right for a single owner and needs more thought for a shared one.

## One system made from small apps

Once your apps share a storage layer and a permission model, the agent can build across them. It can pull data from one app into another and build new tools on top of both.

**Tweaking an app you have is real and easy.** Open it, tell the agent what you want different (a darker palette, a new column, a weekly view instead of daily), and it edits the app's source in place and recompiles. You skip the fork button and project setup; the app is one file, and the agent edits that file the same way it would write a new one.

**Composing several apps into a new one is the next rung, and I still have to build the full flow.** The idea is a health dashboard that reads across your workout tracker, calorie log, gratitude journal, and dream diary, then surfaces the metrics you actually care about. The backend already has the pieces. An app can declare that it reads another app's data, and the backend enforces the handshake on both sides. But almost nothing uses it today, each app's storage is scoped to itself by default, and the product still lacks a "build me an app that unifies these" flow. When I build it, this is the example I will build it against.

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
  <figcaption>The composition I want and have not built yet. The dashed box marks the part that does not exist today.</figcaption>
</figure>

The two apps I have barely touched here, Memory and Reflection, drive most of this adaptation. Memory records the lessons worth keeping from what the agent has learned about how you work. It avoids profile-building and focuses on what works. Reflection is the overnight job that reviews the day's work and feeds new lessons back in. Together they are how the agent gets sharper at fitting your system to you over time. I cover them in [your agent improves itself]({{ '/blog/2026/your-agent-improves-itself/' | relative_url }}).

Building these apps _well_ leans on the same two levers as the rest of Möbius, both from the [harness post]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}). One is the introspection loop that tightens the agent's instructions. The other is a design phase where I drive with Claude and pressure-test with Codex before a line of the app is written, since the build is cheap and the leverage is in the design.

## Philosophy under all of it

**Code empowers the agent; policing is a last resort.** When the agent needs to install an app, write to your shell, or schedule a job, the platform's job is to make that _possible and reversible_, with second-guessing reserved for failures that would be silent and catastrophic. Validators show up only in those cases; everywhere else the lever is a clear contract and a good recovery path.

**Low floor, high ceiling.** A personal tracker that stores a little data and works offline should take one sentence, and an app that wants its own local database is free to reach for one. The one real wall right now blocks arbitrary network connections from apps to outside services, a deliberate security line I have not yet built a careful door through.

**You own all of it.** Your data is on a server you control. Your apps are files you can read. Your shell is a git repo you can revert. The system is tuned for usefulness. Engagement hacking is the wrong goal here. Across this series, I have been arguing for an assistant that builds the thing you asked for and then leaves you with software you actually own.

## After the starter pack

An app store was the obvious next thing once the agent could build apps reliably. With a store, Möbius becomes a system where the unit of software is small enough for the agent to write and repair, installing and breaking are reversible, and "I wish I had a thing that..." becomes a thing you can open on your phone.

The apps above are a starter pack; the interesting ones are still ahead. If you [deploy an instance]({{ '/mobius/' | relative_url }}) and build something, or tear one of these apart and rebuild it as something better, that is the use case I care about, and I would love to see it.

The source is on [GitHub](https://github.com/mobius-os/mobius), the
app repos are under [`mobius-os`](https://github.com/mobius-os), and the
deploy button gets you a working instance in about three minutes.
