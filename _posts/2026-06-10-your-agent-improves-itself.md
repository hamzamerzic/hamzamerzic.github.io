---
layout: post
title: Your agent improves itself, while you sleep
date: 2026-06-10 12:00:00
description: The Mind is the agent's memory of everything it has learned with you, and Dreaming is the nightly loop that tidies it, anticipates what you will need, and audits your instance, all on your own server.
thumbnail: assets/img/mobius/covers/cover-post4.jpg
thumbnail_2x: assets/img/mobius/covers/cover-post4-2x.jpg
categories: software
keywords: self-hosted AI agent, agent memory, knowledge graph, nightly agent loop, self-improving AI, Möbius, Mind, Dreaming, Claude Code, Codex
giscus_comments: true
related_posts: false
published: true
---

<details class="tldr">
<summary><strong>TL;DR.</strong> The <a href="{{ '/blog/2026/the-self-improvement-harness/' | relative_url }}">second post</a> was about how the developers make the agent better. This one is about how the agent makes itself better, for you, on your own instance, while you sleep. Two pieces do the work: the <strong>Mind</strong>, a knowledge graph of everything the agent has learned across every interaction and lesson, kept separate from your transcripts, and <strong>Dreaming</strong>, a nightly loop that reviews the day and tries to be more useful tomorrow.</summary>

<ul>
<li><strong>The Mind</strong> is the agent's memory, not a profile of you. It is what the agent has learned about building, about the platform, and about working with you, organized as a browsable graph instead of a chat log.</li>
<li><strong>Dreaming</strong> runs overnight. It tidies and reorganizes the Mind, anticipates what you will need next, suggests apps and features worth building, and audits your instance for weak spots.</li>
<li><strong>The tie-back.</strong> Dreaming is the harness from the last post, productized. The reflect-and-refactor loop the developers ran by hand now runs on your instance, against the agent's own memory, on your schedule and your model.</li>
<li><strong>Honest edges.</strong> The Mind and the nightly loop are real and shipped. Several of the things a dream can produce are wired but still shallow, and I say which.</li>
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
This one is about the part of Möbius that improves
itself for you.

Here is the distinction that matters. The second post described work I
do. I sit on my host, run the agent through scenarios, ask it why it
did what it did, and rewrite its instructions between sessions. That
loop lives outside your instance. You never see it. What I want to talk
about now is the version of that loop that runs _inside_ your instance,
on your data, on your schedule, with no one watching but the agent
itself. You go to bed, and your copy of Möbius spends part of the night
trying to be a little more useful to you by morning.

Two pieces make that possible. One is a memory worth improving. The
other is the loop that improves it.

## The Mind is the agent's memory, not a profile of you

Most assistants keep your chat history and call that memory. It is not.
A transcript is a record of what was said, in order, forever. Searching
it is slow, it never reorganizes, and the longer it gets the less the
agent can hold in view at once. Ask such a system what it knows about
you and it re-reads conversations and guesses.

Möbius keeps something different. As the agent works, it writes down
what it _learns_, and those lessons live in a structure separate from
any transcript. That structure is the **Mind**, a knowledge graph of
everything the agent has picked up across every interaction. Notes link
to related notes, the important ones are indexed, and the whole thing
is small enough to load into the agent's context at the start of a
session. So instead of re-reading ten conversations to remember a
gotcha it hit last week, the agent reads one note.

Here is the framing people get wrong. The Mind is the
agent's memory, not a dossier on you. It is not a list of your
preferences harvested to target you. It is what the agent has figured
out about doing its job, which happens to include doing its job _for
you_. A note might say that a certain compile step fails silently if you
skip a flag, or that the offline cache needs priming a particular way,
or that when you say "make it cleaner" you usually mean denser, not more
whitespace. The first two are platform craft. The third is about you,
but it is stored as a lesson the agent learned, the way a good
collaborator remembers how you like things, not as a profile sold to
anyone.

<figure class="mb-diagram">
  <div class="mb-flow">
    <div class="mb-node">
      <span class="mb-node__title">Transcripts</span>
      <span class="mb-node__sub">every word, in order, forever; slow to search, never reorganized</span>
    </div>
    <span class="mb-arrow">→<span class="mb-arrow__label">the agent distills lessons</span></span>
    <div class="mb-node accent">
      <span class="mb-node__title">The Mind</span>
      <span class="mb-node__sub">a graph of what was learned, linked and indexed, kept apart from the chat log</span>
    </div>
  </div>
  <figcaption>The split that makes the difference. The transcript is the raw record; the Mind is the distilled, reorganizable memory the agent actually reasons from. Keeping them separate is what lets the memory get tidied without ever touching what was said.</figcaption>
</figure>

