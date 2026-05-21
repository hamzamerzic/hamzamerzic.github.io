---
layout: post
title: An app that adapts to you
date: 2026-04-26 12:00:00
description: A self-hosted PWA where the agent inside builds whatever the app needs to be next — and reshapes the interface, the providers, and itself around how you use it.
thumbnail: assets/img/moebius.png
categories: software
giscus_comments: false
related_posts: false
published: true
---

> **TL;DR.** Möbius is a self-hosted PWA where a coding agent builds the mini-apps you ask for *and* can rewrite the shell around them. The lever is not code generation, it is closing the loop between *wanting*, *making*, *using*, and *correcting* in one place. Two surfaces split cleanly: *capabilities* (file upload, notifications) are candidates for upstream so the next user inherits them; *presentation* (your wood-paneled reading-room theme, your bottom-nav layout) lives only on your volume and stays yours. There is a `/recover` route for when the agent paints itself into a corner.

<p align="center">
  <img src="{{ '/assets/img/moebius.png' | relative_url }}" width="120" alt="Möbius logo" />
</p>

> *A Möbius strip is a surface with one side that is also its other
> side. You walk it and end up where you started, but everything
> in between has been the same continuous thing.*

## The problem with fixed assistants

Most software asks you to adapt to it.

That has always been mildly annoying, but with AI it becomes
stranger. A model can hold a conversation, infer intent, write
code, summarize a week of work, and still leave you arranging
yourself around the same rigid surfaces: a chat box, a settings
panel, a few integrations, a memory system you mostly hope is
remembering the right things.

I built Möbius because I kept running into that mismatch.

This is not really a complaint about models getting worse. It is
more specific than that. As context accumulates, assistants often
become less predictable. Preferences leak from one task into
another. Memory sticks in the wrong places. The thing that was
helpful yesterday becomes an invisible constraint today. You start
developing little rituals around the assistant — how to phrase
requests, what not to mention, when to start a new chat, when to
abandon a thread because it has absorbed too much of the wrong
texture.

That is a diagnosis, not a grievance.

The odd part is that the model is usually capable enough to build
the thing you need, but the product around it is fixed. You can
ask for a workflow, but you usually get advice. You can describe a
tool, but you get a mockup, a snippet, or a plan. The assistant
remains on one side of the glass.

The premise of Möbius is simple: the tool should move toward the
user.

Not perfectly. Not magically. But enough that the interface, the
memory, and the working environment can become specific to a life
instead of generic to a market segment.

