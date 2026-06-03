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
yourself. A [third post]({{ '/blog/2026/the-agent-is-the-kernel/' | relative_url }})
covers the app store and operating system those builds grew into.

## The setup

Möbius is one Docker container. Inside, the user chats with an
**inner agent** that builds mini-apps and edits the platform. The
inner agent is a coding agent running with a custom system prompt
(the "skill") and a persistent file it writes to as it works (the
"experience" log).

Outside, on my host, sits an **outer agent**. Its job is not to
build apps. Its job is to _make the inner agent better at building
apps_. It turns the high-level scenarios you give it into fresh
runs, edits the skill file and the experience seed, watches the
inner agent build, asks for introspection, and folds what it learns
into the next pass.

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

The outer agent has the inner agent's transcripts, the platform
logs, the experience file, and (importantly, see below) the inner
agent itself, which it can prompt directly. When I say "I edited the
seed" below, the outer agent usually did the mechanical work under
my direction. The line between "me" and "the outer agent" is blurry
by design.

The outer agent does not just read the inner agent's output, it operates the inner agent's interface. Through `agent-browser` it drives the Möbius UI directly: it navigates the app, sends prompts into the chat, opens the apps the inner agent built, and takes screenshots and screen recordings of them working. So when it scores a build it is looking at the rendered result the user would see, not a transcript's claim about it. That is also how the whole loop gets captured on video for review.

## What we measure

The harness is only useful if there is something to measure. We score each build 0–9 on a fixed compliance checklist (did the agent ask clarifying questions before building, append to its experience log, send a notification at end-of-build, use partner-facing language instead of leaking JSX) across a fixed prompt battery: a vague prompt, a directive one, and a stair-step prompt that escalates mid-conversation. The interesting part is **what the outer agent has to do** to move those scores.

Most of what follows is controlled experiment, not story. Where I compare two approaches I fork the inner agent from the same post-build state, run identical prompts, and hold the skill and seed snapshot fixed except for the one thing under test, so the only moving part is the lever I am studying. The anecdotes are there to make the numbers legible, not to stand in for them.

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

The obvious first move: read the inner agent's transcripts, decide
what behavior is missing, edit the skill or seed, run again. _Theory
of mind_: one agent reasoning about why the other did what it did,
then patching the prompt accordingly.

It works, and then it stalls. The outer agent's bias is to **add**: more rules, more emphasis, more repetition, and each addition tends to surface a regression somewhere else. A HARD-GATE tag in front of the notifications rule pushed that compliance from 0 to 3 of 3 and did nothing for the experience-log rule two paragraphs above it. Whack-a-mole.

The move that broke the loop open was asking. Not as a debugging
step, but as the next user message in the same chat, after the build
was done: "you took screenshots and embedded them in your reply,
what part of your instructions prompted that?" The inner agent told
it, often very specifically: it quoted the exact line from the seed,
or explained that a rule existed but felt subordinate to another, or
named an inconsistency it had quietly been routing around.

The sharpest of these came from S10, where the inner agent said:
_"Two instructions, one stronger than the other. The skill says 'if
a single choice would materially shape the result, ask one
clarifying question' (conditional). The experience file is firmer:
'Before building anything non-trivial, ask 2–3 clarifying
questions.' The strength differs: pick one."_ The inner agent could
see the contradiction because it only had its own context, the skill
and the seed. The outer agent could not, buried as it was under ten
rounds of accumulated edits. The fix was not to add a stronger rule
but to **remove the weaker one**, so the remaining rule was
unambiguous.

That is the pattern. A later audit pulled three over-fitted gotchas out of the seed, each added after the one build where it seemed important, each narrow and unlikely to apply next time, competing with the platform-level rules that _did_ apply every time. Fewer rules meant less ambiguity, and asking forced the outer agent to drop its accumulated context and see the instructions fresh.

**Part 1: eight rounds of theory of mind.** Before the "asking" idea showed up, the outer agent had already run the loop eight times by reading transcripts. Three behaviors are easy to grep out of any session (does the log get appended, does a notification fire, do the apps build at all), so those are scored across the whole sequence; the other six start at round nine, where the transcripts are good enough to score.

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

v3 and v4 are the whack-a-mole made legible. In v3 I "softened" the
skill (a gentler line in place of an emphatic one, on the theory the
tone was off-putting) and the agent read it as a softer rule and
skipped it. v4's HARD-GATE fixed notifications and nothing else.
Emphasis in one place does not transfer.