And because it is just a graph of markdown notes on your server, it is
browsable. The **Mind** app, one of the starter-pack apps from the
[last post]({{ '/blog/2026/an-app-store-that-adapts-to-you/' | relative_url }}),
renders it as an Obsidian-style web of nodes and links. You can open it,
see what the agent thinks it knows, follow a thread from one lesson to a
related one, and read any note in full. There is nothing hidden behind
the memory. It is a folder you own, and the app is a window onto it.

This is the same itch I described at the end of the harness post. The
old experience file was a flat log that only grew. It accreted and
never reorganized, so the useful lessons sank under the one-off ones,
and rules that had stopped mattering stayed at full weight forever. A
graph fixes the _shape_ of the memory. It does not, on its own, fix the
_upkeep_. A graph still rots if nothing tends it. Which is the other
half of this post.

## Dreaming is the upkeep

Every night, on a schedule you set, Möbius dreams. The **Dreaming**
agent wakes up while you are not using the system, reviews the day, and
works to be more useful to you tomorrow. It is a scheduled agent like
any other on the platform, a background job that runs the coding agent
with a particular brief, except its brief is the instance itself rather
than any one app.

A dream does roughly four things.

**It tidies the Mind.** This is the part that is most solid, and it is
the one I am most confident in because it is the harness move I trust
most. The dream reads the current memory and the day's transcripts and
produces a _revised_ memory: duplicate notes merged, stale ones
dropped, scattered observations about the same thing pulled into one
place, fresh cross-cutting patterns surfaced as new notes. It does not
edit the transcripts. It rewrites the distilled layer on top of them.
Tomorrow's agent starts from a memory that is a little cleaner than
today's, the same way I clean up the agent's instructions between
sessions in the harness, except no one is driving.

**It anticipates what you will need next.** Having read the day, the
dream can notice a pattern and get ahead of it. If you have been logging
workouts every morning, it can prime the things that make tomorrow's log
instant. If you keep asking the same kind of question, it can note that
a small tool would answer it for you. This is the part that feels like
the agent thinking about you while you are asleep, and it is also the
part I would describe most carefully. Noticing patterns and writing
notes is real, while acting on them ahead of time is something the loop
is built to do but does cautiously, because a system that rearranges
your morning based on a guess is worse than one that waits to be asked.

**It suggests apps and features worth building.** A dream that has seen
you reach for the same workaround three times can write down "you keep
doing X by hand; an app would do it for you" and surface that as a
suggestion the next morning. It does not build the app unattended. The
build loop is the one from the first post, with you in it, asking the
clarifying questions and approving the result. The dream's job is to
have the idea and bring it to you, not to ship code into your instance
overnight.

**It audits your instance for weak spots.** The agent has write access
to its own shell, themes, app source, and schedules, which means it can
also _review_ all of those. A dream can look for a theme rule that hurts
contrast, a scheduled job that has been failing quietly, an app whose
data is growing in a way that will bite later, or a place where the
shell has drifted. This is the most aspirational of the four. The
hooks are there, the agent can read every one of those surfaces, but the
audit today is closer to a checklist than the deep self-review I want it
to become.

<figure class="mb-diagram">
  <div class="mb-cycle">
    <div class="mb-node">
      <span class="mb-node__lead">you · asleep</span>
      <span class="mb-node__title">The day's work is done</span>
      <span class="mb-node__sub">chats, builds, and edits from today sit in the transcripts and the Mind</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">a scheduled job wakes the agent</span></span>

    <div class="mb-node accent">
      <span class="mb-node__lead">Dreaming · overnight</span>
      <span class="mb-node__title">Review the day, work to be more useful tomorrow</span>
      <span class="mb-node__sub">tidy the Mind · anticipate what you'll need · suggest apps and features · audit the instance</span>
    </div>
    <span class="mb-arrow">↓<span class="mb-arrow__label">a revised memory and a short list of suggestions</span></span>

    <div class="mb-node">
      <span class="mb-node__lead">you · awake</span>
      <span class="mb-node__title">A sharper agent and a few things worth a look</span>
      <span class="mb-node__sub">tomorrow's sessions start from a cleaner Mind; suggestions wait for your yes</span>
    </div>

    <div class="mb-loopback">
      <span class="mb-loopback__glyph">↺</span>
      <span>each night's tidy-up is the input to the next night's &nbsp;→&nbsp; the memory compounds instead of just growing</span>
    </div>

  </div>
  <figcaption>The nightly loop, end to end. The day fills the Mind; the dream distills it and looks ahead; you wake to a memory that has been tended and a short list of things the agent thinks are worth building or fixing. Nothing irreversible happens without you.</figcaption>
</figure>