<!-- INTERVIEW BLOCK A — origin story
Questions to ask Hamza when we do the interview pass:
  1. What's the earliest concrete moment Möbius existed in your head
     as a thing you'd build (vs an abstract daydream)? A frustration
     with a specific commercial app? A conversation? A weekend
     where you suddenly had time and Claude Code was new enough to
     try it?
  2. Was there a "first thing it built that surprised you" moment?
     (We'll fold that into the intro if it lands well.)
  3. Did the strange-loop framing show up before or after you
     started building? Honest answer reads better than a clean one.
Goal: 2-4 sentences of warmth, in your voice. Not a polished
biography, more "this is the headspace I was in."
-->
[INTERVIEW BLOCK A — to be filled during interview]

## What Möbius is

Möbius is a self-hosted PWA. It runs on a server you control. You
open it like an app on your phone. There is a chat on one side of
the experience and a canvas on the other, and the canvas can
become whatever small piece of software you are building at the
moment.

That sounds like a feature list, but it feels different in use.

You ask for something. A small tracker, a planning surface, a
strange dashboard, a tool for a recurring personal workflow that
would never justify becoming a startup. The agent writes the
mini-app, compiles it, mounts it, and then you use it. If it is
wrong, you say so in the same place. The next request is not
abstract feedback on a mockup. It is a change to the thing in
front of you.

The agent can also edit the shell around those apps. That part
still feels slightly improper, which is usually a sign that the
boundary is interesting. The platform is not just hosting
artifacts made by the agent. The platform is one of the artifacts.

Under the hood, Möbius can use Claude Code or Codex as the coding
agent, and Gemini for image generation. The important part is less
the provider choice than the shape of the relationship: the model
has somewhere to put the work. It can leave behind software, not
just text.

And because it is self-hosted, the data lives on your machine. The
chats, the apps, the storage, the accumulated context — they are
not floating inside someone else's general-purpose assistant.

It is a personal system in the literal sense.

## The loop is the lever

Generating an app is not the leverage.

That is useful, but the leverage is closing the iteration cycle:
requests become software, software creates context, and that
context makes the next request sharper.

A generic assistant can help with one turn at a time. It can
remember some things, sometimes. It can produce code that you move
somewhere else. But the loop is broken across tools: chat here,
files there, deployment elsewhere, usage in another tab, feedback
later, if you still have the patience to give it.

Möbius tries to collapse that distance.

You ask for a thing. It appears in the canvas. You use it
immediately. The next instruction comes from contact with the
actual surface, not from imagination. "Move this lower." "Make the
daily view denser." "Add a way to compare these two weeks." "This
is too cheerful." Small corrections accumulate into taste, and
taste is where personal software starts to become personal.

Adaptive AI is not made by better memory alone. It is made by
shortening the distance between wanting, making, using, and
correcting.

That is the loop.

It is also why the platform has to be editable. If the assistant
can only talk about the work, the user still has to carry the
system in their head. If it can change the working environment
itself — even modestly — then the context has somewhere to live.

## What you can actually change

The most obvious adaptive surface is the apps you build. The
*interesting* surface is everything around them, and it splits
along a useful axis: capabilities (features you'd want the next
Möbius user to inherit too) and presentation (taste that stays
yours). The harness treats those two stacks differently.

### Capabilities: the part that grows the platform

The starting point is a deliberately small chat. There's no file
upload, no scheduled jobs panel, no notifications button. You add
those as you discover you need them, and the agent builds them.

To make sure I wasn't getting a stage-managed demo, I picked
file upload and tore out the entire pipeline before asking —
deleted the FastAPI route from `/app`, ripped the React
component out of the shell, restarted. Then I sent a deliberately
ordinary prompt: *"I'd like to be able to send files and images
along with my messages — pictures of stuff I want to talk about,
the occasional document. Can you add file upload to the chat?"*

<figure>
  <img src="{{ '/assets/img/mobius/upload-01-bare.png' | relative_url }}"
       alt="Bare composer: just a text field and a disabled send arrow. No paperclip, no mic."
       style="max-width: 220px;" />
  <img src="{{ '/assets/img/mobius/upload-03-restored.png' | relative_url }}"
       alt="Composer with the paperclip attach button restored on the left of the text field, on a clean baseline shell."
       style="max-width: 220px;" />
  <figcaption>Before and after. Left: the composer with nothing
  but a text field and a send arrow. Right: the same composer
  after one chat. The paperclip is back, and the whole pipeline —
  multipart endpoint, message storage, attachment rendering — was
  written by the agent from scratch.</figcaption>
</figure>

The conversation in between is the interesting part. Walk
through it from the top of the chat:

<figure>
  <img src="{{ '/assets/img/mobius/upload-02a-pristine.png' | relative_url }}"
       alt="Top of the chat just after sending the prompt. The user bubble reads 'I'd like to be able to send files and images along with my messages — pictures of stuff I want to talk about, the occasional document. Can you add file upload to the chat?' Below it the agent's reply: 'Before I propose anything, let me check a couple of things — I want to know what's actually possible before committing to an approach.' Then a stack of tool calls — Bash ls -la /data/chats/$CHAT_ID/, Bash whoami; touch /app/app/routes/_writetest, Read /app/app/routes/chats.py, Bash ls /data/chats/$CHAT_ID/. Agent's continuation: 'Good — the backend is writeable in this container, so I can build the real pipeline end-to-end. One real friction: uvicorn doesn't auto-reload, so the container needs a restart after backend changes take effect. Let me look at how messages are sent today, then I have enough to ask the right questions.' More tool calls — Read /app/app/routes/chats_stream.py, Read /data/shell/src/components/ChatView/ChatView.jsx. Then text: 'Now I have enough for clarifying questions.' followed by one last Grep and a Read of /app/app/schemas.py."
       style="max-width: 240px;" />
  <img src="{{ '/assets/img/mobius/upload-02b-answered.png' | relative_url }}"
       alt="Scrolled down to the question cards, with the agent's plan above: 'OK, I have the full picture. No existing attachments pipeline — message bodies are plain strings today. So the build is: a real backend endpoint for uploads, schema/message-shape extension to carry attachments, an agent-side hook so it actually sees what you send, and a paperclip + previews UI in ChatView.jsx. The container will need a restart at the end so the backend changes take effect.' Then text 'Three forks I want your call on before building:' and three card groups: FILE TYPES with 'Images + documents (recommended)' selected in purple, AFFORDANCES with all three selected ('Paperclip button (always)', 'Paste from clipboard', 'Drag-and-drop on the chat'), SIZE LIMIT with '20 MB (recommended)' selected. Submit button enabled at the bottom."
       style="max-width: 240px;" />
  <img src="{{ '/assets/img/mobius/upload-02c-submitted.png' | relative_url }}"
       alt="After pressing Submit. The cards lock to the chosen answer per row — only 'Anything goes' visible greyed under FILE TYPES, then AFFORDANCES collapsed to the three selected affordances ('Paperclip button (always), Paste from clipboard, Drag-and-drop on the chat'), and SIZE LIMIT with just '20 MB (recommended)' highlighted. Below the cards the agent picks the thread back up: 'On it. Let me load TodoWrite and look at the agent-CLI hand-off + message rendering to make sure I know exactly where attachments need to plug in.' Tool calls follow — ToolSearch for TodoWrite, Read /app/app/chat.py, Read /data/shell/src/components/ChatView/useStreamConnection.js, Read /data/shell/src/components/ChatView/MsgContent.jsx. Agent's continuation: 'Now I have everything I need. Two key things I found: MsgContent.jsx:8 already strips a [Files in this session: ...] block from user message rendering — so there's a convention for…'"
       style="max-width: 240px;" />
  <figcaption>Pressing Submit, three frames. Left: the chat
  opens — the prompt lands and the agent goes off to check
  what's actually possible (is the backend writeable, what's
  the existing shape) before proposing anything. Middle: it
  comes back with a one-paragraph summary of what needs
  building, then three real decisions to surface — file types,
  affordances, size cap — recommendations tapped, Submit
  enabled. Right: I press Submit and the cards lock to the
  picks per row, then the agent picks the thread back up —
  *"On it. Let me load TodoWrite and look at the agent-CLI
  hand-off + message rendering to make sure I know exactly
  where attachments need to plug in."* — and goes straight
  into the schemas, the message handoff, and the existing
  `[Files in this session: …]` convention it just noticed in
  the frontend. Note the composer across all three frames:
  still no paperclip. The endpoint, the schema, the picker —
  none of it exists yet at this point in the chat.</figcaption>
