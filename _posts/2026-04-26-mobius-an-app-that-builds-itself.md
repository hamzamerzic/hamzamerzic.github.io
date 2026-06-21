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
<li><strong>Presentation</strong> (your theme, layout, fonts) stays
on your volume and remains yours.</li>
<li><strong><code>/recover</code></strong> is a separate recovery
page that brings the instance back when the agent paints itself into a
corner.</li>
<li>Source on <a href="https://github.com/mobius-os/mobius">GitHub</a>;
deploys in about three minutes.</li>
</ul>

</details>

A Möbius strip is a surface with no inside or outside and no beginning
or end. That is the idea behind Möbius, an agent that loops back on
itself, building the tools you use and improving them as it goes.

## You grow it from a chat input

Möbius starts as almost nothing, a chat on one side and an empty
canvas on the other. Because the agent can rewrite the thing it runs
inside, you grow it from there. File upload and scheduled jobs have to
be added; so does the notifications button. Ask for file upload and it
builds file upload. Ask for an app and one appears on the canvas. You
end up with the shell you asked for.

One of those moments looked like this, end to end. I sent a
deliberately ordinary prompt. _"I'd like to send files and images along
with my messages, pictures of stuff I want to talk about, the
occasional document. Can you add file upload to the chat?"_ One
conversation later the agent had added a backend route, message
storage, drag-and-drop, and image rendering.

## You can break it

The same power works against you too. Tell the agent to delete an app
and it deletes it. Tell it to rip out a feature and the feature is
gone. You can repaint the shell until the composer is hidden or
restructure the navigation until the drawer is unreachable. Anything
you can build, you can also break.

Recovery keeps that cheap. `/recover` is a separate page served outside
the editable shell, rendered straight from the server, so it loads even
when the shell it would normally live in is broken. From there a
recovery chat can reset the shell to its seeded baseline, roll back to a
backup, reinstall an app, or patch whatever broke, then restart, all
while keeping your chats, your apps, and your data. That lets you
break it, recover, and try again.

The rest of this series stays with that trade. The agent can touch
the apps, the interface, and the data on your own machine because that
lets it be genuinely useful, and recovery keeps the cost close to zero.
I want software that bends to you.

## Why I built this

Most software asks you to adapt to it. Over time, AI assistants make
this worse. Preferences leak between tasks, memory accumulates in the
wrong places, and the thing that was helpful yesterday becomes an
invisible constraint today. The model in front of you can usually write
the tool you want, but the product around it stops at talking about it.
Ask for a workflow and you get advice; describe a tool and you get a
mockup or a plan. It never crosses over into building the thing.

Möbius puts the assistant inside the product. Asking for a
tool, using it, and correcting it happen in one place. The platform has
to be editable for that to work. If the agent stops at describing the
work, you still have to carry the system in your head.

## How it works

Apps are the obvious adaptive surface. The surrounding shell matters
too, and the harness separates **capabilities**
(general features like file upload or notifications, candidates for
upstreaming so the next install inherits them) from **presentation**
(your theme, layout, fonts, which stay confined to your volume and
stay yours).

### Capabilities grow the platform

Walk through that file-upload chat from the top, in order.

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
  paperclip. By the end of the same chat I attach the Möbius logo and
  the agent on the other side reads it back. One conversation, from
  empty composer to working feature.
</div>

File upload is one capability the agent can build. The same loop also
produces actual mini-applications that appear on the canvas next to the
chat and persist there.

<figure style="text-align: center; margin: 2rem auto;">
  <video src="{{ '/assets/img/mobius/apps-cycle.mp4' | relative_url }}" width="280" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);">
    <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}" width="280" alt="Five apps Möbius has built in chat" />
  </video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    A few of the apps Möbius has built me, each from a single
    prompt: a live ISS tracker, a Brazil trip planner, a daily
    news digest, a Hacker News dashboard, an earthquake monitor, a
    habit tracker, and a drum machine. The agent wrote the JSX and
    mounted the compiled app in the same shell the chat uses.
  </figcaption>
</figure>

General capabilities get added this way too. Notifications, scheduled
jobs, a web-search button, voice mode, and a richer settings panel all
fit the same path. The agent builds the feature when you ask. A second
loop sits above the first, a harness that watches the inner agent and
periodically asks
_was this change generally useful, or specific to my instance?_ The
generally useful diffs become candidates for upstreaming into the
shipped image, a promotion step I still review.