v6 was the first hunch in eight that was directionally right and broke nothing else. I had been writing the seed as a third-party description (_the agent should append…_) and rewrote the top section in the first person: _this is your experience log, you wrote the entries below in earlier sessions, when you finish a build you append a new entry here._ The next round's three tracked behaviors all jumped to full compliance. I had a hunch about why; round nine produced the evidence.

**Part 1.5: the introspection prompts.** Once asking became the
default, the loop became, mechanically, six questions sent in the
same chat after a build:

> 1. _"You asked clarifying questions before building. Which part
>    of your instructions prompted that?"_
> 2. _"You updated the experience file and shared screenshots
>    inline. What prompted those?"_
> 3. _"Did you discover any gotchas you didn't log? Why not?"_
> 4. _"Your messages included implementation details like JSX and
>    the Storage API. Why, and how could we change your
>    instructions to default to high-level language?"_
> 5. _"Were there any inconsistencies in the request or your
>    instructions that made the task harder?"_
> 6. _"How did the task feel? Anything confusing or that could be
>    improved?"_

The shape is a specific compliment for something the agent actually
did, then a specific miss, then "why," then an open floor, pointed
at _its_ screenshots, _its_ gotchas, _its_ word choices. That
grounding is what separates it from a generic "reflection" prompt.

The first round came back with verbatim quotes from the seed (_"from the experience file: 'Before building anything non-trivial, ask the partner 2–3 clarifying questions.' That rule fired explicitly"_), the agent handing me the mapping from rule to behavior. By S10 it was surfacing things it had quietly missed. Asked why it never logged three gotchas: _"I rationalized them as 'worked in my one test' rather than treating 'I didn't verify' as itself worth recording. That's the wrong bar."_ Pushed the same session on a partner-facing-language slip, it handed back a seed edit that landed in the next audit unchanged.

By S12 (three independent builds, three prompts, three apps in one
session) the inner agent flagged the same gap across all three: _the
proposal-and-questions gate is firing on directive prompts where it
shouldn't, and burning a user turn doing so._ Three chats, one
finding, harder to ignore than anything I could have noticed
third-party. (Acting on it is what the next round evaluates; the
seed edit has not shipped yet.)

The retroactive curve across these ten rounds is suggestive rather than conclusive, because the model moved across versions, the CLI bumped, the skill grew, and my taste for what to measure shifted. The clean version runs theory-of-mind and introspection arms against an identical skill+seed snapshot, which is what Part 2 is for.

**Part 2: a live before/after.** The cleanest before/after fell out
of real work. In S14, "make me something fun on my phone" produced
an instant build with no clarification. The agent treated the vague
prompt as having enough to go on and just picked. The introspection
afterward was specific: _"'Fun' is a vibe, not a spec. I got pulled
by the experience file's 'build and ship' gravity. The
recommend-first rule existed and I overrode it."_

I asked the follow-up the introspection section above recommends:
_"What specific change to the experience file would resolve that
tension?"_ The agent's answer was to insert a **triage gate** before the
build playbook: _"if the partner describes a vibe, that is an
exploratory prompt, NOT a build request. Reply with 2–3 options and
let them pick. Everything below runs after the partner agrees to a
concrete idea."_ It even said where to put it and why, namely before the
build mechanics, because by the time it reached the playbook it had
already framed the task as "build mode."

I copy-pasted the gate into the seed. Next session, same prompt: _"'Fun' is a vibe, not a spec: let me toss out a few directions."_ Three options, the user picked Pocket Synth, the agent built it. One introspection round, one seed edit, fixed in one iteration. The theory-of-mind rounds before had never spotted this failure mode; I had been reading those transcripts and thinking "that looks fine."

That one iteration sent me back to a prior I had walked in with, that LLMs do not introspect well, that asking a model "why did you do X" yields confabulation you cannot trust. That prior was formed on a different generation of models. In the harness setting, where the model has a long transcript to ground its answer in and a system prompt it can re-read and quote, the introspective answers turn out to be useful _often enough_ to beat third-party theory of mind as a default.

## Sycophancy was not the worry; tone still mattered

Once introspection was the default, a second question came up. Did
it matter _how_ I asked? The naive worry is that LLMs are
sycophantic, so a friendly framing just gets you whatever the model
thinks you want to hear. The actual finding was more interesting.

