---
layout: post
title: The agent is the kernel
date: 2026-06-02 12:00:00
description: Möbius grew an app store. Install an app by pasting a URL, tweak it by asking, run it offline, save it to your home screen. The interesting part is not the store — it is what an editable, recoverable, single-owner operating system lets the agent do for you.
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

The short version: Möbius has an app store now. The longer version
is that calling it a store undersells it. The store is the surface
you tap; underneath it is a small operating system where the agent
is the part that turns a request into a working thing, and almost
everything else — the apps, the data, the shell, the rules — is
yours to keep, move, rewrite, or throw away.

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/os-hero.png' | relative_url }}"
       alt="The Möbius OS landing page: the headline 'The agent is the kernel.' over a description of a self-hosted PWA where mini-apps are installed, customized, and rebuilt from a single chat surface."
       loading="lazy" style="max-width:330px; width:100%; height:auto; border-radius:0.7rem;" />
  <figcaption class="caption mt-2">The framing, stated plainly on the project's own front page.</figcaption>
</figure>

## The agent is the kernel

In a normal operating system the kernel is the privileged core: it
owns the hardware, schedules the work, and everything you actually
use runs on top of it. Möbius keeps that shape and swaps the core.
The privileged thing in the middle is not a scheduler — it is the
agent. You describe what you want; it can write the app, install it,
schedule its background jobs, and wire it into the shell. The apps
are user space. The chat is the system call.

<figure class="mb-diagram">
  <div class="mb-stack">
    <div class="mb-layer"><span class="mb-layer__name">Your apps</span><span class="mb-layer__role">user space · News, Gym, Visited, …</span></div>
    <div class="mb-layer"><span class="mb-layer__name">The shell</span><span class="mb-layer__role">chat · canvas · drawer · theme</span></div>
    <div class="mb-layer kernel"><span class="mb-layer__name">The agent</span><span class="mb-layer__role">turns a request into running software</span></div>
    <div class="mb-layer"><span class="mb-layer__name">Your server &amp; data</span><span class="mb-layer__role">one container · git history · storage</span></div>
  </div>
  <figcaption>The stack, with the agent where the kernel usually sits. The chat is the system call: you describe a thing, the agent builds it into the layer above, and it lands on the hardware you own at the bottom.</figcaption>
</figure>

I do not mean this as a slogan. It changes what the primitives are.
An app is not a binary you trust and cannot inspect; it is a single
file of source the agent (or you) can read and rewrite in place. An
update is not an opaque package; it is a new version of that file.
Installing is not a permission you grant once and forget; it is a
transaction the platform can roll back. The rest of this post is
those primitives, one at a time, and where each one is solid versus
still aspirational.

## The store is a starter pack, not a registry

The app store is itself a Möbius app — it ships in the drawer of a
fresh install, because on first boot the platform installs it
through the exact same path you will use for everything else — the
first sign that there is no privileged install channel hiding
somewhere.

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/store-catalog.png' | relative_url }}"
       alt="The Möbius OS curated app catalog: cards for News, Visited, Gym, LaTeX, and Dreaming, each with an icon, version number, description, and capability badges such as 'Works offline' and 'Runs daily'."
       loading="lazy" style="max-width:340px; width:100%; height:auto; border-radius:0.7rem;" />
  <figcaption class="caption mt-2">The curated catalog — the same starter-pack apps the in-app store installs. Each card is generated from that app's manifest, so the version and description are always the live ones.</figcaption>
</figure>

What is in it today is a hand-picked set, not a gate you have to
pass:

<div class="table-wrap" markdown="1">

| App          | What it does                                                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| **News**     | A daily AI-curated digest. A background job wakes at 10:00, runs the agent with web search only, and writes the morning's report.    |
| **Visited**  | A draggable 3D globe; tap the countries you have been to and the count climbs toward 195.                                            |
| **Gym**      | A training-program tracker — push/pull/legs, rest timer, a personal-record table, a heatmap. No agent, no cloud, all on your device. |
| **LaTeX**    | A math-first editor where an AI sub-agent writes `.tex` while you watch the typeset output render live.                              |
| **Dreaming** | A nightly job that reads yesterday's activity and writes you a one-page morning report, with a streak counter.                       |

</div>

