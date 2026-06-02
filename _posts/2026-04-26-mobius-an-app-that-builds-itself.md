---
layout: post
title: An agent that adapts to you
date: 2026-04-26 12:00:00
description: A personalized AI agent you can self-host. It builds the tools you need, edits the interface around them, and adapts both its functionality and its presentation to how you actually use it.
thumbnail: assets/img/mobius/covers/cover-post1.jpg
categories: software
giscus_comments: true
related_posts: false
published: true
---

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

<style>
  /* .tldr lives in the shared Möbius post stylesheet (_sass/_mobius-modern). */
  .swiper {
    max-width: 320px;
    margin: 2rem auto;
    border-radius: 0.75rem;
    overflow: hidden;
  }
  .swiper-slide {
    aspect-ratio: 9 / 20;
    background: var(--global-bg-color);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .swiper-slide img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: contain;
  }
  .swiper-slide video {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: contain;
  }
  .swiper-button-prev,
  .swiper-button-next {
    color: var(--global-theme-color);
    opacity: 0.4;
    transition: opacity 0.3s ease;
  }
  .swiper-button-prev:hover,
  .swiper-button-next:hover {
    opacity: 1;
  }
  .swiper-pagination-bullet-active {
    background: var(--global-theme-color);
  }
</style>

<details class="tldr">
<summary><strong>TL;DR.</strong> Möbius is a personalized AI agent you can self-host. It builds the tools you need, edits the interface they sit in, and learns from use.</summary>

<ul>
<li><strong>The demo:</strong> I tore file upload out of the chat,
asked the agent for it back, and got the full pipeline (backend
route, message storage, drag-and-drop, image rendering) in one
conversation.</li>
<li><strong>Capabilities</strong> (file upload, notifications,
settings panels) are candidates for upstreaming so the next install
inherits them.</li>
<li><strong>Presentation</strong> (your theme, layout, fonts) lives
only on your volume and stays yours.</li>
<li><strong><code>/recover</code></strong> resets the shell when
the agent paints itself into a corner.</li>
<li>Source on <a href="https://github.com/hamzamerzic/mobius">GitHub</a>;
deploys in about three minutes.</li>
</ul>

</details>

<p align="center">
  <img src="{{ '/assets/img/moebius.png' | relative_url }}" width="120" alt="Möbius logo" />
</p>

## The demo

Möbius's starting point is a deliberately small chat: no file
upload, no scheduled jobs panel, no notifications button. To keep
the claim honest rather than stage-managed, I picked file upload and
tore the entire pipeline out: deleted the FastAPI route from `/app`,
ripped the React component out of the shell, restarted the app. Then
I sent a deliberately ordinary prompt: _"I'd like to send files and
images along with my messages, pictures of stuff I want to talk
about, the occasional document. Can you add file upload to the
chat?"_

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-02a-pristine.png' | relative_url }}"
           alt="Top of the chat: the typed prompt asking for file upload, the agent's initial check, and a composer at the bottom with no paperclip."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}"
           alt="The feature in use end to end: the Möbius logo attached inline in the sent message, with the agent reading off the symbolism."
           loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<div class="caption mt-2">
  Instructing the agent to add file upload to chat: the prompt at
  the top, the agent's first dig through the codebase. Chat upload
  added: multipart endpoint, message storage, drag-and-drop
  overlay, paste handler, chip row, image thumbnails, all written
  from scratch in the same conversation.
</div>

