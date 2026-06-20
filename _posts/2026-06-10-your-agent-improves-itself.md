---
layout: post
title: Your agent improves itself, while you sleep
date: 2026-06-10 12:00:00
description: Memory is the agent's knowledge graph of what it has learned about working with you, and Reflection is the nightly loop that tidies it, anticipates what you will need, and reviews your instance for weak spots, all on your own server.
thumbnail: assets/img/mobius/covers/cover-post4.jpg
thumbnail_2x: assets/img/mobius/covers/cover-post4-2x.jpg
categories: software
keywords: self-hosted AI agent, agent memory, knowledge graph, nightly agent loop, self-improving AI, Möbius, Memory, Reflection, Claude Code, Codex
giscus_comments: true
related_posts: false
published: true
---

<details class="tldr">
<summary><strong>TL;DR.</strong> The <a href="{{ '/blog/2026/the-self-improvement-harness/' | relative_url }}">second post</a> was about how the developers make the agent better. Here, the agent starts improving itself for you, on your own instance, while you sleep. Two pieces make that work: <strong>Memory</strong>, a knowledge graph of the lessons the agent has picked up working with you, kept separate from your transcripts, and <strong>Reflection</strong>, a nightly loop that reviews the day and tries to be more useful tomorrow.</summary>

<ul>
<li><strong>Memory</strong> is the agent's knowledge graph. It holds what the agent has learned about building, about the platform, and about working with you, organized as a browsable graph instead of a chat log.</li>
<li><strong>Reflection</strong> runs overnight. It tidies and reorganizes Memory, anticipates what you will need next, suggests apps and features worth building, and reviews your instance for weak spots, then leaves a one-page morning brief.</li>
<li><strong>The tie-back.</strong> Reflection is the harness from the last post, built in. The reflect-and-refactor loop the developers ran by hand now runs on your instance, against the agent's own memory, on your schedule and your model.</li>
<li><strong>Honest edges.</strong> Memory and the nightly loop are shipping now. Several of the things a reflection run can produce are wired but still shallow, and I say which ones.</li>
</ul>

</details>

This is the fourth post about [Möbius]({{ '/mobius/' | relative_url }}),
a personal AI agent you self-host. The
[first]({{ '/blog/2026/mobius-an-app-that-builds-itself/' | relative_url }})
is about the agent building the tools you ask for. The
[second]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }})
is about the loop the developers run to make it better at that. The
[third]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }}) is
about the app store and the cross-app system those builds grew into.
This one is about the part of Möbius that improves itself for you.

The second post described work I do. I sit on my host, run the agent
through scenarios, ask it why it did what it did, and rewrite its
instructions between sessions. That loop lives outside your instance, and
you never see it. I want to talk now about the version of that loop that
runs _inside_ your instance, on your data, on your schedule, with the
agent watching its own work. You go to bed, and your copy of Möbius
spends part of the night trying to be a little more useful to you by
morning.

Two pieces make that work: a memory worth improving and a loop that keeps
improving it.

## Memory, the agent's knowledge graph

Most assistants keep your chat history and call that memory. A
transcript records what was said, in order, forever. Searching it is
slow, it never reorganizes, and the longer it gets the less the agent can
hold in view at once. Ask such a system what it knows about you and it
has to re-read conversations and infer the answer.

Möbius keeps the lessons separately. As the agent works, it writes down what
it _learns_, and those lessons live in **Memory**, a knowledge graph that
sits apart from any transcript. Notes link to related notes, the
important ones are indexed, and the indexed core is small enough to load
into the agent's context at the start of a session, even as the full
graph grows past what would fit. The nightly tidy-up keeps that core the
right size, so the agent loads the lessons that matter and leaves stray
notes outside the starting context. Instead of re-reading ten
conversations to remember a gotcha it hit last week, the agent reads one
note.

Memory holds what the agent has learned about doing its job, including
doing that job _for you_. A note might say that a certain compile step
fails silently if you skip a flag, or that the offline cache needs
priming a particular way, or that when you say "make it cleaner" you
usually mean denser rather than more whitespace. The first two are
platform craft. The third is about you, and the agent keeps it the way a
good collaborator remembers how you like things.

<figure class="mb-diagram">
  <div class="mb-flow">
    <div class="mb-node">
      <span class="mb-node__title">Transcripts</span>
      <span class="mb-node__sub">every word, in order, forever; slow to search, never reorganized</span>
    </div>
    <span class="mb-arrow">→<span class="mb-arrow__label">the agent distills lessons</span></span>
    <div class="mb-node accent">
      <span class="mb-node__title">Memory</span>
      <span class="mb-node__sub">a graph of what was learned, linked and indexed, kept apart from the chat log</span>
    </div>
  </div>
  <figcaption>The transcript is the raw record, and Memory is the distilled, reorganizable layer the agent actually reasons from. Keeping them separate lets the memory get tidied without ever touching what was said.</figcaption>