The reason all of this can run unattended is the philosophy the whole
series keeps coming back to. Breaking is allowed because it is
reversible. A dream commits its changes to the same git history
everything else does, so a bad night's reorganization is something you
can read back and undo, and the input it works from, your transcripts,
is never touched. The dream produces a new memory beside the old one and
the old one stays recoverable. That is what makes it safe to let an
agent rewrite its own memory while no one is watching.

## Dreaming is the harness, productized

If the loop in that last diagram looks familiar, it should. It is the
harness from the [second post]({{ '/blog/2026/the-self-improvement-harness/' | relative_url }}),
turned inward.

In the harness, the developers run a reflect-and-refactor loop on the
agent by hand. An outer agent watches the inner one work, asks it why it
did what it did with the transcript still in context, and rewrites its
instructions between sessions. The two findings that made that loop work
were that an agent reflecting on its _own_ recent experience self-corrects
better than a bigger agent reasoning from outside, and that the right
move is usually to _remove and reorganize_ rules rather than pile on new
ones, because a memory that only grows competes with itself.

Both of those are exactly what a dream does, except the agent runs the
loop on itself. It reflects on its own day, the transcript right there in
context, which is the setting where introspection actually beats
third-party theory of mind. And the core operation is a refactor of an
existing memory, merge the duplicates, drop the rules that stopped
firing, surface the pattern that spans several builds, which is the lesson
that broke the harness loop open in the first place. The harness proved,
on controlled experiments, that this is the move that compounds. Dreaming
is that move, scheduled, on your instance, on your behalf.

<blockquote class="pull-quote">
The same reflect-and-refactor loop the developers run by hand now runs on your own instance, against the agent's own memory, on your schedule and your model.
</blockquote>

There is also a piece of related work that this lines up with cleanly.
While I was building the harness, Anthropic shipped a primitive called
Dreams. A dream reads a memory store and past transcripts and
produces a _new_ store, with duplicates merged and stale entries
replaced, without touching the input, so a developer can review the
result and keep or discard it. That is almost exactly the contract the
nightly loop runs on, the input log left alone, a fresh memory produced
beside it, the output yours to keep. Möbius's version is self-hosted,
your own scheduler and model, running on a graph you actually own.

And that ownership is the whole point of doing it this way. A
self-improving agent that runs in someone else's cloud means your memory,
your patterns, and your nightly review all live on their machine. Here
they do not. The dream runs in the same single container as the rest of
Möbius, reads from `/data` on your server, writes back to it, and never
sends any of it anywhere. The agent gets sharper about you specifically,
and the record of that is a folder you can read, back up, or delete.
Self-improvement and self-hosting turn out to fit together better than
either does alone. The thing that learns you the most deeply is the thing
you most want to keep on hardware you control.

## What is shipped and what is still shallow

In the spirit of the rest of this series, here is the honest line
between what works today and what is still a sketch.

The Mind is real and shipped. It is a live knowledge graph, the agent
reads from it at the start of every session, it writes back to it as it
learns, and the Mind app renders it as a browsable web of notes. The
three-layer memory it sits in, a curated constitution, an editable set of
skills, and the graph itself, is the live model on every instance, not a
prototype.

Dreaming is real and shipped as a scheduled agent, and the first of its
four jobs, tidying the Mind, is the one that genuinely works. The other
three exist along a spectrum. Anticipating your needs is mostly
note-taking today; it observes and records well, and acts ahead of time
only in small, reversible ways. Suggesting apps is wired but quiet, and
gets better the more the agent has seen you do. The instance audit is the
most aspirational, the agent can read every surface it would need to
review, but the review itself is shallow and is where I am spending
effort next.

I would rather tell you that than pretend the whole nightly loop is
already the thing I am describing. The architecture is built so that as
each of those jobs deepens, it does so on the same safe footing: read
the day, propose a change beside the old state, commit it to a history
you can walk back. Getting them deep is the work. The loop they run in
is done.

## Where this goes

The arc of this series has been one agent doing one job, getting more of
itself over time. The first post gave it the ability to build. The
second gave the developers a loop to make it build well. The third gave
you the same reshaping power over an app store and the system around it.
This one closes the loop by handing the _improvement_ itself to your
instance. The agent that builds your tools now also tends its own memory
of how to build them, on your server, while you sleep.

That is the version of a personal assistant I actually want. Not one
that gets more generic the longer you use it, tuned to keep you engaged,
its memory of you locked in someone else's cloud. One that gets more
yours, that improves itself in the direction of being useful to you
specifically, and that keeps every trace of that on hardware you own.

[Möbius]({{ '/mobius/' | relative_url }}) is a deploy-button click away,
the source is on [GitHub](https://github.com/mobius-os/mobius), and the
apps are under [`mobius-os`](https://github.com/mobius-os). Deploy one,
use it for a week, and open the Mind app some morning to see what your
agent learned overnight.
