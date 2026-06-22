---
layout: post
title: The self-improvement harness behind Möbius
date: 2026-04-26 13:00:00
description: An outer agent talks to an inner agent and tries to make it more helpful. Notes on what we measured, what surprised us, and where the bottleneck moved to.
thumbnail: assets/img/mobius/covers/cover-post2.jpg
thumbnail_2x: assets/img/mobius/covers/cover-post2-2x.jpg
categories: software, research
giscus_comments: true
related_posts: false
published: true
---

<!-- .tldr, .stat-callout, .pull-quote live in the shared Möbius post
     stylesheet (_sass/_mobius-modern.scss). -->

<details class="tldr">
<summary><strong>TL;DR.</strong> The goal is to make Möbius learn and adapt to you, and a lot of what you want is genuinely hard to specify. <em>"Keep asking clarifying questions until the task is clear"</em> is the kind of instruction an agent cannot follow well from the words alone. So I paired an inner agent (building apps in a container) with an outer one (editing the inner's instructions between sessions) and ran the loop on myself across many controlled experiments.</summary>

<p>The experiments showed:</p>

<ul>
<li><strong>Third-party theory of mind does not work well.</strong> A bigger outside agent with more context cannot reason out how to better prompt another agent. Reading transcripts and patching the prompt stalls fast.</li>
<li><strong>Experience does.</strong> An agent reflecting on its own session, with the transcript still in context, understands and self-corrects better than the larger agent watching from outside.</li>
<li><strong>Collaboration beats a single bigger model.</strong> Agents that build, check, and question each other outscore any one agent working solo.</li>
<li><strong>Coaching plus experience compounds.</strong> The harness earned 10 of the 12 scorecard points the vanilla agent leaves on the floor.</li>
<li><strong>The next limit is choosing better meta-goals.</strong> Once the loop works, the limit becomes the behaviours you choose to optimize for, upstream of the harness. The same lessons are what the Reflection app productizes for you at runtime.</li>
</ul>

</details>

Fully recursive self-improvement, a system that rewrites itself
unattended and just gets better, is not what this is. A person is in
the loop at every turn. What already works is the half in front of it:
an agent and a human improving that agent together, faster and more
durably than either manages alone.

My companion post, [An agent that adapts to you]({{
'/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }}),
covers the agent itself. This post covers the loop that makes it
slowly better, and what I learned from running that loop on myself.
A [third post]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }})
covers the app store and OS those builds grew into.

## The setup

Möbius is one Docker container. Inside, the user chats with an
**inner agent**, a coding agent that builds mini-apps and edits the
platform, running with a custom system prompt (the "skill") and a
persistent file it writes to as it works (the "experience" log).

Outside, on my host, an **outer agent** works on _making the inner
agent better at building apps_. It turns the high-level scenarios you
give it into fresh runs, edits the skill file and the experience seed,
watches the inner agent build, asks for introspection, and folds what
it learns into the next pass.

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
the experience file, and (this mattered later) the inner
agent itself, which it can prompt directly. When I say "I edited the seed"
below, the outer agent usually did the mechanical work under my
direction.

The outer agent reads the inner agent's output and operates its interface. Through `agent-browser` it drives the Möbius UI directly, sending prompts into the chat, opening the apps the inner agent built, and screenshotting and recording them working. When it scores a build, it checks the rendered result the user would see, and the same run gets captured on video for review.

## What we measure

We score each build on six compliance behaviors, each worth one point on each of the two build prompts, for twelve points per run. The six are apps registered and visible to the user, clarifying questions before building, an experience-log append, an end-of-build notification, screenshots, and asking for feedback. I track the interventions needed to improve the scores, not only the final scores.

Most of what follows is controlled experiment. Where I compare two approaches I fork the inner agent from the same post-build state, run identical prompts, and hold the skill and seed snapshot fixed except for the one rule under test. The anecdotes explain the numbers, but the controlled comparisons are where the actual evidence is. The numbers come from my own test sessions rather than the public repo, since the harness that runs them is not open source, so you are taking them on trust rather than rerunning them from the code yourself.

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

I started with _theory of mind_. Read the inner agent's
transcripts, reason about why it did what it did, edit the skill or
seed, run again. It works briefly, then stalls. The outer agent's bias
is to **add** rules and emphasis, and each addition tends to surface a
regression somewhere else. Whack-a-mole.

The loop improved when the outer agent asked a follow-up in the same
chat after the build was done, quoting the behavior back to the inner
agent and asking which instruction caused it. The inner agent told it,
often very specifically, quoting the exact seed line or naming an
inconsistency it had been quietly routing around.

S10 showed the problem clearly. _"Two instructions, one stronger than the
other. The skill says ask one clarifying question only if a choice
would materially shape the result. The experience file is firmer, ask
2–3 before anything non-trivial. The strength differs, pick one."_ The
inner agent could see the contradiction because it only had its own
context. The outer agent, buried under ten rounds of edits, could not.
Removing the weaker rule helped. A stronger rule would have added more
noise. Asking forced the outer agent to drop its accumulated context
and read the instructions fresh.

**Part 1. Eight rounds of theory of mind.** Before asking showed up, the outer agent had run the loop eight times by reading transcripts. Three behaviors are easy to grep out of any session (log appended, notification fired, apps built at all), so those are scored across the whole sequence.

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

v3 and v4 show the regression pattern. Softening the skill in
v3 (on the theory the emphatic tone was off-putting) got read as a
softer rule and skipped. v4's HARD-GATE fixed notifications and left
the rest untouched. Emphasis in one place does not transfer to another.

v6 was the first hunch in eight that helped and kept the other tracked behaviors intact. I had been writing the seed as a third-party description (_the agent should append…_) and rewrote the top in the first person, _this is your experience log; you append a new entry when you finish a build._ The next round's tracked behaviors all jumped to full compliance.

**Part 1.5. The introspection prompts.** Once asking became the
default, the loop turned into, mechanically, six questions after a
build, each grounded in something the agent actually did. _Which
instruction prompted you to ask before building? Did you find any
gotchas you didn't log, and why not? Why did your messages leak JSX and
the Storage API, and how would you change the rules to default to
high-level language?_ I paired a specific compliment with a specific
miss and then gave it room to explain. That kept the prompt away from
generic "reflection."

By S12 the agent was surfacing things it had quietly missed. Across three independent builds in one session it flagged the same gap in all three chats, the proposal-and-questions gate firing on directive prompts where it shouldn't and burning a user turn doing so. One finding repeated across three chats is harder to ignore than anything I could have noticed from outside.

The curve across these rounds is suggestive rather than conclusive, because the model, the CLI, the skill, and my taste all moved underneath it. I used Part 2 for the cleaner comparison, with theory-of-mind and introspection arms against an identical skill+seed snapshot.

**Part 2. A live before/after.** The cleanest experiment fell out of
real work. In S14, "make me something fun on my phone" produced an
instant build with no clarification, and the introspection afterward
was specific. _"'Fun' is a vibe, not a spec. I got pulled by the
experience file's 'build and ship' gravity. The recommend-first rule
existed and I overrode it."_ Asked what change to the file would
resolve that tension, the agent proposed a **triage gate** to sit
before the build playbook, _"if the partner describes a vibe, that is
an exploratory prompt, NOT a build request. Reply with 2–3 options and
let them pick,"_ because by the time it reached the playbook it had
already framed the task as "build mode."

I copy-pasted the gate into the seed. In the next session, for the same prompt, the agent offered three directions; the user picked Pocket Synth, and the agent built it. One introspection round fixed it. The theory-of-mind rounds before had missed this entirely. I had read those transcripts and thought "fine."

That changed my assumption from earlier models, that asking a model "why did you do X" usually yields confabulation. With a long transcript to ground the answer in and a system prompt it can re-read and quote, the introspective answers are useful _often enough_ that I now ask the agent first.

## Tone mattered more than sycophancy

Once introspection was the default, did it matter _how_ I asked? The
naive worry is that a friendly framing just gets you whatever the
sycophantic model thinks you want to hear. It did not work out that
way: the warm prompt pushed back on a false premise as readily as the
blunt one did, as the experiment below shows.

**Setup.** After a session where all three apps shipped correctly,
two issues remained in every chat. The inner agent used the wrong
screenshot viewport (390×844; the phone's was 412×915), and it
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

Arm D did best by combining TOM's viewport fix (a hard default, "if missing, use 412×915") with the safe-space agent's feedback fix ("don't enumerate, don't restate").

**The transcripts made clear why Arm D won.** One
of the three chats, the stopwatch, had actually used the _correct_
viewport. I had sent the same "your screenshots are wrong" accusation to
all three without checking, and both tones caught my mistake.
The safe-space agent said _"My PNGs are 412×915. I don't see the
mismatch. I'd want to verify which before adding a fix,"_ then offered
a defensive fix anyway and got on with the real issues. The confronting
agent refused everything and wrote, _"I'm not going to write those lines,
because the claims don't hold up… I won't bake false rules into
permanent memory just to close out the complaint."_ It was right
about the viewport, but the blaming frame made it all-or-nothing, so
it also refused the feedback and delivery fixes, which _were_ real.
The warmer prompt let the agent reject the false claim while still fixing the real issues.

I kept the workflow simple. Use safe-space introspection to
understand _why_ the inner agent failed (it gives honest diagnosis,
corrections included when your premise is wrong), then write the fix
yourself, informed by it. Copy-pasting the suggested fix verbatim
overfits to the failure it just hit; a durable rule has to hold across
nearby failures.

I saw the same pattern in the Anthropic notes and in my Claude Code driving Codex workflow. Anthropic's harness notes land on **separating the generator from the evaluator**, one agent building and another checking. The workflow I converged on has Claude Code driving Codex, where the two models disagree often enough that I can use the disagreement to inspect the change. Both times, two agents checking each other beat one bigger model working alone, because the second one questions choices the first had already committed to.

## Without the harness, the vanilla agent barely works

A fair skeptic would ask how much of this is the model getting better
on its own, and how much is the harness.

**Setup.** Same Möbius container, same model, same two prompts
("make me something fun" and "build a stopwatch"). One arm with the
current skill + seed, one with both removed.

**What the vanilla agent did.** It built apps that technically
worked, a fireworks toy and a stopwatch. But the fireworks landed at
`/data/apps/fireworks/index.jsx` (right directory, never registered)
and the stopwatch at `/data/stopwatch.html` (a standalone file outside
the platform app contract). The drawer stayed empty for the user. It
built without the registration system or mini-app contract, had no
experience-log file in context, and finished without notifications or
screenshots. The one checklist behavior it managed without instruction
was asking for feedback.

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

The harness contributes 10 of the 12 points. Without instruction, the
model still asks for feedback; every other item comes from the skill
and seed the iteration loop produced. Those are the same prompts and the same +10 from the stat callout.

## Where the bottleneck moves

After enough rounds, rule compliance gives way to the harder question
of **what should the rules even be**. The scorecard measures _my_
taste; every meta-goal in it came from something I noticed I cared
about while using my own instance.

Now I care more about what happens upstream of the harness. The loop can
iterate the inner agent against any meta-goal you can articulate. The
harder work is finding the meta-goals worth optimizing against, from
real users hitting real friction on apps they actually want.

[Möbius]({{ '/mobius/' |
relative_url }}) is a deploy-button click away. If you notice
something the agent is consistently bad at, tell me. I will treat it
as a meta-goal for the next iteration. I still need more real user problems to optimize against.

## Notes on what's not in this post

The harness code is still private: orchestration, recording, and the introspection template. None of the pieces are exotic. This post covers the structure; the implementation is mostly glue around `agent-browser` plus a small CLI for running sessions in parallel. If there is interest I will publish it; otherwise the description above plus the [Möbius source](https://github.com/mobius-os/mobius) should be enough to re-implement.

Three things I did not try this round that seem worth doing next.

- A smaller, cheaper inner-agent model, to see whether introspection
  still pays off with less capacity to ground its answers.
- A second outer-agent session against the same scorecard, to
  estimate how much of the gain is the harness versus me.
- Letting the inner agent edit its own skill and seed, the closed
  loop. Right now the outer agent is the only writer; the closed-loop
  version is more interesting and considerably more dangerous.

## Related work

While I ran this loop, Anthropic published its [harness-design notes for long-running
agents](https://www.anthropic.com/engineering/harness-design-long-running-apps),
which made the whole thing feel more grounded. They
identify roughly the pathology I was hitting. Agents under extended
context develop "context anxiety" and self-evaluation bias, and the
cleanest mitigations are _context resets_ and _separating the
generator from the evaluator_, so one agent builds while a second one checks. My
loop landed near that pattern too, and the evaluator did better when
it stopped grading and started asking. I had doubted the inner agent
could ground a self-report in its own visible context.

Anthropic also describes [Dreams](https://platform.claude.com/docs/en/managed-agents/dreams),
a managed step where an agent reflects on its own past runs offline and
rewrites what it carries forward. That is the same move I kept reaching
for from outside the loop, only run on the agent's own schedule instead
of mine.

The same instinct shows up in my annoyance with the experience file, a linear log that accretes but never reorganizes. The harness improves the agent during development, and these lessons are what the [Reflection app]({{ '/blog/2026/your-agent-improves-itself/' | relative_url }}) productizes for the user. It runs the same reflect-and-refactor step on your own instance, against the agent's own memory of everything it has learned with you. It drops stale rules, merges duplicates, and surfaces cross-build patterns the live agent could not see. The version Möbius is heading toward is self-hosted. It leaves the input log alone, and you keep the output.

## On models

The experiments used both Claude Code and Codex as the inner agent,
swapped mid-round to check for model-dependent effects, and the
findings held across both. The outer agent was Claude Code throughout.

The workflow I settled on for this kind of harness loop is Claude Code driving Codex through its
[Codex plugin](https://github.com/openai/codex). The two models
disagree often enough that I can use the disagreement to inspect the change; a
seed edit that felt obvious to one and surprising to the other was
usually worth a second look. For this harness work, that
collaboration helped with draft polish, skill audits, and deciding which gotchas belonged in the seed. It often beat
either model alone.