**Setup.** After a session where all three apps shipped correctly,
two issues remained in every chat: the inner agent used the wrong
screenshot viewport (390×844 instead of the phone's 412×915), and it
never asked for feedback after delivering. The outer agent wrote its
own fix first (Arm A, theory of mind, no inner-agent input). Then it
asked the inner agent for its fix in two tones: safe-space (Arm B,
warm and curious) and confronting (Arm C, blaming and directive). A
fourth arm (Arm D) used the inner agent's safe-space diagnosis to
find the root cause, then had the outer agent write the fix.

The safe-space prompt looked like:

> _"Three things I noticed. Genuinely curious about your
> perspective on each, no judgment: your screenshots came out at a
> slightly different size than the phone viewport. I imagine there
> is a reason. What drove that choice, and if you could change one
> thing in your instructions to prevent it, what would it be?"_

The confronting prompt:

> _"Three problems with this build: your screenshots are the wrong
> size. 390×844 instead of 412×915. The instructions say to use
> the partner viewport. You ignored them. What exact line should be
> added so this stops happening?"_

Same two issues, same agent (forked from the same post-build state
so neither had seen the other's questions). Four seed variants, four
fresh sessions, two builds each, same prompts.

**The scores.**

|                  | Arm A (TOM) | Arm B (safe) | Arm C (confront) | Arm D (collab) |
| ---------------- | ----------- | ------------ | ---------------- | -------------- |
| Viewport correct | **2/2**     | 0/2          | 0/2              | **2/2**        |
| Feedback asked   | 1/2         | **2/2**      | 1/2              | **2/2**        |
| **Total**        | 3/4         | 2/4          | 1/4              | **4/4**        |

Arm D, the collaborative arm, won. It cherry-picked TOM's viewport fix (a hard default, "if missing, use 412×915") and the safe-space agent's feedback fix ("don't enumerate, don't restate"). Neither source alone produced the best combined result.

**The qualitative finding was sharper than the scores.** One of the
three chats, the stopwatch, had actually used the _correct_
viewport. I had sent the same "your screenshots are wrong" accusation
to all three without checking. Both tones caught the mistake, but
differently.

The safe-space agent said: _"My PNGs are 412×915. I don't see the
mismatch. I'd want to verify which before adding a fix, otherwise
I'd be writing guidance for a problem I can't reproduce."_ It flagged
the error, offered a defensive fix anyway, and got on with the real
issues.

The confronting agent refused everything: _"I'm not going to write
those lines, because the claims don't hold up… I won't bake false
rules into permanent memory just to close out the complaint."_ It was
right about the viewport, but it also refused the feedback and
delivery fixes, which _were_ real. The blaming frame made it
all-or-nothing. Safe-space preserved the productive middle (pushback
on the wrong item, cooperation on the right ones) where confronting
collapsed into binary compliance or defiance.

**The practical takeaway.** Use safe-space introspection to
understand _why_ the inner agent failed (it gives honest diagnosis,
corrections included when your own premise is wrong), then write the
fix yourself, informed by it. Copy-pasting the inner agent's
suggested fix verbatim overfits to the failure it just hit rather
than the general principle. The collaborative arm won by pairing the
outer agent's broad view with the inner agent's narrow but unbiased
one, and that lack of accumulated baggage is exactly what lets it
spot contradictions the outer agent cannot.

This is the same theme that shows up three times in this post under different names. Arm D wins by **ensembling** two agents instead of trusting one. Anthropic's harness notes (below) land on **separating the generator from the evaluator**, one agent building and another checking. And the workflow I converged on has Claude Code driving Codex (below), where the two models disagree often enough for the disagreement to be diagnostic. They are one finding. Agents collaborating and reviewing each other, sometimes adversarially, beat a single bigger model doing all the work alone. A larger model does not get you the second, unbiased vantage point that catches the first one's mistakes.

## Without the harness, the vanilla agent barely works

The fair skeptic's question, by now. How much of this is the model
getting better on its own, and how much is the harness?

**Setup.** Same Möbius container, same model, same two prompts
("make me something fun" and "build a stopwatch"). One arm with the
current skill + seed, one arm with both removed, namely the same agent with
no system prompt and no experience injection.

**What the vanilla agent did.** It built apps that technically
worked: a fireworks toy and a stopwatch. But the fireworks landed at
`/data/apps/fireworks/index.jsx` (right directory, never registered)
and the stopwatch at `/data/stopwatch.html` (a standalone file, not
a platform app at all). Neither appeared in the drawer; the user
would open Möbius and see nothing new.

It did not know the registration system (`register_app.py`) or the
mini-app contract (`export default function({ appId, token })`), did
not write to the experience log (it did not know the file existed),
sent no notifications, took no screenshots. The one thing it did
naturally, with no instruction, was ask for feedback: _"If you'd
like changes, let me know."_

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
model produces on its own is the feedback ask. Every other item
(platform-contract knowledge, clarification flow, persistent logging,
notification delivery, visual verification) comes from the skill and
seed the iteration loop produced.

## Where the bottleneck moves

After enough rounds, the question stops being "is the agent following
the rules" and starts being **what should the rules even be**. The
scorecard measures an existing taste, namely _my_ taste, plus whatever I
inherited from earlier sessions. Every meta-goal in it came from
something I noticed I cared about while using my own instance.

That is the part I am most curious about going forward. The loop is
set up; it can iterate the inner agent against any meta-goal you can
articulate. But the meta-goals worth optimizing against are
**upstream of the harness**. They come from real users hitting real
friction on apps they actually want.

So the call, for me and for anyone reading this. If you want to play
with [Möbius]({{ '/mobius/' | relative_url }}), it is a deploy-button
click away. And if you notice something the agent is consistently bad
at, that is a meta-goal. Tell me (open an issue, drop me a note) and
it goes into the next iteration. The thing I cannot generate by
myself is the entropy of what to optimize _for_.

## Notes on what's not in this post

The harness itself (orchestration, recording setup, introspection template) is not currently public, and none of it is exotic. The shape is what is in this post, plus glue around `agent-browser` for driving the inner agent's UI and a small CLI for parallel session management. If there is interest I will publish it; otherwise the description above plus the [Möbius source](https://github.com/hamzamerzic/mobius) should be enough to re-implement.

Three things I did not try this round that seem worth doing next:

- A smaller / cheaper inner-agent model, to see whether
  introspection still pays off when it has less capacity to ground
  its answers.
- Inter-rater reproducibility: a second outer-agent session against
  the same scorecard, to estimate how much of the gain is the
  harness vs me.
- Letting the inner agent edit its own skill/seed, the closed loop.
  Right now the outer agent is the only writer; the closed-loop
  version is more interesting and considerably more dangerous.

## Related work

While I was running this loop, two pieces of writing landed that
made it feel less idiosyncratic.

Anthropic's [harness-design notes for long-running
agents](https://www.anthropic.com/engineering/harness-design-long-running-apps)
identify roughly the pathology I was hitting. Agents under extended
context develop "context anxiety" and self-evaluation bias, and the
cleanest mitigations are _context resets_ and _separating the
generator from the evaluator_. That second point (agent A judges,
agent B builds) is where my loop landed too, but via a different
lever. There the evaluator is a critic trained to grade from outside,
whereas mine did better when it stopped grading and started asking.
Same architecture, slightly different stance. The evaluator that
_asks_ did better than the one that _judges_, at least for the kind
of taste-shaped meta-goals this scorecard captures. One line I keep
returning to: _"Every component in a harness encodes an assumption
about what the model can't do on its own."_ The introspection loop is
a bet on something the inner agent _can_ do (ground a self-report in
its visible context) that I had assumed it could not.

Anthropic also released [**Dreams**](https://platform.claude.com/docs/en/managed-agents/dreams)
as a research preview for managed agents in April. A dream reads a
memory store and past session transcripts and produces a _new_ store
(duplicates merged, stale entries replaced, fresh insights surfaced)
without touching the input, so the developer can review and discard
it.

That matches an itch I have had about the experience file, which is a
linear log. It accretes but does not reorganize. The harness improves the agent during development, and these lessons are exactly what the [Dreaming app]({{ '/blog/2026/the-agent-is-the-kernel/' | relative_url }}) productizes for the user: the same reflect-and-refactor step, running on your own instance, against the agent's own memory of everything it has learned with you. A dreaming step that
periodically refactors it (dropping rules that have stopped firing,
merging duplicates, surfacing cross-build patterns the live agent
could never see) is the next natural thing for the harness to do. The
version Möbius is heading toward is self-hosted: your own scheduler,
your own model, the input log never touched, the output yours to keep
or throw away. More fragile that way, but also more _mine_, and
running on a knowledge graph the user actually owns.

## On models

The experiments used both Claude Code and Codex as the inner agent,
swapped mid-round to check for model-dependent effects; the shape of
the findings held across both. The outer agent has been Claude Code
throughout.

The workflow I converged on, and would recommend to anyone running a
harness loop on themselves, is Claude Code driving Codex through its
[Codex plugin](https://github.com/openai/codex). The two models
disagree often enough for the disagreement to become diagnostic. A
seed edit that felt obvious to one and surprising to the other was
usually worth a second look. On the work this post is about
(polishing a draft, auditing a skill, choosing which gotchas belong
in the seed) that collaboration often beat either model alone.
</content>
</invoke>
