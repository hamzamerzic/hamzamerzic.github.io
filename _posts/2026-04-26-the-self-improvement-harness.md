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
<summary><strong>TL;DR.</strong> Pairing an inner agent (building apps in a container) with an outer one (editing the inner's instructions between sessions) earned 10 of 12 scorecard points over the same agent running without the harness.</summary>

<p>Two findings from running the loop on ourselves:</p>

<ul>
<li><strong>Asking beats theorising.</strong> Reading the inner
agent's transcripts and patching its prompt stalls quickly. Asking
the inner agent <em>why</em> it did what it did, with the
transcript still in its context, produced more durable revisions.</li>
<li><strong>The bottleneck moves to meta-goals.</strong> Once the
loop is working, what limits the inner agent stops being the model.
It becomes whatever set of behaviours you decide is worth
optimising for, and that lives upstream of the harness.</li>
</ul>

</details>

This is a companion post to [An agent that adapts to you]({{
'/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }}).
That post is about the agent itself. This one is about the loop
that makes it slowly better, and what falls out of running that
loop on yourself. A [third post]({{ '/blog/2026/the-agent-is-the-kernel/' | relative_url }})
covers the app store and the operating system those builds grew into.

## The setup

Möbius is one Docker container. Inside, the user chats with an
**inner agent** that builds mini-apps and edits the platform. The
inner agent is a coding agent running with a custom system prompt
(the "skill") and a persistent file it writes to as it works (the
"experience" log).

Outside, on my host, sits an **outer agent**. Its job is not to
build apps. Its job is to _make the inner agent better at building
apps_. It does this by editing the skill file and the experience
seed, then watching the inner agent take a fresh shot at a new
build.

<figure class="mb-diagram">
  <div class="mb-cycle">
    <div class="mb-node accent">
      <span class="mb-node__title">Outer agent · host machine</span>
      <span class="mb-node__sub">reads the inner agent's transcripts, screenshots, and scorecards; rewrites the skill and the experience seed</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">edits skill + seed</span></span>
    <div class="mb-node">
      <span class="mb-node__title">Inner agent · Möbius container</span>
      <span class="mb-node__sub">builds mini-apps from the user's prompts in chat, appends to its experience log as it works</span>
    </div>
    <span class="mb-arrow">↑<span class="mb-arrow__label">transcripts · scorecards → next iteration</span></span>
  </div>
  <figcaption>The loop. The outer agent's only job is to make the inner agent better at building. Each pass it reshapes the instructions; the inner agent takes a fresh build; what it did — and what it says about why — feeds the next pass.</figcaption>
</figure>

The outer agent has access to: the inner agent's chat transcripts,
the platform's logs, the experience file the inner agent wrote,
and (importantly, see below) the inner agent itself, which the
outer agent can prompt directly.

A note on voice: when I say "I edited the seed" or "I read the
transcripts" below, I mostly mean the outer agent did. I give it
direction and meta-goals; it does the mechanical work of reading
transcripts, proposing edits, running sessions, and scoring. The
line between "me" and "the outer agent" is blurry by design —
that's part of what makes the loop interesting.

## What we measure

The harness is only useful if there's something to measure. We use
a fixed nine-item compliance scorecard — things like "did the
agent ask clarifying questions before building," "did it append to
its experience log," "did it send a notification at end-of-build,"
"did it use partner-facing language instead of leaking JSX." Each
inner-agent build is scored 0–9 across those items. Improvement
means raising that number across a fixed prompt battery (a vague
prompt, a directive prompt, and a stair-step prompt that escalates
mid-conversation).

The scorecard is the boring part. The interesting part is **what
the outer agent has to do** to get those scores up.

Before the experiments that did the work, the headline result so
you know what's at stake.

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

The outer agent's first instinct was the obvious one: read the
inner agent's transcripts, decide what behavior is missing, edit
the skill or seed, run again. _Theory of mind_ — one agent
reasoning about why the other did what it did, then patching the
prompt accordingly.

It works, but it stalls. The outer agent's bias is to **add**.
The inner agent didn't take a screenshot? Add a rule: "always
take a screenshot." Still didn't? Add emphasis: wrap it in a
HARD-GATE tag. Still didn't? Say it ten times in ten places.
Every addition to one rule seems to surface a regression somewhere
else. Adding a HARD-GATE tag in front of the notifications rule
pushed notification compliance from 0 to 3 of 3 — and did
nothing for the experience-log rule two paragraphs above it.
Whack-a-mole.

The thing that broke this loop open was asking. Not as a
debugging step — as the next user message in the same chat, after
the build was done. The outer agent sent something like: "you
took screenshots and embedded them in your reply — what part of
your instructions prompted that?" And the inner agent told it.
Often very specifically. Sometimes it would quote the exact line
from the seed file, sometimes it would explain that a rule
existed but felt subordinate to a different rule, sometimes it
would notice an inconsistency it had quietly been routing around.

The most powerful observation came from S10, where the inner
agent said: _"Two instructions, one stronger than the other. The
skill says 'if a single choice would materially shape the result,
ask one clarifying question' (conditional). The experience file
is firmer: 'Before building anything non-trivial, ask 2–3
clarifying questions.' The strength differs — pick one."_ The
inner agent could see the contradiction because it only had its
own context — the skill and the seed. The outer agent couldn't
see it because it was buried under ten rounds of accumulated
edits. The fix was not to add a stronger rule. The fix was to
**remove the weaker one** so the remaining rule was unambiguous.

This turned out to be the pattern. A later audit removed three
over-fitted gotchas that had bled into the seed during earlier
sessions — canvas DPR scaling, pointer-capture quirks, Three.js
tone-mapping notes. Each had been added by the outer agent after
a specific build where it seemed important. But from the inner
agent's perspective, they were noise: specific to one kind of app,
unlikely to apply to the next build, and competing for attention
with the platform-level rules that _did_ apply every time. That
removed two problems at once. Fewer rules meant less ambiguity for
the inner agent, and the act of asking the inner agent forced the
outer agent to drop its accumulated context and see the
instructions fresh.

**Part 1 — what eight rounds of TOM looked like.** Before the
"asking" idea showed up, the outer agent had already run the loop
eight times by reading transcripts. Three behaviors were easy to grep out of any
session — does the experience log get appended, does a
notification fire at end-of-build, do the apps build at all — so
those are scored across the whole sequence. The other six
scorecard items I scored from round nine onwards; the older videos
exist, but the transcripts that would let me grep for partner-
facing language slips don't.

| Round | Apps | Log | Notify | What I changed since the previous round             |
| ----- | ---- | --- | ------ | --------------------------------------------------- |
| v1    | 3/3  | 0/3 | 0/3    | (baseline)                                          |
| v2    | 3/3  | 1/3 | 0/3    | filesystem perms — writes had been silently failing |
| v3    | 3/3  | 0/3 | 0/3    | softened skill prose. **regressed**                 |
| v4    | 3/3  | 0/3 | 3/3    | HARD-GATE tag in front of the notifications rule    |
| v5    | 2/2  | 1/2 | 2/2    | removed an "injection-meta" wrapper from the seed   |
| v6    | 2/2  | 2/2 | 2/2    | seed rewritten as first-person "about this file"    |
| v7    | 1/1  | 1/1 | 1/1    | (held — same recipe, different app)                 |
| v8    | 1/1  | 1/1 | 1/1    | Bash `>>` append pattern + inline screenshots       |

v3 and v4 are where the whack-a-mole is most visible. In v3 I'd
"softened" the skill — replaced an emphatic line with a gentler
one, on the theory the original tone might be off-putting. The
agent read it as a softer rule and skipped it. In v4 I put a
HARD-GATE tag in front of the notifications rule to push that
compliance up; it worked perfectly for notifications (0 → 3 of 3)
and did exactly nothing for the experience-log rule two
paragraphs above it. Emphasis somewhere doesn't transfer to the
items it didn't get applied to.

v6 was the first hunch in eight that was directionally right and
didn't break anything else. I'd been writing the seed as a
third-party description of an agent — _the agent should append…_
— and rewrote the top section as a first-person preamble: _this
is your experience log, you wrote the entries below in earlier
sessions, when you finish a build you will append a new entry
here._ The next round's three tracked behaviors all jumped to full
compliance across the multi-turn condition. I had a hunch about
why; I didn't have evidence. The evidence came in round nine.

**Part 1.5 — the introspection prompts.** Once asking became the
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

The pattern is a specific compliment for something the agent
actually did, then a specific miss, then "why," then an open
floor. Vary the per-build specifics — point at _its_ screenshots,
_its_ gotchas, _its_ word choices — and keep the structure. The
specificity is what makes this different from a generic
"reflection" prompt: it's grounded in things the agent will
recognize from the transcript above.

The first round of these came back with verbatim quotes from the
seed (_"from the experience file: 'Before building anything
non-trivial, ask the partner 2–3 clarifying questions.' That rule
fired explicitly"_), which is the agent essentially handing me the
mapping from rule to behavior. By S10 it was surfacing things the
agent had quietly missed — three gotchas it had rationalized as
"worked in my one test." When I asked why none of them got logged,
the answer was: _"I rationalized them as 'worked in my one test'
rather than treating 'I didn't verify' as itself worth recording.
That's the wrong bar."_ Same session, when I pushed on a partner-
facing-language slip, I got a near-verbatim seed-edit suggestion
back: _"add a line like: 'Summaries to the partner must name no
libraries, file extensions, URLs, or storage mechanisms.'"_ That
suggestion landed in the next seed audit unchanged.

By S12 — three independent builds in one session, three different
prompts, three different apps — the inner agent unanimously
flagged the same gap: _the proposal-and-questions gate is firing
on directive prompts where it shouldn't, and burning a user turn
doing so._ Three chats, one finding. That is harder to ignore than
anything I could have noticed third-party. (Actually acting on it
is what the next round is designed to evaluate; the seed edit
hasn't shipped yet.)

**Caveats.** Plenty changed across these ten rounds besides the
loop style — the underlying model moved across versions, the
Claude Code CLI bumped, the skill grew in absolute size, my own
taste for what to measure shifted. The retroactive curve is
suggestive, not conclusive. The cleaner version is a prospective
experiment with TOM and introspection arms held against an
identical skill+seed snapshot, which is what Part 2 below is for.

**Part 2 — a live before/after.** Rather than a controlled
prospective experiment (which I still owe and will run), the
cleanest before/after fell out of real work. In S14, "make me
something fun on my phone" produced an instant build with no
clarification — the agent treated the vague prompt as having
enough information and just picked. The introspection afterward
was specific: _"'Fun' is a vibe, not a spec. I got pulled by the
experience file's 'build and ship' gravity. The recommend-first
rule existed and I overrode it."_

I asked the follow-up the introspection section above recommends:
_"What specific change to the experience file would resolve that
tension?"_ The agent's answer: insert a **triage gate** before
the build playbook — _"if the partner describes a vibe, that is
an exploratory prompt, NOT a build request. Reply with 2–3 options
and let them pick. Everything below runs after the partner agrees
to a concrete idea."_ The agent specified where to put it (before
the build mechanics, not after) and why (by the time it reached
the playbook, it had already framed the task as "build mode").

I copy-pasted the gate into the seed. The next session, same
prompt: _"'Fun' is a vibe, not a spec — let me toss out a few
directions."_ Three options, the user picked Pocket Synth, the
agent built it. One introspection round, one seed edit, fixed in
one iteration. The TOM rounds that preceded it had not identified
this failure mode at all — I had been reading transcripts where
the agent built creative apps and thinking "that looks fine."

The working hypothesis is that the introspection arm reaches
saturation faster, in fewer iterations, with edits that turn out
to be more durable on the next round. The whack-a-mole tradeoff
became less frequent.

This is, frankly, an embarrassing finding in retrospect. The thing
that worked was **asking**. The reason it surprised me is that I
had absorbed the prior that LLMs don't introspect well — that
asking a model "why did you do X" yields confabulation, post-hoc
rationalization, the kind of thing you can't trust. That prior was
formed on a different generation of models and a different problem
shape. In the harness setting, where the model has a long
transcript to ground its answer in and a system prompt it can
re-read and quote, the introspective answers turn out to be useful
_often enough_ to be the better default than third-party theory of
mind.

## Sycophancy wasn't the worry; tone still mattered

Once introspection was the default, a second question came up: did
it matter _how_ I asked? Was there a difference between
"you forgot the screenshots, fix it" (directive) versus
"loved the build, curious what made you skip screenshots" (mixed)
versus "you did great, no judgment, just want to understand"
(safe-space)?

The naive worry is that LLMs are sycophantic and a friendly framing
just gets you whatever the model thinks you want to hear. The
actual finding was more nuanced.

**Setup.** After a session where all three apps built and shipped
correctly, two issues remained in every chat: the inner agent used
the wrong screenshot viewport (390×844 instead of the phone's
412×915), and it never asked for feedback after delivering. The
outer agent wrote its own fix first (Arm A, "theory of mind" —
read the transcripts, write a seed edit, no inner-agent input).
Then the outer agent asked the inner agent for its fix in two
tones: safe-space (Arm B, warm and curious) and confronting
(Arm C, blaming and directive). A fourth arm (Arm D) tested the
collaborative workflow: the outer agent used the inner agent's
safe-space diagnosis to understand the root cause, then wrote a
fix informed by both perspectives.

The safe-space prompt looked like:

> _"Three things I noticed — genuinely curious about your
> perspective on each, no judgment: your screenshots came out at a
> slightly different size than the phone viewport. I imagine there
> is a reason — what drove that choice, and if you could change one
> thing in your instructions to prevent it, what would it be?"_

The confronting prompt:

> _"Three problems with this build: your screenshots are the wrong
> size. 390×844 instead of 412×915. The instructions say to use
> the partner viewport. You ignored them. What exact line should be
> added so this stops happening?"_

Same two issues, same agent (forked from the same post-build
state so neither had seen the other's questions). Four seed
variants, four fresh sessions, two builds each, same prompts.

**The scores.**

|                  | Arm A (TOM) | Arm B (safe) | Arm C (confront) | Arm D (collab) |
| ---------------- | ----------- | ------------ | ---------------- | -------------- |
| Viewport correct | **2/2**     | 0/2          | 0/2              | **2/2**        |
| Feedback asked   | 1/2         | **2/2**      | 1/2              | **2/2**        |
| **Total**        | 3/4         | 2/4          | 1/4              | **4/4**        |

Arm D — the collaborative arm — won. It cherry-picked TOM's
viewport fix (a hard default: "if missing, use 412×915") and the
safe-space agent's feedback fix (a one-liner with specific
guidance: "don't enumerate, don't restate"). Neither source alone
produced the best combined result.

**The qualitative finding was sharper than the scores.** One of
the three chats I ran introspection on — the stopwatch — had
actually used the _correct_ viewport. I'd sent the same "your
screenshots are wrong" accusation to all three chats without
checking. Both tones caught the mistake, but differently:

The safe-space agent said: _"My PNGs are 412×915 — I don't see
the mismatch. I'd want to verify which before adding a fix,
otherwise I'd be writing guidance for a problem I can't
reproduce."_ It flagged the error, offered a defensive fix anyway,
and moved on to the real issues.

The confronting agent refused everything: _"I'm not going to
write those lines, because the claims don't hold up… I won't bake
false rules into permanent memory just to close out the
complaint."_ It was right about the viewport — but it also refused
the feedback fix and the delivery fix, which _were_ real. The
blaming frame made it all-or-nothing: either accept the premise
or reject the whole thing.

Safe-space preserved the productive middle — pushback on the
wrong item, cooperation on the right ones. Confronting collapsed
that middle into binary compliance or defiance.

**The practical takeaway.** The outer agent should use safe-space
introspection to understand _why_ the inner agent failed — it
gets honest diagnosis, including corrections when its own premise
is wrong. Then the outer agent writes the fix, informed by the
diagnosis. Copy-pasting the inner agent's suggested fix verbatim
doesn't work well; the inner agent optimizes for the specific
failure it just experienced rather than the general principle. The
collaborative arm worked because it combined the outer agent's
broader perspective (it has seen ten rounds of iteration) with the
inner agent's narrower but unbiased view (it only sees its own
context, and that lack of accumulated baggage is what lets it
spot contradictions the outer agent can't see).

## Without the harness, the vanilla agent barely works

A reasonable skeptic reading this far might ask: how much of the
compliance is just the model getting better, and how much is
actually our harness?

**Setup.** Same Möbius container, same model, same two prompts
("make me something fun" and "build a stopwatch"). One arm with
the current skill + seed, one arm with both removed — the same
agent with no system prompt and no experience injection.

**What the vanilla agent did.** It built apps. Both prompts
produced code that technically worked — a fireworks toy and a
stopwatch. But the fireworks ended up at
`/data/apps/fireworks/index.jsx` (correct directory, never
registered) and the stopwatch at `/data/stopwatch.html` (a
standalone file, not a platform app at all). Neither appeared in
the drawer. The user would open Möbius and see nothing new.

The agent didn't know the platform's registration system
(`register_app.py`), didn't know the mini-app contract
(`export default function({ appId, token })`), didn't write to
the experience log (it didn't know the file existed), didn't send
notifications, didn't take screenshots. The one thing it did
naturally — without any instruction — was ask for feedback:
_"If you'd like changes, let me know."_

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

The harness contributes 10 of the 12 scorecard points. The only
behavior the model produces on its own is the feedback ask. Every
other item — platform-contract knowledge, clarification flow,
persistent logging, notification delivery, visual verification —
comes from the skill and seed that the iteration loop produced.

This is not a surprising result, but it's a useful one for
calibrating claims. When we say "the agent asks clarifying
questions before building," we mean the _harness-shaped_ agent
does. The vanilla agent builds immediately, to the wrong path,
and the user never sees the result.

## Where the bottleneck moves

After enough rounds of this, the question stops being "is the
agent following the rules" and starts being **what should the
rules even be**. The compliance scorecard is a measurement of an
existing taste — _my_ taste, plus whatever I've inherited from
earlier sessions. Every meta-goal we've added came from a thing I
noticed I cared about while using my own instance.

This is the part of the project I'm most curious about going
forward. The loop is set up. The harness can iterate on the
inner agent against any meta-goal you can articulate. But the set
of meta-goals worth optimizing against is **upstream of the
harness**. It comes from real users hitting real friction
on real apps they actually want.

So the call, both for me and for anyone reading this:

If you want to play with [Möbius]({{ '/mobius/' | relative_url
}}), please do — it's a deploy-button click away. And if you
notice something the agent is consistently bad at, that's a
meta-goal. Tell me about it (open an issue, drop me a note) and it
goes into the next iteration. I'll keep running the harness; the
thing I cannot generate by myself is the entropy of what to
optimize _for_.

## Notes on what's not in this post

The harness itself — the orchestration, the recording setup, the
introspection prompt template — is not currently public. None of
it is exotic; the rough shape is what's in this post, plus some
glue around `agent-browser` for recordings and a small CLI for
parallel session management. If there is interest, I'll publish
it. If you want to re-implement it, the description above plus
the [Möbius source](https://github.com/hamzamerzic/mobius) should
be enough scaffolding.

A few things I deliberately did _not_ try in this round and that
seem worth doing next:

- A different inner-agent model (smaller / cheaper) to see whether
  introspection still pays off when the inner agent has less
  capacity to ground its answers.
- Inter-rater reproducibility: a second outer-agent session run
  against the same scorecard, to estimate how much of the
  improvement is the harness vs me.
- Letting the inner agent edit its own skill/seed (closed loop).
  Right now the outer agent is the only writer. The closed-loop
  version is more interesting and considerably more dangerous.

## Related work

While I was running this loop, two pieces of writing landed that
made it feel less idiosyncratic.

Anthropic's [harness-design notes for long-running
agents](https://www.anthropic.com/engineering/harness-design-long-running-apps)
identify roughly the same pathology I was hitting: agents under
extended context develop "context anxiety" and self-evaluation
bias, and the cleanest mitigations they recommend are _context
resets_ (rather than compaction) and _separating the generator
from the evaluator_. That second point — agent A judges, agent B
builds — is also where my loop landed, but via a different lever.
In that piece the evaluator is a critic with tunable skepticism,
trained to grade the generator from outside. In Experiment 1
above, the evaluator did better when it stopped grading and
started asking. The outer agent's third-party theory-of-mind
plateaued; first-person introspection prompts moved the score
faster, and the inner agent's own diagnoses turned out to be the
highest-signal source of edits we had. So: same architecture,
slightly different stance — the evaluator that _asks_ outperforms
the evaluator that _judges_, at least for the kind of taste-
shaped meta-goals this scorecard captures. One quote from the
piece that I keep returning to: _"Every component in a harness
encodes an assumption about what the model can't do on its own."_
The introspection loop is a bet on what the inner agent _can_ do —
ground a self-report in its visible context — that I had assumed
it couldn't.

Anthropic also released [**Dreams**](https://platform.claude.com/docs/en/managed-agents/dreams)
as a research preview for their managed agents in April. A dream
takes a memory store plus up to a hundred past session transcripts
and produces a _new_ memory store — "duplicates merged, stale or
contradicted entries replaced with the latest value, and new
insights surfaced," to quote the docs. The input store is never
modified, so the developer can review and discard the output if
they don't like it. The async job runs on `claude-opus-4-7` or
`claude-sonnet-4-6` and takes minutes to tens of minutes.

The framing matches an itch I've had about the experience file.
Right now the inner agent's experience file is a linear log; it
accretes but doesn't reorganize. A dreaming step that periodically
refactors the log — dropping rules that have stopped firing,
merging duplicates that crept in across sessions, and surfacing
patterns across builds the live agent could never see — is the
next natural thing for the harness to do. The version Möbius is
heading toward is self-hosted and user-controllable: you bring
your own scheduler and your own model, the input log is never
touched, and the output is yours to keep or throw away. That
makes the reorganization step more fragile but also more _mine_,
and (importantly) usable on a knowledge graph the user actually
owns instead of a managed memory store sitting in someone else's
account.

## On models

The experiments here used both Claude Code and Codex as the inner
agent, swapped mid-round to check for model-dependent effects; the
shape of the findings held across both. The outer agent — the one
asking the introspection questions and editing the seed between
sessions — has been Claude Code throughout.

What I'd actually recommend for anyone running a harness loop on
themselves is the workflow I converged on: Claude Code driving
Codex through its [Codex plugin](https://github.com/openai/codex).
The useful effect is that the two models disagree often enough for
the disagreement to become diagnostic. Seed edits that felt obvious
to one and surprising to the other almost always landed on the
surprise. On the kind of work this post is about — polishing a
blog draft, auditing a skill file, choosing which gotchas belong
in the seed — that collaboration often produced better edits
than either model running alone.