Each of those is a public git repo in the [`mobius-os`](https://github.com/mobius-os)
organization, named `app-<something>`, built around three things: a
`mobius.json` manifest, an `index.jsx` entry point, and a 1024×1024
icon. The smallest apps are that single file; larger ones pull in a
few more, but the manifest plus an entry is the whole contract.
There is no submission queue, no review board, no registry to be
blessed by. "Publishing" an app means making a repo public and
sharing the URL to its manifest. The curated list above is a starter
pack I picked; the install button will take any manifest URL you
paste, and the store warns — but does not stop you — if it comes from
a host it has not seen before.

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/app-repo.png' | relative_url }}"
       alt="The app-gym repository on GitHub: a flat list of files including mobius.json, index.jsx, and icon.png alongside a README and a couple of support files."
       loading="lazy" style="max-width:100%; height:auto;" />
  <figcaption class="caption mt-2">One app's repo. The manifest, the entry point, and the icon are the contract; everything else is the app's own code — here the agent has been rebuilding the Gym tracker.</figcaption>
</figure>

<figure class="text-center my-4">
  <img src="{{ '/assets/img/mobius/os/github-org.png' | relative_url }}"
       alt="The mobius-os GitHub organization page: one public repository per app — app-news, app-store, and others — each holding a manifest, a single index.jsx, and an icon."
       loading="lazy" style="max-width:100%; height:auto;" />
  <figcaption class="caption mt-2">The <a href="https://github.com/mobius-os">mobius-os</a> organization: one public repo per app. Publishing an app is making a repo public and sharing the URL to its manifest.</figcaption>
</figure>

### What "install" actually does

When you tap Install, the work happens on the server, in one
transaction. The platform fetches the manifest (with the
paranoid-but-boring protections you want when a URL can point
anywhere — no reaching into private networks or cloud metadata
endpoints, every redirect re-checked), then fetches the app's
source, its icon, its background job if it has one, and any starter
data it ships. It compiles the source off to the side, and only
promotes the compiled app to "live" after the database row commits —
so a half-written app is never something you can open. If anything
fails along the way, the whole thing rolls back and leaves nothing
half-installed behind.

That all-or-nothing property is not a detail. It is what lets the
rest of the system be relaxed about breaking, which is the next
two sections.

## Updates: version bumps you can see, data you keep

An installed app remembers the URL it came from. That URL is its
identity — not its name, not a version number, the URL. The store
periodically checks each app's upstream manifest, and if the version
there is newer than the one you have, it shows an "Update available"
pill.

Tapping Update reinstalls from the same URL. The backend recognizes
the app by that URL, switches into update mode, and patches the
parts that should change — the code, the description, the
permissions, the icon, the schedule — recompiles, and remounts. The
part that matters: **your data is not in that list.** Starter data
is only seeded for keys that do not exist yet, so an update can ship
new default content without trampling the entries you have created.
Your logged workouts, your visited countries, your notes survive the
update.

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
  <figcaption>An update is a reinstall from the same URL. The platform patches the source, description, permissions, icon, and schedule — and leaves the data you have created untouched.</figcaption>
</figure>

There is one sharp edge here and I would rather name it than hide
it. If you have asked the agent to _customize_ an installed app —
change its layout, add a field — and then you tap Update, the
update overwrites those customizations. There is no three-way merge.
For a single-owner system this is a defensible default: the upstream
is a CDN-backed file, the agent can re-apply your change in a
sentence, and your chat history is the version log. But it is a real
trade-off, and the direction I want to take it is to clone each app
as its own git repo so an update becomes a merge that carries your
edits forward, and a conflict becomes — what else — a chat where the
agent resolves it. That is designed, not built. I will not pretend
otherwise.

## Recovery: breaking is allowed because it is reversible

Möbius is built on a principle I keep coming back to: an agent that
can rewrite its own interface will eventually ship a CSS rule that
hides the composer or a layout change that buries the drawer. The
answer is not to wrap the agent in enough guardrails that it can
never make a mistake. The answer is to make mistakes cheap to undo.

There are a few layers of that, and it is worth being precise about
what each one is, because "recovery" can mean a lot of things:

- **A failed install cannot half-land.** The atomic transaction from
  earlier means a broken update restores the previous working
  version of the app from a snapshot. You do not get a corrupted app;
  you get the old one back.
- **`/recover` is the bookmark you keep.** It is a route rendered by
  a separate, server-side codepath the agent does not edit. It resets
  the shell to its baseline while keeping your chats, apps, and data.
  If a theme paints text the same color as the background, that page
  still works, because it does not go through the shell at all.
- **Your whole instance is a git repo.** The agent commits the
  changes it makes to your shell, themes, app source, and schedules.
  When something breaks, the recovery path is the same one a
  developer would use: read the log, find the change, restore it —
  except the agent does the reading.

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
      <span class="mb-node__sub">shell, themes, app source, schedules — the agent reads the log and restores</span>
    </div>
  </div>
  <figcaption>Three independent safety nets, not a single rollback button. Breaking is cheap to undo, so the agent does not have to be wrapped in guardrails that stop it from being useful.</figcaption>
</figure>

What this is _not_ is a one-click "roll back this app to last
week's version" button in the store. That does not exist. Recovery
today is uninstall-and-reinstall, plus `/recover`, plus the git
history — not a versioned rollback. If your update broke something,
the cleanest fix is to ask the agent to fix it, which is the whole
philosophy in one move: when a guardrail falls short, you do not add
a check, you invoke Möbius.

<blockquote class="pull-quote">
Recovery paths should make agent mistakes cheap to inspect and repair.
</blockquote>

## Your home screen, with or without Möbius

An app you install is not trapped inside the chat. Each one is also
served at its own address, with its own web manifest and icon, as a
standalone progressive web app. You can add it to your phone's home
screen and launch it like any native app — full screen, no drawer,
no chat, just the app. The Gym tracker opens straight to today's
workout. Visited opens straight to the globe.

That standalone shell vendors its own copy of React, served from
your own server, which is what makes the next section possible.

## Offline, and the sync that catches up

Offline-capable apps work with no network, and storage works offline
for every app. This is the part I spent the most unglamorous
engineering on, because "works offline" is easy to claim and hard to
actually land on a phone.

When an app is marked offline-capable, a service worker caches the
shell and the app's code, so opening it with the network off still
renders the real app — not the browser's offline page, not a blank
screen, but a branded "you are offline" panel at worst and the
working app at best. And storage works offline for _every_ app, not
just the offline-capable ones: reads come instantly from a local
cache and refresh in the background, and writes you make offline
queue in a local outbox and sync to your server the moment you
reconnect.

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
  <figcaption>Log a set in airplane mode, mark a country from a plane, jot a note on the subway — the outbox catches up the moment you reconnect. Listing and chat deliberately stay online.</figcaption>
</figure>

So you log a set at the gym in airplane mode, mark a country from a
plane, jot a note on the subway — and when you surface, it is all on
your server. The honest caveats: a couple of operations
deliberately stay online (a cached _listing_ could resurrect things
you deleted, and chat itself is online-only by design), and the
conflict rule is last-write-wins per item, which is right for a
single owner and would need more thought for a shared one. But the
common case — your own data, on your own devices, surviving a dead
connection — works, and I have checked it on a real phone rather
than a desktop pretending to be one.

## Tweaking an app, and the composition I have not built

Here is where I have to be careful, because this is the part it
would be easy to oversell.

**Tweaking an app you have is real and easy.** Open it, tell the
agent what you want different — a darker palette, a new column, a
weekly view instead of daily — and it edits the app's source in
place and recompiles. There is no fork button to find, no project to
set up; the app is one file and the agent owns the keyboard. This is
the same loop as building an app from scratch, pointed at something
that already exists.

**Composing several apps into a new one is not a feature yet.** The
fantasy — and it is a good one — is to take your workout tracker,
your calorie log, your gratitude journal, and your dream diary, and
ask for a health dashboard that reads across all four and surfaces
the metrics you actually care about. The substrate for this exists:
the platform has a permission model where an app can declare that it
reads another app's data, and the backend enforces the handshake on
both sides. But almost nothing uses it today, each app's storage is
scoped to itself by default, and there is no "build me an app that
unifies these" flow. So the truthful statement is: the foundation is
there, the feature is not. When I build it, this is the example I
will build it against.

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
  <figcaption>The composition I want and have not built. The permission substrate for one app to read another's data exists and is enforced; the flow that turns four apps into a unifying fifth does not. The dashed box is a promise, not a feature.</figcaption>
</figure>

## The philosophy under all of it

Three ideas hold this together, and they are worth stating plainly
because they are why the system has the shape it does.

**Code empowers the agent; it does not police it.** When the agent
needs to do something powerful — install an app, write to your
shell, schedule a job — the platform's job is to make that _possible
and reversible_, not to second-guess it. Validators and sanitizers
show up only where a failure would be silent and catastrophic.
Everywhere else, the lever is a clear contract and a good recovery
path, not a wall.

**Low floor, high ceiling, no walls.** The easy thing should be
trivial: a personal tracker that stores a little data and works
offline should take one sentence. The hard thing should be possible:
the storage primitive is a convenience, not a cage, and an app that
wants its own local database or storage layer is free to reach for
it. The one real wall right now is that apps cannot open arbitrary
network connections to outside services — a deliberate security line
I have not yet built a careful door through.

**You own all of it.** Your data is on a server you control. Your
apps are files you can read. Your shell is a git repo you can revert.
Nothing here is tuned to keep you engaged; the whole series has been
an argument for the opposite — an assistant that is most helpful when
it builds you the thing, gets out of the way, and leaves you holding
something you can keep.

## Where this goes

An app store was the obvious next thing once the agent could build
apps reliably. The less obvious thing is what it turns Möbius into: a
place where the unit of software is small enough for the agent to
write, own, and repair; where installing, updating, and breaking are
all reversible; and where the privileged core is the one part that
can turn "I wish I had a thing that…" into a thing that is there the
next time you open your phone.

The apps above are a starter pack. The interesting ones are the apps
that do not exist yet, because nobody has needed them yet. If you
[deploy an instance]({{ '/mobius/' | relative_url }}) and build
something — or tear one of these apart and rebuild it as something
better — that is exactly the point, and I would love to see it.

The source is on [GitHub](https://github.com/hamzamerzic/mobius), the
app repos are under the [`mobius-os`](https://github.com/mobius-os)
organization, and the deploy button gets you a working instance in
about three minutes.