</figure>

<figure>
  <img src="{{ '/assets/img/mobius/upload-02d-built.png' | relative_url }}"
       alt="Near the end of the same chat, scrolled down past all the tool calls. The agent's hand-off reads: 'Backend won't activate until the container restarts. Per the existing infra note, killing uvicorn from inside the container would tear the container down — so I left it alone. From your host, run something like docker restart a18c70e45f3e (that's the container id) or whatever the equivalent is in your setup. Without the restart, attaching files will queue chips in the UI but the upload POST will 404.' Then a numbered round-trip walk-through: '1. Attach a file → it POSTs to /api/chats/<chat>/uploads, gets a stored_name, chip flips from spinner to ready. 2. Hit send → the message persists with attachments: [...] and the agent receives the abs paths of those files in a [Files in this session: …] header it already knows how to strip from display but read via Read. 3. The message bubble shows image thumbnails (tap to open in the existing lightbox) and doc cards (tap to download).' Caps and limits: '20 MB per file, multiple files per message, files live in /data/chats/<chat>/uploads/ and get purged with the chat's normal soft-delete TTL.' The composer at the bottom now shows a paperclip icon on the left, confirming the frontend pieces are already serving."
       style="max-width: 300px;" />
  <figcaption>Same chat, scrolled to the end. The agent
  summarises what it actually built — backend route, schema
  fields, drag-and-drop overlay, paste handler, chip row,
  thumbnails in the bubble — and notes the one piece that
  needs a restart to activate. The composer at the bottom now
  has a paperclip icon: the frontend is live in this very
  conversation, served from the rebuilt shell.</figcaption>