The full walk-through is below, along with the rest of what Möbius
does: themes the agent rewrites, navigation it restructures, a
`/recover` route for when it paints itself into a corner. But the
file-upload moment is the load-bearing claim, and I wanted it in the
room before any framing. (One caveat: by default the agent gets
read-write on `/data` and read-only on `/app`, so for this demo I
temporarily loosened things to let it land that backend route on its
own; more on why that is not the default in [The catch](#the-catch).)

## Why I built this

Most software asks you to adapt to it. AI assistants make this worse
with time: preferences leak between tasks, memory accumulates in the
wrong places, the thing that was helpful yesterday becomes an
invisible constraint today. The model in front of you is usually
capable of writing the tool you want, but the product around it can
only talk about the tool. You ask for a workflow and get advice. You
describe a tool and get a mockup, a snippet, or a plan. The
assistant stays on one side of the glass.

The premise of Möbius is to put it on the other side: shorten the
distance between wanting, making, using, and correcting until they
happen in one place. Requests become software, software becomes
context, the next request lands somewhere sharper. The platform has
to be editable for that to work: if the agent can only talk about
the work, you still have to carry the system in your head.

The name is from Möbius strips: each app the agent builds does not
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

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-02a-pristine.png' | relative_url }}"
           alt="Top of the chat just after sending the prompt. The agent's reply: 'Before I propose anything, let me check a couple of things, I want to know what's actually possible before committing to an approach.' Then a stack of tool calls, Bash, Read of chats.py, Read of chats_stream.py and ChatView.jsx, then 'Now I have enough for clarifying questions.'"
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-02b-answered.png' | relative_url }}"
           alt="Question cards. The agent's plan: 'No existing attachments pipeline. The build is: backend endpoint, schema extension, agent-side hook, paperclip + previews UI.' Then three forks: FILE TYPES (Images + documents recommended), AFFORDANCES (Paperclip + Paste + Drag-and-drop), SIZE LIMIT (20 MB)."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-02c-submitted.png' | relative_url }}"
           alt="After pressing Submit. The cards lock to the chosen answer per row. Below the cards the agent picks the thread back up: 'On it. Let me load TodoWrite and look at the agent-CLI hand-off + message rendering.' Tool calls follow, Read of chat.py, useStreamConnection.js, MsgContent.jsx."
           loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<div class="caption mt-2">
  The build starts from an empty composer. The agent checks the
  codebase, surfaces three real decisions (file types, affordances,
  size cap) then resumes with the answers locked in and goes
  straight into the schemas and message handoff, picking up the
  existing <code>[Files in this session: …]</code> convention it just
  noticed in the frontend. At this point the endpoint, schema,
  picker, and paperclip still do not exist.
</div>

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-02d-built.png' | relative_url }}"
           alt="Near the end of the same chat. The agent's hand-off: 'Backend won't activate until the container restarts.' Then a numbered round-trip walk-through of attach → send → render. Caps and limits: 20 MB per file, files live under /data/chats/<chat>/uploads/. The composer at the bottom shows a paperclip icon, the frontend pieces are already serving."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}"
           alt="The feature in use end to end: my user bubble showing the Möbius logo attached inline, with the text 'Here is the Möbius logo. Tell me what you see.' The agent reads off the symbolism: 'a human and an AI collaborating on a shared canvas, neither one fully upstream of the other.'"
           loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<div class="caption mt-2">
  Same chat, end to end. The agent summarises what it shipped
  (backend route, schema fields, overlay, paste handler, chip row,
  thumbnails) and flags the one piece that needs a restart; the
  picked file then shows up inline, and the agent on the other side
  actually sees the image: its reply reads off the meaningful
  details. The endpoint it called was not there when I asked, and
  the chip component did not exist either. Both shipped in one chat.
</div>

File upload is one capability the agent can build. The same loop
produces apps, too, actual mini-applications that land on the canvas
next to the chat and persist there:

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
jobs, a web-search button, voice mode, a richer settings panel): the
agent builds it when you ask. A second loop sits above the first: a
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

The cheap-to-vary axis is visual. Four prompts, four different
instances of the same product:

<figure style="text-align: center; margin: 2rem auto;">
  <video src="{{ '/assets/img/mobius/theme-cycle.mp4' | relative_url }}" width="280" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);">
    <img src="{{ '/assets/img/mobius/theme-00-baseline.png' | relative_url }}" width="280" alt="Möbius theme cycle, baseline, cozy reading nook, drifting ambient, medieval manuscript" />
  </video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    Same instance, four prompts: baseline; a cozy reading nook; an
    ambient drifting mesh with glassy bubbles; and a medieval
    manuscript in parchment cream. Each is CSS (sometimes plus a font
    import or a keyframe) the agent wrote from one sentence. The clip
    ends on the clean charcoal default it ships with today.
  </figcaption>
</figure>

<figure style="text-align: center; margin: 2rem auto;">
  <video src="{{ '/assets/img/mobius/theme-agent-transformations.mp4' | relative_url }}" width="280" autoplay loop muted playsinline style="border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);">
    <img src="{{ '/assets/img/mobius/theme-00-baseline.png' | relative_url }}" width="280" alt="Möbius restyled from its default to a Claude-style theme to a meme theme" />
  </video>
  <figcaption class="caption mt-2" style="font-size: 0.85em;">
    Or ask for a specific look. Same instance, restyled end to end:
    the charcoal default, then <em>"make this look like the Claude
    app"</em>, then <em>"go wild and meme-worthy"</em>. Two short
    prompts; the agent rewrote the theme each time.
  </figcaption>
</figure>

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/theme-07-dynamic-prompt.png' | relative_url }}"
           alt="Build chat moment: the agent has scrolled the user's playful-theme prompt out of view at the top, the warm-rose-tinted background is already running while the agent reads files and stages CSS edits, tool blocks (Bash cat / curl / Read /data/shell/src/components/) visible below the prompt."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/theme-07-dynamic-built.png' | relative_url }}"
           alt="Built result, same theme: chat with 'say hi in one short sentence with a smiley' / 'Hi! :)' exchange, drifting bubbles and dark star silhouettes layered over the gradient, composer at the bottom."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <video src="{{ '/assets/img/mobius/theme-07-dynamic.mp4' | relative_url }}"
             autoplay
             loop
             muted
             playsinline
             preload="metadata"
             poster="{{ '/assets/img/mobius/theme-07-dynamic-built.png' | relative_url }}"
             aria-label="Video of the same theme in motion: bubbles drifting up, star silhouettes shifting position, the warm-cool gradient slowly cycling.">
      </video>
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<div class="caption mt-2">
  One chat: mid-build as the agent stages edits, then the finished
  theme with a test "hi" over the drifting bubbles, then the same
  theme in motion. The prompt asked for a "playful room" with a
  <code>prefers-reduced-motion</code> guard. The still and clip
  differ because the gradient cycles.