### Presentation stays yours

General capabilities can move upstream. _Taste_ belongs to the
instance. The shell ships with one default theme. The same agent that
built file upload can rewrite the CSS, swap fonts, add background
animation, restructure the layout, and keep that diff confined to your
volume. A redeploy can
ship you the new file-upload feature while your wood-paneled reading-room
theme stays put, because the two changes live in different layers.

Visual changes are cheap to vary. Ask the agent to restyle the whole
shell and it rewrites the CSS, swaps the fonts, and repaints the
background. The new look is live the moment the agent saves, and you
watch it change as it works.

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
    the unicorns and emoji bounce across the screen. The agent keeps its
    opinions to itself.
  </figcaption>
</figure>

_Layout_ is harder because it moves the controls themselves. It is the
same conversation and the same chat box. Ask the agent to rewrite the
navigation model and it does, with the new layout live immediately.
The default is drawer-first. One prompt later it is a bottom-nav app
with Chat / Apps / Settings as tabs.

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
  The drawer-first shell, chats and apps tucked behind a toggle, becomes
  a bottom-nav app with Chat / Apps / Settings as a persistent strip.
  The navigation model of the whole instance changed along with the
  surface treatment.
</div>

The reshaped Settings tab is also where you connect the coding agents,
Claude Code and Codex, and the image model, Gemini. From there a chat
can run on whichever one fits. Different models have different tastes
(Codex tends to be terser, Claude tends to spell out its reasoning),
so you can pick the one that matches what you are building, or switch
if a turn goes sideways.

App data follows the same pattern. Apps store data through a small
storage primitive the agent already knows how to compose. New schemas
and scheduled jobs are the plumbing you would write yourself, except
you describe it instead.

## The agent is the server

Möbius is one container you self-host, and the agent inside it is the
server. It builds the tools, edits the interface those tools sit in,
runs scheduled jobs on a timer, fetches from the web when an app needs
fresh data, and stores everything on a machine you control. The same
thing that answers your message ships the feature, mounts the app, and
reshapes the shell around both.

Requests become software, so personalization compounds, and that
software gives the next request more useful context. Every app you grow
and every layout you reshape gives the agent one more thing to build on
next time.

## What's next

Memory is the next thing to take seriously. The experience file the
agent appends to is a linear log, enough to make my instance diverge
from yours after a few months. It keeps appending chronologically, and
it shows. I had four directions in mind:

- **A knowledge graph.** Structured memory growing from every
  interaction, separate from the chat transcript, so pattern queries
  start from structured memory and skip a full scan of every
  conversation.
- **Reflection.** A scheduled background pass that consolidates and
  reorganises the graph while you are away, so the agent maintains its
  own memory on its own schedule.
- **Discretion.** Noticing stale apps and suggesting something worth
  learning before it interrupts, with the user's interest as the
  constraint.
- **Help that seeks you out.** The part I want most and am least
  sure how to ship. An agent that notices you have been reading
  distributed-systems papers three Tuesdays in a row and builds you
  a swipe-style recommender on its own. Most products
  in this space are tuned to maximise engagement. I want one that
  surfaces a suggestion only when it has a real reason to, and
  otherwise leaves you alone.

When this was written, all four were still future work. Since then, the
Memory graph and Reflection have shipped, covered in a [later post in
this series]({{ '/blog/2026/your-agent-improves-itself/' | relative_url }});
discretion and help that seeks you out are still open. The loop that
makes any of them possible is the subject of a [companion post on the
self-improvement
harness]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}),
an outer agent that watches the inner one build, asks it questions, and
rewrites its instructions to make it less brittle next time.

Since this was written, the apps the agent builds got an app store and
the start of an operating system around it where you
install, update, tweak, and recover apps on your own instance. I cover
that in a [companion post]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }}).

The source is on [GitHub](https://github.com/mobius-os/mobius), the
project page is [here]({{ '/mobius/' | relative_url }}), and the
README's deploy button gets you a working instance in about three
minutes. It runs for roughly five dollars a month on hosting you
control, signing in with your own Claude or Codex account, and your
data stays on the machine you deployed it to. The free Codex plan is already
enough to do a lot. I would love to know what you build with it, and
what you change _around_ what you build.