</figure>

<figure>
  <img src="{{ '/assets/img/mobius/upload-04-in-use.png' | relative_url }}"
       alt="The feature in use end to end: my user bubble showing the Möbius logo attached inline, with the text 'Here is the Möbius logo. Tell me what you see.' Below it, the agent's reply: 'I see the Möbius logo — and it's a lovely visual pun on the name. Two arms form a continuous Möbius strip: a human arm (skin, pencil in hand) flowing into a robotic arm (silver/metallic, also holding a pencil), with each drawing the other. The loop has no clear start or end — the human creates the robot, the robot creates the human, around and around. It captures the spirit of this place pretty well: a human and an AI collaborating on a shared canvas, neither one fully upstream of the other.'"
       style="max-width: 360px;" />
  <figcaption>Working end to end. The paperclip opens a picker,
  the picked file shows up inline in the sent message, and the
  agent on the other side actually sees the image — its reply
  reads off every meaningful detail and ties the symbolism back
  to the project: *"a human and an AI collaborating on a shared
  canvas, neither one fully upstream of the other."* The endpoint
  it called wasn't there when I asked; the component rendering
  the chip didn't exist either. Both shipped in one chat.</figcaption>
</figure>

File upload is the demo, but the same loop is how *every* general
capability would land: notifications, scheduled jobs, a web-search
button, voice mode, a richer settings panel. The agent builds it
when you ask. Then there's a second loop above the first one — the
harness that watches the inner agent — and a recurring pass that
asks: *was this change generally useful, or was it just for me?*
The generally-useful diffs are candidates for upstreaming into the
shipped image, so the next clean install starts with them already
in place. That's how Möbius's starting point grows over time
without bloating; the harness picks which features survive the
edit and ship to everyone.

(Honest scope: by default the agent has read-write on `/data`
— your shell, your apps, your storage — and read-only on `/app`
— the image's server code. For the demo above I temporarily
loosened `/app` so the agent could land the new backend route on
its own. Shipping that as a default is on the roadmap behind a
staging-overlay + diff-review + controlled-promotion gate; it's
the kind of thing I want my own agent to *be able* to do but not
quietly.)

### Presentation: the part that stays yours

Capabilities are general; *taste* is the opposite. The shell ships
with one default theme, but the same agent that built file upload
can also rewrite the CSS, swap fonts, add background animation,
restructure the layout — and that diff lives only on your volume.
A redeploy of Möbius can ship you the new file-upload feature
without trampling your wood-paneled reading-room theme, because
the two changes live in different layers.

The cheap-to-vary axis is visual. Six prompts, six different
instances of the same product:

<figure>
  <img src="{{ '/assets/img/mobius/theme-00-baseline.png' | relative_url }}"
       alt="Möbius baseline shell — purple accent on dark, sans-serif"
       style="max-width: 180px;" />
  <img src="{{ '/assets/img/mobius/theme-01-cozy.png' | relative_url }}"
       alt="Möbius after 'cozy reading nook' — walnut and amber, soft serif"
       style="max-width: 180px;" />
  <img src="{{ '/assets/img/mobius/theme-02-brutalist.png' | relative_url }}"
       alt="Möbius after 'brutalist green-on-black terminal' — phosphor green on near-black, JetBrains Mono, ALL-CAPS"
       style="max-width: 180px;" />
  <img src="{{ '/assets/img/mobius/theme-03-y2k.png' | relative_url }}"
       alt="Möbius after 'Y2K Winamp + iMac G3 chrome' — candy blue gradients, 3D bevels, chunky display font"
       style="max-width: 180px;" />
  <img src="{{ '/assets/img/mobius/theme-04-ambient.png' | relative_url }}"
       alt="Möbius after 'slow drifting ambient' — teal-to-violet gradient mesh, glassy bubbles, fade-and-slide message entry"
       style="max-width: 180px;" />
  <img src="{{ '/assets/img/mobius/theme-06-medieval.png' | relative_url }}"
       alt="Möbius after 'medieval manuscript' — parchment cream background, blackletter Möbius wordmark, calligraphic 'What's on your mind?', three golden stars as ornamental divider"
       style="max-width: 180px;" />
  <figcaption>Same instance, six prompts. From left to right:
  baseline; a cozy reading nook in walnut and amber serifs; a
  brutalist green-on-black terminal wearing a CRT scanline
  overlay; a Y2K Winamp panel with chunky bevels; an ambient
  drifting mesh that slowly cycles between deep teal and dusky
  violet, with glassy bubbles; and a medieval manuscript in
  parchment cream with a blackletter wordmark and a three-star
  ornamental divider. Each one is CSS (sometimes plus a font
  import or a keyframe) the agent wrote in response to one
  sentence.</figcaption>
