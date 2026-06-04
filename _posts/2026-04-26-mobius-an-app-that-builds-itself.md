---
layout: post
title: An agent that adapts to you
date: 2026-04-26 12:00:00
description: A personalized AI agent you can self-host. It builds the tools you need, edits the interface around them, and adapts both its functionality and its presentation to how you actually use it.
thumbnail: assets/img/mobius/covers/cover-post1.jpg
thumbnail_2x: assets/img/mobius/covers/cover-post1-2x.jpg
categories: software
giscus_comments: true
related_posts: false
published: true
---

<details class="tldr">
<summary><strong>TL;DR.</strong> Möbius is a personal AI agent you can self-host whose one job is to be as useful to you as it can. It actively helps by building the tools you ask for as small apps next to the chat, editing the interface they sit in, and learning from use while your data stays on a machine you control.</summary>

<ul>
<li><strong>The demo.</strong> Asked the agent for file upload and got the full pipeline (backend
route, message storage, drag-and-drop, image rendering) in one
conversation.</li>
<li><strong>Capabilities</strong> (file upload, notifications,
settings panels) are candidates for upstreaming so the next install
inherits them.</li>
<li><strong>Presentation</strong> (your theme, layout, fonts) lives
only on your volume and stays yours.</li>
<li><strong><code>/recover</code></strong> resets the shell when
the agent paints itself into a corner.</li>
<li>Source on <a href="https://github.com/mobius-os/mobius">GitHub</a>;
deploys in about three minutes.</li>
</ul>

</details>

## You grow it from a chat input

Möbius starts as almost nothing, a chat on one side and an empty
canvas on the other. No file upload, no scheduled jobs panel, no
notifications button. What makes that interesting is that the agent can rewrite the
thing it runs inside. So you grow it. Ask for file upload and it
builds file upload. Ask for a new look and it restyles itself. Ask for
an app and one appears on the canvas. The shell you end up with is the
one you talked into being.

Here is one of those moments, end to end. I sent a deliberately
ordinary prompt. _"I'd like to send files and images along with my
messages, pictures of stuff I want to talk about, the occasional
document. Can you add file upload to the chat?"_ One conversation
later there was a backend route, message storage, drag-and-drop, and
image rendering, none of which existed when I asked.

## The flip side: you can break it

The same power cuts both ways. Tell the agent to delete an app and it
deletes it. Tell it to rip out a feature and the feature is gone. You
can repaint the shell until the composer is hidden, restructure the
navigation until the drawer is unreachable, paint yourself into a
corner. That is not a flaw. It is the point. An interface you can
grow in any direction is, by construction, an interface you can also
break.

What makes that safe is that breaking is cheap to undo. `/recover`
bounds the blast radius. It resets the shell to its seeded baseline
while keeping your chats, your apps, and your data. It renders from a
separate server-side codepath the agent does not edit, so it survives
even a shell rewrite that hides everything else. Grow in any
direction, break it, recover, try again. The goal is maximal
personalization, software that bends to you instead of the other way
around.

## Why I built this

Most software asks you to adapt to it. AI assistants make this worse
with time: preferences leak between tasks, memory accumulates in the
wrong places, the thing that was helpful yesterday becomes an
invisible constraint today. The model in front of you is usually
capable of writing the tool you want, but the product around it can
only talk about the tool. You ask for a workflow and get advice. You
describe a tool and get a mockup, a snippet, or a plan. The
assistant stays on one side of the glass.

The premise of Möbius is to put it on the other side, to shorten the
distance between wanting, making, using, and correcting until they
happen in one place. Requests become software, software becomes
context, the next request lands somewhere sharper. The platform has
to be editable for that to work. If the agent can only talk about
the work, you still have to carry the system in your head.

The name is from Möbius strips. Each app the agent builds does not
sit somewhere external; it lands in the shell the chat lives in, and
becomes part of the surface the next conversation happens on. The
shell the chat runs in was, once, written by a different version of
the same chat.

## How it works

The most obvious adaptive surface is the apps the agent builds. The
interesting surface is everything around them, and it splits along a
useful axis: **capabilities** (general features like file upload or
notifications, candidates for upstreaming so the next install
inherits them) and **presentation** (your theme, layout, fonts,
which live only on your volume and stay yours). The harness treats
those two stacks differently.

### Capabilities: the part that grows the platform

Walk through that file-upload chat from the top. The order is the
point.

