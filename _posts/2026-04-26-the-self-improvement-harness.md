---
layout: post
title: The self-improvement harness behind Möbius
date: 2026-04-26 13:00:00
description: An outer agent talks to an inner agent and tries to make it more helpful. Notes on what we measured, what surprised us, and where the bottleneck moved to.
thumbnail: assets/img/mobius/covers/cover-post2.jpg
categories: software, research
giscus_comments: true
related_posts: false
published: true
---

<!-- .tldr, .stat-callout, .pull-quote live in the shared Möbius post
     stylesheet (_sass/_mobius-modern.scss). -->

<details class="tldr">
<summary><strong>TL;DR.</strong> The goal is to make Möbius learn and adapt to you, and a lot of what you want is genuinely hard to specify. <em>"Keep asking clarifying questions until the task is clear"</em> is the kind of instruction an agent cannot follow well from the words alone. So I paired an inner agent (building apps in a container) with an outer one (editing the inner's instructions between sessions) and ran the loop on myself across many controlled experiments.</summary>

<p>What the experiments showed:</p>

<ul>
<li><strong>Third-party theory of mind does not work well.</strong> A bigger outside agent with more context cannot reason out how to better prompt another agent. Reading transcripts and patching the prompt stalls fast.</li>
<li><strong>Experience does.</strong> An agent reflecting on its own session, with the transcript still in context, understands and self-corrects better than the larger agent watching from outside.</li>
<li><strong>Collaboration beats a single bigger model.</strong> Agents that build, check, and question each other outscore any one agent working solo.</li>
<li><strong>Coaching plus experience compounds.</strong> The harness earned 10 of the 12 scorecard points the vanilla agent leaves on the floor.</li>
<li><strong>The bottleneck moves to meta-goals.</strong> Once the loop works, the limit is no longer the model but whatever behaviours you decide are worth optimizing for, upstream of the harness. The same lessons are what the Dreaming app productizes for you at runtime.</li>
</ul>

</details>

This is a companion post to [An agent that adapts to you]({{
'/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }}),
which is about the agent itself. This one is about the loop that
makes it slowly better, and what falls out of running that loop on
yourself. A [third post]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }})
covers the app store and OS those builds grew into.

## The setup

Möbius is one Docker container. Inside, the user chats with an
**inner agent**, a coding agent that builds mini-apps and edits the
platform, running with a custom system prompt (the "skill") and a
persistent file it writes to as it works (the "experience" log).

Outside, on my host, sits an **outer agent** whose job is to _make
the inner agent better at building apps_. It turns the high-level
scenarios you give it into fresh runs, edits the skill file and the
experience seed, watches the inner agent build, asks for
introspection, and folds what it learns into the next pass.

<figure class="mb-diagram">
  <div class="mb-cycle">
    <div class="mb-node">
      <span class="mb-node__lead">you</span>
      <span class="mb-node__title">Decide what is worth getting good at</span>
      <span class="mb-node__sub">the high-level capabilities the agent should have, the goals worth optimising for</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">scenarios &amp; goals</span></span>

    <div class="mb-node accent">
      <span class="mb-node__lead">outer agent · host</span>
      <span class="mb-node__title">Turn goals into scenarios, coach the build</span>
      <span class="mb-node__sub">writes the skill and the system prompt the inner agent will run with</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">skills + system prompt</span></span>

    <div class="mb-node">
      <span class="mb-node__lead">inner agent · Möbius</span>
      <span class="mb-node__title">Solve the low-level build</span>
      <span class="mb-node__sub">builds the mini-app from chat and logs what it hit along the way → results</span>
    </div>

    <span class="mb-arrow mb-arrow--bi">⇅<span class="mb-arrow__label">introspection: the outer and inner agent talk through what worked, and why</span></span>

    <div class="mb-loopback">
      <span class="mb-loopback__glyph">↺</span>
      <span>updated skills + system prompt &nbsp;→&nbsp; the outer agent runs the next build</span>
    </div>
    <div class="mb-loopback">
      <span class="mb-loopback__glyph">↺</span>
      <span>summary of results + improvements &nbsp;→&nbsp; you, who set the next scenarios</span>
    </div>

  </div>
  <figcaption>Two loops, one machine. In the <strong>inner loop</strong>, the outer agent writes the inner agent's instructions, the inner agent builds, and the two introspect on the result to rewrite those instructions. In the <strong>outer loop</strong>, you set the capabilities worth having; each pass hands back a summary, and you set the next ones.</figcaption>
</figure>

The outer agent has the inner agent's transcripts, the platform logs,
the experience file, and (importantly, see below) the inner agent
itself, which it can prompt directly. When I say "I edited the seed"
below, the outer agent usually did the mechanical work under my
direction; the line between "me" and "it" is blurry by design.

The outer agent does not just read the inner agent's output, it operates the inner agent's interface. Through `agent-browser` it drives the Möbius UI directly, sending prompts into the chat, opening the apps the inner agent built, and screenshotting and recording them working. So when it scores a build it is looking at the rendered result the user would see, not a transcript's claim about it, and that is also how the whole loop gets captured on video for review.

## What we measure

We score each build 0–9 on a fixed compliance checklist (clarifying questions before building, experience-log append, end-of-build notification, partner-facing language instead of leaked JSX) across a fixed prompt battery: a vague prompt, a directive one, and a stair-step prompt that escalates mid-conversation. The interesting part is **what the outer agent has to do** to move those scores.

Most of what follows is controlled experiment, not story. Where I compare two approaches I fork the inner agent from the same post-build state, run identical prompts, and hold the skill and seed snapshot fixed except for the one thing under test, so the only moving part is the lever I am studying. The anecdotes make the numbers legible, they do not stand in for them.

<div class="stat-callout">
  <div class="stat-number">+10</div>
  <div class="stat-label">
    On the same prompts, the same agent earned <strong>2 of 12</strong>
    scorecard points with no system prompt or experience seed, and
    <strong>12 of 12</strong> with the current harness. The
    <a href="#without-the-harness-the-vanilla-agent-barely-works">full
    setup is below</a>; everything between here and there is how the
    harness got that good.
  </div>
</div>

## Asking the inner agent beats theorising about it

The obvious first move is _theory of mind_, read the inner agent's
transcripts, reason about why it did what it did, edit the skill or
seed, run again. It works, and then it stalls. The outer agent's bias
is to **add**, more rules, more emphasis, more repetition, and each
addition tends to surface a regression somewhere else. Whack-a-mole.

What broke the loop open was asking, as the next message in the same
chat once the build was done: "you took screenshots and embedded them
in your reply, what part of your instructions prompted that?" The
inner agent told it, often very specifically, quoting the exact seed
line or naming an inconsistency it had been quietly routing around.

The sharpest came from S10: _"Two instructions, one stronger than the
other. The skill says ask one clarifying question only if a choice
would materially shape the result. The experience file is firmer, ask
2–3 before anything non-trivial. The strength differs, pick one."_ The
inner agent could see the contradiction because it only had its own
context; the outer agent, buried under ten rounds of edits, could not.
The fix was to **remove the weaker rule**, not add a stronger one.
Asking forced the outer agent to drop its accumulated context and see
the instructions fresh.

**Part 1: eight rounds of theory of mind.** Before asking showed up, the outer agent had run the loop eight times by reading transcripts. Three behaviors are easy to grep out of any session (log appended, notification fired, apps built at all), so those are scored across the whole sequence.

| Round | Apps | Log | Notify | What I changed since the previous round                    |
| ----- | ---- | --- | ------ | ---------------------------------------------------------- |
| v1    | 3/3  | 0/3 | 0/3    | (baseline)                                                 |
| v2    | 3/3  | 1/3 | 0/3    | filesystem perms, because writes had been silently failing |
| v3    | 3/3  | 0/3 | 0/3    | softened skill prose. **regressed**                        |
| v4    | 3/3  | 0/3 | 3/3    | HARD-GATE tag in front of the notifications rule           |
| v5    | 2/2  | 1/2 | 2/2    | removed an "injection-meta" wrapper from the seed          |
| v6    | 2/2  | 2/2 | 2/2    | seed rewritten as first-person "about this file"           |
| v7    | 1/1  | 1/1 | 1/1    | (held, same recipe, different app)                         |
| v8    | 1/1  | 1/1 | 1/1    | Bash `>>` append pattern + inline screenshots              |

v3 and v4 are the whack-a-mole made legible. Softening the skill in
v3 (on the theory the emphatic tone was off-putting) got read as a
softer rule and skipped; v4's HARD-GATE fixed notifications and
nothing else. Emphasis in one place does not transfer.

v6 was the first hunch in eight that was directionally right and broke nothing else. I had been writing the seed as a third-party description (_the agent should append…_) and rewrote the top in the first person, _this is your experience log; you append a new entry when you finish a build._ The next round's tracked behaviors all jumped to full compliance.

**Part 1.5: the introspection prompts.** Once asking became the
default, the loop became, mechanically, six questions after a build,
each grounded in something the agent actually did. _Which instruction
prompted you to ask before building? Did you find any gotchas you
didn't log, and why not? Why did your messages leak JSX and the
Storage API, and how would you change the rules to default to
high-level language?_ A specific compliment, then a specific miss,
then "why," then an open floor, which is what separates it from a
generic "reflection" prompt.

By S12 the agent was surfacing things it had quietly missed. Across three independent builds in one session it flagged the same gap in all three chats, the proposal-and-questions gate firing on directive prompts where it shouldn't and burning a user turn doing so. One finding repeated across three chats is harder to ignore than anything I could have noticed third-party.

The curve across these rounds is suggestive, not conclusive, because the model, the CLI, the skill, and my taste all moved underneath it. The clean version runs theory-of-mind and introspection arms against an identical skill+seed snapshot, which is what Part 2 is for.

**Part 2: a live before/after.** The cleanest experiment fell out of
real work. In S14, "make me something fun on my phone" produced an
instant build with no clarification, and the introspection afterward
was specific: _"'Fun' is a vibe, not a spec. I got pulled by the
experience file's 'build and ship' gravity. The recommend-first rule
existed and I overrode it."_ Asked what change to the file would
resolve that tension, the agent proposed a **triage gate** to sit
before the build playbook, _"if the partner describes a vibe, that is
an exploratory prompt, NOT a build request. Reply with 2–3 options and
let them pick,"_ because by the time it reached the playbook it had
already framed the task as "build mode."

I copy-pasted the gate into the seed. Next session, same prompt, the agent tossed out three directions, the user picked Pocket Synth, and built it. One introspection round, one seed edit, one iteration. The theory-of-mind rounds before had never spotted this; I had read those transcripts and thought "fine."

That revised a prior I walked in with, formed on an earlier generation of models, that asking a model "why did you do X" yields confabulation you cannot trust. With a long transcript to ground the answer in and a system prompt it can re-read and quote, the introspective answers are useful _often enough_ to beat third-party theory of mind as a default.

## Sycophancy was not the worry; tone still mattered

Once introspection was the default, did it matter _how_ I asked? The
naive worry is that a friendly framing just gets you whatever the
sycophantic model thinks you want to hear. The finding was more
interesting.

**Setup.** After a session where all three apps shipped correctly,
two issues remained in every chat: the inner agent used the wrong
screenshot viewport (390×844 instead of the phone's 412×915), and it
never asked for feedback after delivering. The outer agent wrote its
own fix first (Arm A, theory of mind). Then it asked the inner agent
in two tones, safe-space (Arm B, warm and curious) and confronting
(Arm C, blaming and directive). A fourth arm (Arm D) took the
safe-space diagnosis and had the outer agent write the fix.

The safe-space prompt:

> _"Three things I noticed, genuinely curious about your perspective,
> no judgment. Your screenshots came out at a slightly different size
> than the phone viewport. I imagine there is a reason. What drove
> that choice, and if you could change one thing in your instructions
> to prevent it, what would it be?"_

The confronting one:

> _"Three problems with this build. Your screenshots are the wrong
> size, 390×844 instead of 412×915. The instructions say to use the
> partner viewport. You ignored them. What exact line should be added
> so this stops happening?"_

Each arm forked from the same post-build state, so no agent had seen
another's questions. Four seed variants, four fresh sessions, two
builds each, same prompts.

**The scores.**

|                  | Arm A (TOM) | Arm B (safe) | Arm C (confront) | Arm D (collab) |
| ---------------- | ----------- | ------------ | ---------------- | -------------- |
| Viewport correct | **2/2**     | 0/2          | 0/2              | **2/2**        |
| Feedback asked   | 1/2         | **2/2**      | 1/2              | **2/2**        |
| **Total**        | 3/4         | 2/4          | 1/4              | **4/4**        |

Arm D, the collaborative arm, won. It cherry-picked TOM's viewport fix (a hard default, "if missing, use 412×915") and the safe-space agent's feedback fix ("don't enumerate, don't restate"), and neither source alone produced the best combined result.

**The qualitative finding was sharper than the scores.** One of the
three chats, the stopwatch, had actually used the _correct_ viewport.
I had sent the same "your screenshots are wrong" accusation to all
three without checking, and both tones caught my mistake.
The safe-space agent said _"My PNGs are 412×915. I don't see the
mismatch. I'd want to verify which before adding a fix,"_ then offered
a defensive fix anyway and got on with the real issues. The confronting
agent refused everything: _"I'm not going to write those lines,
because the claims don't hold up… I won't bake false rules into
permanent memory just to close out the complaint."_ It was right
about the viewport, but the blaming frame made it all-or-nothing, so
it also refused the feedback and delivery fixes, which _were_ real.
Safe-space kept the productive middle, pushback on the wrong item and
cooperation on the right ones.

**The practical takeaway.** Use safe-space introspection to
understand _why_ the inner agent failed (it gives honest diagnosis,
corrections included when your premise is wrong), then write the fix
yourself, informed by it. Copy-pasting the suggested fix verbatim
overfits to the failure it just hit rather than the general principle.

This is the same theme that shows up three times in this post under different names. Arm D wins by **ensembling** two agents instead of trusting one. Anthropic's harness notes (below) land on **separating the generator from the evaluator**, one agent building and another checking. And the workflow I converged on has Claude Code driving Codex (below), where the two models disagree often enough for the disagreement to be diagnostic. They are one finding. Agents collaborating and reviewing each other, sometimes adversarially, beat a single bigger model doing all the work alone, because a larger model does not give you the second, unbiased vantage point that catches the first one's mistakes.

## Without the harness, the vanilla agent barely works

The fair skeptic's question, by now. How much of this is the model
getting better on its own, and how much is the harness?

**Setup.** Same Möbius container, same model, same two prompts
("make me something fun" and "build a stopwatch"). One arm with the
current skill + seed, one with both removed.

**What the vanilla agent did.** It built apps that technically
worked, a fireworks toy and a stopwatch. But the fireworks landed at
`/data/apps/fireworks/index.jsx` (right directory, never registered)
and the stopwatch at `/data/stopwatch.html` (a standalone file, not
a platform app at all). Neither appeared in the drawer; the user
would open Möbius and see nothing new. It did not know the
registration system or the mini-app contract, did not write to the
experience log (it did not know the file existed), sent no
notifications, took no screenshots. The one thing it did naturally,
with no instruction, was ask for feedback.

**The scorecard.**

|                      | Baseline | Current harness |
| -------------------- | -------- | --------------- |
| Apps visible to user | 0/2      | 2/2             |
| Clarifying questions | 0/2      | 2/2             |
| Experience log       | 0/2      | 2/2             |
| Notifications        | 0/2      | 2/2             |
| Screenshots          | 0/2      | 2/2             |
| Feedback asked       | 2/2      | 2/2             |
| **Total**            | 2/12     | **12/12**       |

The harness contributes 10 of the 12 points. The only behavior the
model produces on its own is the feedback ask; every other item comes
from the skill and seed the iteration loop produced.

## Where the bottleneck moves

After enough rounds, the question stops being "is the agent following
the rules" and starts being **what should the rules even be**. The
scorecard measures _my_ taste; every meta-goal in it came from
something I noticed I cared about while using my own instance.

That is what I am most curious about going forward. The loop can
iterate the inner agent against any meta-goal you can articulate, but
the meta-goals worth optimizing against are **upstream of the
harness**, and they come from real users hitting real friction on
apps they actually want.

So the call, for anyone reading this. [Möbius]({{ '/mobius/' |
relative_url }}) is a deploy-button click away. If you notice
something the agent is consistently bad at, that is a meta-goal; tell
me and it goes into the next iteration. The thing I cannot generate by
myself is the entropy of what to optimize _for_.

## Notes on what's not in this post

The harness itself (orchestration, recording setup, introspection template) is not currently public, and none of it is exotic. The shape is what is in this post, plus glue around `agent-browser` and a small CLI for parallel sessions. If there is interest I will publish it; otherwise the description above plus the [Möbius source](https://github.com/mobius-os/mobius) should be enough to re-implement.

Three things I did not try this round that seem worth doing next.

- A smaller, cheaper inner-agent model, to see whether introspection
  still pays off with less capacity to ground its answers.
- A second outer-agent session against the same scorecard, to
  estimate how much of the gain is the harness versus me.
- Letting the inner agent edit its own skill and seed, the closed
  loop. Right now the outer agent is the only writer; the closed-loop
  version is more interesting and considerably more dangerous.

## Related work

While I ran this loop, two pieces of Anthropic writing landed that
made it feel less idiosyncratic.

The [harness-design notes for long-running
agents](https://www.anthropic.com/engineering/harness-design-long-running-apps)
identify roughly the pathology I was hitting. Agents under extended
context develop "context anxiety" and self-evaluation bias, and the
cleanest mitigations are _context resets_ and _separating the
generator from the evaluator_, agent A judges, agent B builds. That
is where my loop landed too, but the evaluator did better when it
stopped grading and started asking, a bet on something I had assumed
the inner agent could not do, ground a self-report in its own visible
context.

Anthropic also released [**Dreams**](https://platform.claude.com/docs/en/managed-agents/dreams)
in April. A dream reads a memory store and past transcripts and
produces a _new_ store (duplicates merged, stale entries replaced,
fresh insights surfaced) without touching the input, for the developer
to review and discard.

That matches an itch I have about the experience file, a linear log that accretes but never reorganizes. The harness improves the agent during development, and these lessons are what the [Dreaming app]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }}) productizes for the user. It runs the same reflect-and-refactor step on your own instance, against the agent's own memory of everything it has learned with you, dropping rules that have stopped firing, merging duplicates, surfacing cross-build patterns the live agent could never see. The version Möbius is heading toward is self-hosted, the input log never touched, the output yours to keep.

## On models

The experiments used both Claude Code and Codex as the inner agent,
swapped mid-round to check for model-dependent effects, and the
findings held across both. The outer agent was Claude Code throughout.

The workflow I converged on, and would recommend to anyone running a
harness loop on themselves, is Claude Code driving Codex through its
[Codex plugin](https://github.com/openai/codex). The two models
disagree often enough for the disagreement to become diagnostic; a
seed edit that felt obvious to one and surprising to the other was
usually worth a second look. On the work this post is about (polishing
a draft, auditing a skill, choosing which gotchas belong in the seed)
that collaboration often beat either model alone.