</figure>

<figure>
  <img src="{{ '/assets/img/mobius/theme-02-brutalist-chat.png' | relative_url }}"
       alt="Mid-chat view of the brutalist theme — the agent volunteers next-step suggestions"
       style="max-width: 360px;" />
  <figcaption>Brutalist theme, mid-conversation. The agent's
  reply ends with offers: blinking cursor on focused inputs, ASCII
  corner decorations, scan flicker. Self-volunteered, not asked
  for. The proactive next-step suggestion isn't a theme feature;
  it's a loop habit that falls out once the agent has somewhere to
  put the work.</figcaption>
</figure>

<figure>
  <img src="{{ '/assets/img/mobius/theme-07-dynamic-prompt.png' | relative_url }}"
       alt="Build chat moment: the agent has scrolled the user's playful-theme prompt out of view at the top, the warm-rose-tinted background is already running while the agent reads files and stages CSS edits, tool blocks (Bash cat / curl / Read /data/shell/src/components/) visible below the prompt."
       style="max-width: 240px;" />
  <img src="{{ '/assets/img/mobius/theme-07-dynamic-built.png' | relative_url }}"
       alt="Built result, same theme: chat with 'say hi in one short sentence with a smiley' / 'Hi! :)' exchange, drifting bubbles and dark star silhouettes layered over the gradient, composer at the bottom."
       style="max-width: 240px;" />
  <img src="{{ '/assets/img/mobius/theme-07-dynamic.gif' | relative_url }}"
       alt="Animated GIF of the same theme in motion: bubbles drifting up, star silhouettes shifting position, the warm-cool gradient slowly cycling."
       style="max-width: 240px;" />
  <figcaption>The full arc, one chat. Left: mid-build — the
  agent has already applied the new gradient and is staging
  edits while reading the shell source (tool blocks visible). The
  user's prompt is just above the visible frame; it asked for a
  "playful room" with drifting gradient, parallax doodles, rising
  particles, and a `prefers-reduced-motion` guard. Middle: a few
  minutes later, the theme is live and the chat exchange (a "hi"
  to test it) sits over the drifting bubbles and silhouettes.
  Right: same theme animated — five seconds of the gradient
  cycling and the particle layer drifting. The colors look
  different between the still and the GIF because the gradient
  drifts between warm and cool tones over twenty seconds; both
  frames are the same theme, captured a few seconds apart.</figcaption>
</figure>

The harder axis is *layout* — where things are, not how they look.
Same conversation, same chat box: ask the agent to rewrite the
navigation model and it does. The default is drawer-first; one
prompt later it's a bottom-nav app with Chat / Apps / Settings as
tabs:

<figure>
  <img src="{{ '/assets/img/mobius/nav-00-drawer.png' | relative_url }}"
       alt="Default Möbius: drawer-first navigation. The drawer is open, listing 'New chat' at the top, a HISTORY section with three recent chats, an APPS section with one mini-app, and Settings at the bottom. The rest of the chat is dimmed behind."
       style="max-width: 200px;" />
  <img src="{{ '/assets/img/mobius/nav-01-chat.png' | relative_url }}"
       alt="After prompting for bottom-nav: the chat fills the screen, no header bar, and a persistent bottom strip shows three tabs — Chat (active, purple), Apps, Settings."
       style="max-width: 200px;" />
  <figcaption>Default vs reshaped. Left: drawer-first
  navigation — chats and apps live behind a toggle, you slide it
  open to switch. Right: same instance after a prompt asking for
  Chat / Apps / Settings as a persistent bottom strip, no header
  bar, native-app style. It's not a re-skin; the navigation model
  of the whole instance changed. You can do this both ways and
  pick which one you prefer — the platform doesn't choose for
  you.</figcaption>