</figure>

Because it is a graph of markdown notes on your server, you can browse
it. The **Memory** app, one of the starter-pack apps from the
[last post]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }}),
renders it as an Obsidian-style web of nodes and links. You can open it,
see what the agent thinks it knows, follow a thread from one lesson to a
related one, and read any note in full. The notes are a folder you own,
and the app is a window onto it.

This answers the itch I described at the end of the harness post. The
old experience file was a flat log that only grew. It accreted and never
reorganized, so the useful lessons sank under the one-off ones, and
rules that had stopped mattering stayed at full weight forever. A graph
fixes the _shape_ of the memory, but it still needs upkeep, and
Reflection handles that part.

## Reflection keeps it fresh

Every night, on a schedule you set, Möbius reflects. The **Reflection**
agent wakes up while you are away from the system, reviews the day, and
works to be more useful to you tomorrow. It is a scheduled agent like
any other on the platform, a background job that runs the coding agent
with a particular brief, and that brief covers the instance as a whole.

A reflection run leaves a one-page brief after four checks.

**It tidies Memory.** I trust this part most, it's the harness move I've
seen work. The nightly run reads the current memory and the day's
transcripts and produces a _revised_ memory with duplicate notes merged,
stale ones dropped, scattered observations about the same thing pulled
into one place, and fresh cross-cutting patterns surfaced as new notes.
It leaves the transcripts alone and rewrites the distilled layer on top
of them. Tomorrow's agent starts from a memory that is a little cleaner
than today's. The same cleanup I do between harness sessions now runs on
its own schedule.

**It anticipates what you will need next.** Having read the day, the
nightly run can notice a pattern and get ahead of it. If you have been
logging workouts every morning, it can prime the things that make
tomorrow's log instant. If you keep asking the same kind of question, it
can note that a small tool would answer it for you. I am careful with
this one because it can sound creepier than it is. Noticing patterns and
writing notes works today. The loop takes only small, reversible action
ahead of time, because a system that rearranges your morning based on a
guess is worse than one that waits to be asked.

**It suggests apps and features worth building.** A reflection run that
has seen you reach for the same workaround three times can write down
"you keep doing X by hand; an app would do it for you" and surface that
as a suggestion the next morning. Actual building stays in the loop from
the first post, with you asking the clarifying questions and approving
the result. The run brings you the idea and leaves your code alone.

**It reviews your instance for weak spots.** The agent has write access
to its own shell, themes, app source, and schedules, which means it can
also _read_ all of those. A reflection run can look for a theme rule
that hurts contrast, a scheduled job that has been failing quietly, an
app whose data is growing in a way that will bite later, or a place
where the shell has drifted. This is the weakest piece today. The hooks
are there and the agent can read every one of those surfaces, but the
review itself runs closer to a checklist than the deep self-review I want
it to become.

<figure class="mb-diagram">
  <div class="mb-cycle">
    <div class="mb-node">
      <span class="mb-node__lead">you · asleep</span>
      <span class="mb-node__title">The day's work is done</span>
      <span class="mb-node__sub">chats, builds, and edits from today sit in the transcripts and Memory</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">a scheduled job wakes the agent</span></span>

    <div class="mb-node accent">
      <span class="mb-node__lead">Reflection · overnight</span>
      <span class="mb-node__title">Review the day, work to be more useful tomorrow</span>
      <span class="mb-node__sub">tidy Memory · anticipate what you'll need · suggest apps and features · audit the instance</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">a revised memory and a short list of suggestions</span></span>

    <div class="mb-node">
      <span class="mb-node__lead">you · awake</span>
      <span class="mb-node__title">A sharper agent and a few things worth a look</span>
      <span class="mb-node__sub">tomorrow's sessions start from a cleaner Memory; suggestions wait for your yes</span>
    </div>

    <div class="mb-loopback">
      <span class="mb-loopback__glyph">↺</span>
      <span>each night's tidy-up is the input to the next night's &nbsp;→&nbsp; the memory gets cleaner and more useful each night</span>
    </div>

  </div>
  <figcaption>The nightly loop, end to end. The day fills Memory, the nightly run distills it and looks ahead, and you wake to a cleaner memory and a short list of things the agent thinks are worth building or fixing. Everything it changes overnight is committed to a history you can walk back, and anything new or risky waits for your yes in the morning.</figcaption>
</figure>