<figure class="shot-row shot-row--flow">
  <div class="shot">
    <img src="{{ '/assets/img/mobius/upload-02a-pristine.png' | relative_url }}"
         alt="Top of the chat just after sending the prompt. The agent's reply: 'Before I propose anything, let me check a couple of things, I want to know what's actually possible before committing to an approach.' Then a stack of tool calls reading chats.py, chats_stream.py, and ChatView.jsx."
         loading="lazy" />
    <span class="shot__label">ask for file upload</span>
  </div>
  <span class="shot-arrow" aria-hidden="true">→</span>
  <div class="shot">
    <img src="{{ '/assets/img/mobius/upload-02b-answered.png' | relative_url }}"
         alt="Question cards. The agent's plan: 'No existing attachments pipeline. The build is: backend endpoint, schema extension, agent-side hook, paperclip + previews UI.' Then three forks: FILE TYPES (Images + documents), AFFORDANCES (Paperclip + Paste + Drag-and-drop), SIZE LIMIT (20 MB)."
         loading="lazy" />
    <span class="shot__label">answer a few questions</span>
  </div>
  <span class="shot-arrow" aria-hidden="true">→</span>
  <div class="shot">
    <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}"
         alt="The feature in use end to end: my user bubble showing the Möbius logo attached inline, with the text 'Here is the Möbius logo. Tell me what you see.' The agent reads off the symbolism: 'a human and an AI collaborating on a shared canvas, neither one fully upstream of the other.'"
         loading="lazy" />
    <span class="shot__label">file upload, working</span>
  </div>
</figure>

<div class="caption mt-2">
  The build starts from an empty composer. The agent checks the
  codebase, surfaces three real decisions (file types, affordances,
  size cap), then writes the endpoint, the schema, the picker, and the
  paperclip, none of which existed when I asked. By the end of the same
  chat I attach the Möbius logo and the agent on the other side reads it
  back. One conversation, from empty composer to working feature.
</div>

File upload is one capability the agent can build. The same loop
produces apps, too, actual mini-applications that land on the canvas
next to the chat and persist there.

<figure style="text-align: center; margin: 2rem auto;">
  <video src="{{ '/assets/img/mobius/apps-cycle.mp4' | relative_url }}" width="280" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);">
    <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}" width="280" alt="Five apps Möbius has built in chat" />
  </video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    A few of the apps Möbius has built me, each from a single
    prompt: a live ISS tracker, a Brazil trip planner, a daily
    news digest, a Hacker News dashboard, an earthquake monitor, a
    habit tracker, and a drum machine. The agent wrote the JSX,
    compiled it, mounted it, and the app lives in the same shell
    the chat does.
  </figcaption>
</figure>

This is how general capabilities land (notifications, scheduled
jobs, a web-search button, voice mode, a richer settings panel). The
agent builds it when you ask. A second loop sits above the first, a
harness that watches the inner agent and periodically asks _was this
change generally useful, or was it just for me?_ The generally useful
diffs become candidates for upstreaming into the shipped image, a
promotion step I still review.

### Presentation: the part that stays yours

Capabilities are general; _taste_ is the opposite. The shell ships
with one default theme, but the same agent that built file upload can
rewrite the CSS, swap fonts, add background animation, restructure
the layout, and that diff lives only on your volume. A redeploy can
ship you the new file-upload feature without trampling your
wood-paneled reading-room theme, because the two changes live in
different layers.

The cheap-to-vary axis is visual. Ask the agent to restyle the whole
shell and it rewrites the CSS, swaps the fonts, and repaints the
background. There is no build step you wait on. The new look is live
the moment the agent saves, and you watch it change as it works.

<figure style="text-align: center; margin: 2rem auto;">
  <video src="{{ '/assets/img/mobius/theme-switch.mp4' | relative_url }}" width="260" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);">
    <img src="{{ '/assets/img/mobius/theme-06-medieval.png' | relative_url }}" width="260" alt="The same Möbius new-chat screen cycling through themes the agent built: a medieval manuscript, a cozy reading room, a light Y2K look, a deep-blue ambient theme, and a hot-pink meme theme with floating unicorns." />
  </video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    The same new-chat screen in a range of looks the agent has built, from
    a medieval manuscript to a cozy reading room to a deep-blue ambient
    theme, finishing fully meme-worthy. Each one is a single prompt, and
    the new look is live the moment the agent saves.
  </figcaption>
</figure>

<figure style="text-align: center; margin: 2rem auto;">
  <video src="{{ '/assets/img/mobius/theme-meme-motion.mp4' | relative_url }}" width="280" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.18);"></video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    And it moves. The meme theme is live CSS, so the rainbow drifts and
    the unicorns and emoji bounce across the screen. The agent does not
    judge your taste.
  </figcaption>
</figure>

The harder axis is _layout_, where things are, not how they look. It
is the same conversation and the same chat box. Ask the agent to
rewrite the navigation model and it does, and the new layout is live
immediately, the same way a theme change is. The default is
drawer-first; one prompt later it is a bottom-nav app with Chat /
Apps / Settings as tabs.