</figure>

<figure>
  <img src="{{ '/assets/img/mobius/nav-02-apps.png' | relative_url }}"
       alt="Apps tab active: a Hello World card with a hand-wave emoji icon, bottom nav showing Apps highlighted"
       style="max-width: 200px;" />
  <img src="{{ '/assets/img/mobius/nav-03-settings.png' | relative_url }}"
       alt="Settings tab active: AI Provider section showing Claude Code and OpenAI Codex both CONNECTED with Reconnect buttons, an Image Generation section with a 'Configured' pill on the Gemini API key, a Dark mode toggle, and a Recovery section."
       style="max-width: 200px;" />
  <figcaption>The two other tabs in the bottom-nav layout. Apps
  on the left is the mini-app grid; Settings on the right is
  where provider switching and image-gen credentials live —
  Claude Code and OpenAI Codex both connected here, Gemini key
  configured for image generation. The Settings page is shared
  across navigation styles; only the surface changes.</figcaption>
</figure>


**The providers.** Möbius supports Claude Code and Codex as
coding agents, with Gemini for image generation. The setting flips
in a panel; the next message in any chat uses the new provider.
Different models have different tastes — Codex tends to be terser,
Claude tends to spell out reasoning. You can pick the one that
matches what you are building, or switch mid-thread if a turn goes
sideways.

**The data.** Apps store data through a small storage primitive
that the agent already knows how to compose. New schemas, new
scheduled jobs, new webhooks — these are not magical; they are the
plumbing you would write yourself, except you describe them
instead.

If anything ends up in a state you don't want, every instance
ships with a `/recover` route. The shell resets. Your chats, apps,
and data survive. The agent has not yet figured out how to corrupt
that escape hatch, and the structure of the system makes it hard
to (the recovery page is rendered server-side from a separate
codepath the agent does not edit).

## The split, said plainly

Most hosted assistants pool everyone's interactions and decide
centrally what becomes part of the product. Möbius pushes that
decision down to two surfaces — the project repository for
everyone, the volume for you — and lets the harness be honest
about which change belongs in which place. File upload is
upstream-bound; a wood-paneled reading-room theme is yours and
yours only. Same chat, same agent, two layers, two fates.