</div>

The harder axis is _layout_: where things are, not how they look.
Same conversation, same chat box: ask the agent to rewrite the
navigation model and it does. The default is drawer-first; one
prompt later it is a bottom-nav app with Chat / Apps / Settings as
tabs:

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/nav-00-drawer.png' | relative_url }}"
           alt="Default Möbius: drawer-first navigation. The drawer is open, listing 'New chat' at the top, a HISTORY section with three recent chats, an APPS section with one mini-app, and Settings at the bottom. The rest of the chat is dimmed behind."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/nav-01-chat.png' | relative_url }}"
           alt="After prompting for bottom-nav: the chat fills the screen, no header bar, and a persistent bottom strip shows three tabs, Chat (active, purple), Apps, Settings."
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/nav-02-apps.png' | relative_url }}"
           alt="Apps tab active in the bottom-nav layout: a Hello World card with a hand-wave emoji icon, bottom nav showing Apps highlighted"
           loading="lazy" />
    </div>
    <div class="swiper-slide">
      <img src="{{ '/assets/img/mobius/nav-03-settings.png' | relative_url }}"
           alt="Settings tab active: AI Provider section showing Claude Code and OpenAI Codex both CONNECTED with Reconnect buttons, an Image Generation section with a 'Configured' pill on the Gemini API key, a Dark mode toggle, and a Recovery section."
           loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>

<div class="caption mt-2">
  Default vs reshaped. The drawer-first shell becomes a bottom-nav
  app with Chat / Apps / Settings as a persistent strip, native-app
  style. It is not a re-skin; the navigation model of the whole
  instance changed, and the Settings page is shared across both
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
schemas, scheduled jobs, webhooks: these are the plumbing you would
write yourself, except you describe it instead.

## The catch

The sharp edge is permissions. By default the agent can write `/data`
(your shell, apps, storage) but only read `/app` (the server code).
The file-upload demo above temporarily loosened that, useful for
showing what the agent can do, but not something I want as the
default. Shipping write access to `/app` sits behind a
staging-overlay + diff-review + controlled-promotion gate I have not
yet built.

Recovery exists because an agent with write access to its own
interface will occasionally ship a CSS rule that hides the composer,
a layout change that makes the drawer unreachable, or a theme that
paints text the same colour as the background. `/recover` resets the
shell to the seeded baseline while keeping your chats, apps, and
data. It renders from a separate server-side codepath the agent does
not edit, so it survives even a misbehaved shell rewrite.

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
  learning, asking before interrupting: proactive in service of
  the user, not engagement.
- **Help that seeks you out.** The part I want most and am least
  sure how to land. An agent that notices you have been reading
  distributed-systems papers three Tuesdays in a row and builds you
  a swipe-style recommender, without being asked. Most products
  in this space are tuned to maximise engagement; the goal here is
  the opposite: a system that shows up because it knows you, not
  because it is trying to keep you.

None of those ship yet. The loop that makes them possible is the
subject of a [companion post on the self-improvement
harness]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}):
an outer agent that watches the inner one build, asks it questions,
and rewrites its instructions to make it less brittle next time.

A note on the agent itself: for the iteration work behind this post I
have been letting Claude drive Codex through its [Codex
plugin](https://github.com/openai/codex). The disagreements between
the two models were the useful part: when they pulled in different
directions on an edit, that was usually a sign the edit was worth a
closer look.

Since this was written, the apps the agent builds grew a place to
live: an app store, and the start of an operating system around it
where you install, update, tweak, and recover apps on your own instance.
That is its own [companion post]({{ '/blog/2026/the-agent-is-the-kernel/' | relative_url }}).

The source is on [GitHub](https://github.com/hamzamerzic/mobius), the
project page is [here]({{ '/mobius/' | relative_url }}), and the
README's deploy button gets you a working instance in about three
minutes. I would love to know what you build with it, and what you
change _around_ what you build.

<script>
  document.querySelectorAll('.swiper').forEach((swiperEl) => {
    new Swiper(swiperEl, {
      loop: true,
      spaceBetween: 16,
      pagination: {
        el: swiperEl.querySelector('.swiper-pagination'),
        clickable: true,
      },
      navigation: {
        nextEl: swiperEl.querySelector('.swiper-button-next'),
        prevEl: swiperEl.querySelector('.swiper-button-prev'),
      },
    });
  });
</script>