All of this can run unattended because the whole system treats breaking
as reversible. A reflection run commits its changes to the same git
history everything else does, so a bad night's reorganization is
something you can read back and undo, and it never touches the input it
works from, your transcripts. The run produces a new memory beside the
old one, and the old one stays recoverable. That is why I can let it
rewrite memory overnight.

## The harness moves inside

The harness from the [second post]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }})
now runs inside the instance.

In the harness, the developers run a reflect-and-refactor loop on the
agent by hand. An outer agent watches the inner one work, asks it why it
did what it did with the transcript still in context, and rewrites its
instructions between sessions. The loop worked because of two findings.
An agent reflecting on its _own_ recent experience self-corrects better
than a bigger agent reasoning from outside, and the right move is usually
to _remove and reorganize_ rules, because a memory that only grows
competes with itself.

Reflection uses both findings, with the agent running the loop on itself.
It reflects on its own day with the transcript right there in context,
where introspection beat an outside agent's guesswork in my tests. The
core operation refactors an existing memory by merging duplicates,
dropping rules that stopped firing, and surfacing patterns that span
several builds. In the harness experiments, repeated cleanup made later
runs better. Reflection runs the same move, scheduled, on your instance,
on your behalf.

Reflection carries only one of the harness's two mechanisms. The harness
paired an outside agent cross-checking the inner one with the inner
agent's own introspection. At 3am only the introspection half runs, and
the agent grounds a self-report in the day it has had. The experiments
showed that this half does real work, which is why Reflection tidies its
own memory well. Its review of the rest of the instance is still shallow,
and the deep self-review still needs a second vantage.

<blockquote class="pull-quote">
The same reflect-and-refactor loop the developers run by hand now runs on your own instance, against the agent's own memory, on your schedule and your model.
</blockquote>

This nightly loop runs on almost exactly the contract behind Dreams, the
primitive Anthropic shipped for managed agents while I was building the
harness. A dream reads a memory store and past transcripts and produces a
fresh store beside them, with duplicates merged and stale entries
replaced. The input stays intact, so you can review the result and keep
or discard it. Möbius runs that contract self-hosted, on your own
scheduler and model and a graph you own.

Here, self-hosting changes the trust model. A self-improving agent in
someone else's cloud keeps your memory and your nightly review on their
machine, and Möbius keeps them on yours. The nightly run lives in the same
container as everything else, reads from `/data` on your server, and
writes back to it. Your memory and your transcripts stay there. The one
thing that leaves the box is the prompt context each run sends to whatever
model you have configured, the same as any chat does, unless you point it
at a local one. The agent gets sharper about you specifically, and the
record of that is a folder you can read, back up, or delete.

## What has shipped and what is still shallow

The split today is simple.

Memory is shipping now, a live knowledge graph. The agent reads from
it at the start of every session, jots lightweight notes as it works, and
leaves the heavier consolidation to Reflection at night. The Memory app
renders the whole thing as a browsable web of notes. The three-layer
memory it sits in, a curated constitution, an editable set of skills, and
the graph itself, is the live model on every instance.

Reflection is shipping now as a scheduled agent, and the first of its
four jobs, tidying Memory, is the strongest one. The other three are
uneven. Anticipating your needs is mostly note-taking today; it observes
and records well, and acts ahead of time only in small, reversible ways.
Suggesting apps is wired but quiet, and gets better the more the agent
has seen you do. The instance audit is the least mature. The agent can
read every surface it would need to review, but the review itself is
shallow, and that is where I am spending effort next.

I would rather tell you that than pretend the whole nightly loop already
does everything described here. Each job uses the same reversible
workflow as it gets deeper. It reads the day, proposes a change beside
the old state, and commits it to a history you can walk back. The
remaining work is depth; the loop itself is already running.

## Where this goes

Across the series, the agent has moved outward from building tools into
maintaining the system around them. The first three posts added
capability, tooling, and a reshaping mechanism for the app store. This
post moves the _improvement_ loop itself onto your instance. The agent
that builds your tools now also tends its own memory of how to build
them, on your server, while you sleep.

I actually want this version of a personal assistant. Most of them get
more generic the longer you use them, tuned to keep you engaged, with
their memory of you locked in someone else's cloud. I want one that
learns your preferences and keeps that record where you can inspect it,
on hardware you own.

[Möbius]({{ '/mobius/' | relative_url }}) is a deploy-button click away,
the source is on [GitHub](https://github.com/mobius-os/mobius), and the
apps are under [`mobius-os`](https://github.com/mobius-os). Deploy one,
use it for a week, and open the Memory app some morning to see what your
agent learned overnight.