<figure class="shot-row">
  <div class="shot">
    <img src="{{ '/assets/img/mobius/nav-01-chat.png' | relative_url }}"
         alt="After prompting for bottom-nav: the chat fills the screen, no header bar, and a persistent bottom strip shows three tabs, Chat (active), Apps, Settings."
         loading="lazy" />
    <span class="shot__label">Chat</span>
  </div>
  <div class="shot">
    <img src="{{ '/assets/img/mobius/nav-02-apps.png' | relative_url }}"
         alt="Apps tab active in the bottom-nav layout: a Hello World card with a hand-wave emoji icon, bottom nav showing Apps highlighted."
         loading="lazy" />
    <span class="shot__label">Apps</span>
  </div>
  <div class="shot">
    <img src="{{ '/assets/img/mobius/nav-03-settings.png' | relative_url }}"
         alt="Settings tab active: AI Provider section showing Claude Code and OpenAI Codex both connected, an Image Generation section with a Gemini API key configured, a Dark mode toggle, and a Recovery section."
         loading="lazy" />
    <span class="shot__label">Settings</span>
  </div>
</figure>

<div class="caption mt-2">
  Default vs reshaped. The drawer-first shell, chats and apps tucked
  behind a toggle, becomes a bottom-nav app with Chat / Apps / Settings
  as a persistent strip. It is not a re-skin; the navigation model of
  the whole instance changed, and Settings is shared across both
  layouts.
</div>

The reshaped Settings tab is also where the provider choice lives.
The same settings panel switches the coding agent between Claude Code
and Codex, with Gemini for image generation. The next message in any
chat uses the new provider. Different models have different tastes
(Codex tends to be terser, Claude tends to spell out its reasoning),
so you can pick the one that matches what you are building, or switch
mid-thread if a turn goes sideways.

The same plainness applies to app data. Apps store data through a
small storage primitive the agent already knows how to compose. New
schemas, scheduled jobs, webhooks are the plumbing you would
write yourself, except you describe it instead.

## Recovery, so you can be fearless

An agent with write access to its own interface will occasionally
ship a CSS rule that hides the composer, a layout change that makes
the drawer unreachable, or a theme that paints text the same colour
as the background. That is the cost of an interface you can reshape
this freely, and it is a cost worth paying as long as it is
reversible.

`/recover` is what makes it reversible. It resets the shell to the
seeded baseline while keeping your chats, apps, and data. It renders
from a separate server-side codepath the agent does not edit, so it
survives even a misbehaved shell rewrite. The whole point of the
route is to let you grow the thing without fear. Any change you make
is one you can roll back, so there is no edit too bold to try.

## The agent is the server

Step back and the loop closes. Möbius is one container you self-host.
The agent inside it is not a chat bolted onto a finished product; it
is the server. It builds the tools, edits the interface those tools
sit in, runs scheduled jobs on a timer, fetches from the web when an
app needs fresh data, and stores everything on a machine you control.
The same thing that answers your message is the thing that ships the
feature, mounts the app, and reshapes the shell around both.

That is what makes the personalization compound. Requests become
software, software becomes context, the next request lands sharper.
Because the server is the agent, every app you grow and every layout
you reshape is one more thing it can build on next time. The more you
use it, the more it is yours.

## What's next

Memory is the next thing to take seriously. The experience file the
agent appends to is a linear log, enough to make my instance diverge
from yours after a few months, but it does not reorganise, and it
shows. Four directions:

- **A knowledge graph.** Structured memory growing from every
  interaction, separate from the chat transcript, so the agent can
  reason about your patterns without re-reading every conversation.
- **Dreaming.** A scheduled background pass that consolidates and
  reorganises the graph while you are away. Anthropic previewed
  something similar for managed agents; the Möbius version is the
  self-hosted, user-controllable one.
- **Discretion.** Noticing stale apps, suggesting something worth
  learning, asking before interrupting, proactive in service of
  the user, not engagement.
- **Help that seeks you out.** The part I want most and am least
  sure how to land. An agent that notices you have been reading
  distributed-systems papers three Tuesdays in a row and builds you
  a swipe-style recommender, without being asked. Most products
  in this space are tuned to maximise engagement; the goal here is
  the opposite, a system that shows up because it knows you, not
  because it is trying to keep you.

None of those ship yet. The loop that makes them possible is the
subject of a [companion post on the self-improvement
harness]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}),
an outer agent that watches the inner one build, asks it questions,
and rewrites its instructions to make it less brittle next time.

A note on the agent itself. For the iteration work behind this post I
have been letting Claude drive Codex through its [Codex
plugin](https://github.com/openai/codex). The disagreements between
the two models were the useful part. When they pulled in different
directions on an edit, that was usually a sign the edit was worth a
closer look.

Since this was written, the apps the agent builds grew a place to
live: an app store, and the start of an operating system around it
where you install, update, tweak, and recover apps on your own instance.
That is its own [companion post]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }}).

The source is on [GitHub](https://github.com/mobius-os/mobius), the
project page is [here]({{ '/mobius/' | relative_url }}), and the
README's deploy button gets you a working instance in about three
minutes. I would love to know what you build with it, and what you
change _around_ what you build.