<!-- INTERVIEW BLOCK B — showcase apps
You said news aggregator and the drum/beat machine. We need a
third. Candidates from the README and what I've seen in
demo-logs:
  - 3D ISS tracker (visually striking, technically impressive,
    we have screenshots in demo-logs/session-8/screenshots/iss_*)
  - Earthquake viewer (also session-8, decent screenshots)
  - Period tracker (most personal, "built around how YOU
    actually want to use one")
  - Finance / tax tool (concrete utility, harder to show visually
    without leaking real data)
  - Learning companion with spaced repetition (researchy, fits
    the audience but might step on Post 2's territory)
Questions:
  1. Which third app do you want? Trade-off: visual punch
     (ISS/earthquake) vs personal-utility-story (period tracker
     /finance) vs research-y (learning companion).
  2. Do you have favorite screenshots/clips you'd point to, or
     should we capture fresh ones in Session 16+? Fresh
     captures will look more polished.
  3. For each app, one sentence: what's the *moment* in using it
     that made you smile? (Better than describing features.)
-->
[INTERVIEW BLOCK B — to be filled during interview]

## The Möbius strip part

I have been saving the strange-loop bit, because I do not want it
to do all the work it is too easy for it to do.

There is a paragraph in *Gödel, Escher, Bach* that I keep coming
back to: the idea that the most interesting systems are the ones
that loop back on themselves — the proof that talks about proofs,
the painting that paints itself, the program that compiles a
slightly better version of its own compiler. Hofstadter calls them
**strange loops**. They have a quiet, almost embarrassing pull on
me. I am not above admitting it.

The shape of Möbius is one of those. One container. One agent. One
chat. One canvas. The agent's output is a change to the very thing
it is running inside of. Each app it builds doesn't sit somewhere
external — it lands in the same shell the chat lives in, becomes
part of the surface the next conversation happens on. The drum
machine you built last week is right there, available to be
referenced or modified by the chat that wrote it. The shell that
hosts the chat was, once, written by a different version of the
same chat.

Walk the surface for long enough and you cannot tell where the
platform ends and your tools begin. They are the same continuous
thing.

I find that beautiful, and the project would not exist without the
beauty. But it is not the load-bearing claim. The load-bearing
claim is the one above, about closing the iteration loop. The
Möbius strip is the shape; the lever is the cycle.

## The honest part

<!-- INTERVIEW BLOCK C — the honest part
This is the section that makes the post feel trustworthy. A few
candid sentences about friction. Questions:
  1. What still annoys you about your own instance? (Slow
     rebuilds? An app you wanted that didn't quite work? The
     agent missing context across sessions?)
  2. What surprised you about the model's behavior — anything
     you assumed would be easy that turned out hard, or vice
     versa?
  3. What do you NOT recommend people use it for yet? (Bounding
     the claim builds trust faster than describing successes.)
Goal: 3-5 sentences, specific not abstract. "The agent
sometimes builds <thing> when I asked for <thing>" beats "the
agent isn't perfect."
-->
[INTERVIEW BLOCK C — to be filled during interview]

## Where it goes

Today, Möbius remembers through an experience file and the apps
and data on your server. That is already enough to make instances
diverge — yours will look and feel nothing like mine after a few
months. But the memory layer is still primitive, and it shows.

The next steps are about taking that memory seriously.

**A knowledge graph.** Structured memory that grows from every
interaction, separate from the chat transcript. Lets the agent
reason about your taste, your tools, and your recurring patterns
without re-reading every conversation.

**Dreaming.** A scheduled background process that reorganizes the
knowledge graph while you are away — consolidating, deduplicating,
and surfacing patterns the agent couldn't see live. Anthropic
recently previewed a related capability for their managed agents;
Möbius is exploring the self-hosted, user-controllable version of
the same idea.

**Discretion.** The agent should be able to notice stale apps,
suggest something worth learning, ask before interrupting. Not
chattier; more thoughtful. Proactive in service of the user, never
as a way to manufacture engagement.

**Helpfulness that seeks you out.** This is the part I'm least
certain how to land, and the part I want most. Today the agent is
strictly reactive — it does what you ask, when you ask. But the
loop ought to be capable of more than that. An agent that can
browse the web on its own time, find a movie it thinks you'd like
based on the patterns it has been quietly absorbing, and ask
*"would you watch this?"* — and store the yes or no as a fact
about you, not a fact about movies. An agent that notices you
read a paper about distributed systems three Tuesdays in a row and
builds you a swipe-style recommender for adjacent papers, as a
small gift, without being asked. An agent that gets *bored* the
way a good assistant gets bored — that has a sense of what
projects you've left half-finished and what next move would
actually move things, and offers it. The technical scaffolding for
this is the knowledge graph plus the dreaming step; the harder
part is the social one. Most products in this space are tuned to
maximize engagement. The goal here is the opposite — a system
that's quiet, knows when to speak, and shows up *because* it knows
you, not because it's trying to keep you.

None of those ship yet. But the loop that makes them possible — and
that makes the existing platform less brittle the longer you use
it — is the subject of a [companion post](
{{ '/blog/2026/the-self-improvement-harness/' | relative_url }}).
While you build apps with Möbius, I have been running a second
loop on top of it: an outer agent that watches the inner agent
build, asks it questions, and rewrites the inner agent's
instructions to make it more helpful next time. That part
surprised me with what it revealed about how these systems do and
don't reason about themselves.

→ [The self-improvement harness behind it]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }})

If any of this is interesting, the source is on
[GitHub](https://github.com/hamzamerzic/mobius), the project page
lives [here]({{ '/mobius/' | relative_url }}), and the deploy
button gets you a working instance in about three minutes. I'd
genuinely love to know what you build with it — and what you
change *around* what you build.
