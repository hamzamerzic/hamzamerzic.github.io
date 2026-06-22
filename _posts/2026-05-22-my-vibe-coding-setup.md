---
layout: post
title: My vibe coding setup, on my own server
date: 2026-05-22 14:00:00
description: A small server I own, my data on it, fronted by Cloudflare with Google auth, and sessions that survive me closing the laptop, so the same work is waiting on my phone an hour later.
categories: software, infrastructure
giscus_comments: false
related_posts: false
published: false
---

<details class="tldr">
<summary><strong>TL;DR.</strong> One small server I own, with my data on it. Cloudflare fronts it and gates it behind Google auth, and code-server runs the agents in the browser. The sessions outlive a closed laptop, so I pick the same work up on my phone an hour later.</summary>

<ul>
<li><strong>One 16 GB box.</strong> A €16/mo Hetzner VPS running code-server bound to localhost, with Cloudflare Tunnel and Access doing the auth and TLS so no port is ever open.</li>
<li><strong>Sessions don't die.</strong> code-server's persistent terminals keep the agents running through a closed laptop, and a longer grace time keeps the editor window around too.</li>
<li><strong>The phone is just another screen.</strong> Same URL, sign in with Google, same chats where I left them. Usually four Claude Code agents going at once.</li>
<li><strong>It broke once.</strong> Leaked headless-Chrome daemons thrashed the box into swap. The fix was one env var, so the tool now shuts its own forgotten browsers down.</li>
</ul>
</details>

This is the setup I've settled into. One server I own, my data on it, reachable from any device with a browser. Nothing of mine ends up on someone else's machine.

A piece of it broke recently, and fixing it pushed me to write the rest down. So it's really just the steps I'd follow if I were doing it again, with the lessons sitting in the steps they came from.

<style>
  .vibe-screens {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 1rem;
    margin: 2rem auto;
    flex-wrap: wrap;
  }
  .vibe-screens .desktop {
    flex: 0 1 520px;
    max-width: 520px;
  }
  .vibe-screens .mobile {
    flex: 0 0 180px;
    max-width: 180px;
  }
  .vibe-screens img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 0.5rem;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
  }
</style>

<div class="vibe-screens">
  <div class="desktop">
    <img src="{{ '/assets/img/vibe-setup/desktop.png' | relative_url }}"
         alt="code-server in a desktop browser, with persistent terminals and the Claude panel open."
         loading="lazy" />
  </div>
  <div class="mobile">
    <img src="{{ '/assets/img/vibe-setup/mobile.png' | relative_url }}"
         alt="The same code-server session in mobile Safari, picking up the same chat where it left off."
         loading="lazy" />
  </div>
</div>

<div class="caption mt-2">
  Desktop on the left, phone on the right. The same session on both.
</div>

## A small server

One 16 GB VPS at Hetzner, in Nuremberg, around €16 a month. Pick whatever's geographically close to you; mine's a couple of hops away and the latency has never been an issue. It runs a normal Ubuntu, nothing exotic.

The sizing matters more than I expected.

- 4 GB gets cramped the moment you run more than one agent. Each `claude` process holds 200–500 MB of working set, and I usually have four going.
- 16 GB is the difference between leaning on swap and not thinking about memory at all.

I keep some swap on the main disk anyway. It won't make a small box fast. It just turns a spike that would have killed an agent into one that thrashes for a minute.

## code-server, bound to localhost

Install code-server normally. The only knob that matters is its bind address. In `~/.config/code-server/config.yaml`:

```yaml
bind-addr: 127.0.0.1:8080
auth: none
cert: false
```

That is the whole config file. No public port, no certificate, no built-in password. The actual auth and TLS happen upstream, in Cloudflare. If anything ever bypasses Cloudflare and hits the box, code-server still isn't reachable, because it isn't on a public address.

Run it as a systemd service so it restarts on its own. On most distros the `code-server` package ships a unit.

## Cloudflare Tunnel for ingress

`cloudflared` runs on the box as a systemd service. It opens an outbound QUIC connection to Cloudflare's edge, which then forwards traffic for my hostname back through that connection. No inbound port on the box, ever. The firewall stays closed.

Setup is a five-minute thing in the Cloudflare dashboard: create a tunnel, copy the token, drop it into a systemd unit on the box, point the tunnel's public hostname at `http://localhost:8080`. After that the unit is fire-and-forget.

Public DNS for the hostname is a `CNAME` to a Cloudflare-managed tunnel host. You never see the certificate handling or the rotation.

## Gate it behind Google

Cloudflare Access is the bit that turns "code-server on a tunnel" into "code-server I can leave running for years". In the Cloudflare dashboard, add Google as an identity provider, then set one Access policy on the hostname: emails matching yours.

That's the whole auth setup. There is no on-box config. Every request that reaches code-server has already been validated by Cloudflare; if you're not me, you see a Google sign-in page that rejects you, and code-server never gets the request.

This took the longest to get straight in my head; I kept reaching for VPNs and SSH tunnels. Cloudflare Access is simpler. You sign in through a normal browser on any device, with nothing to install and no key that can go missing.

The one setting that decides whether this is pleasant or a chore is the Access session duration. Out of the box it's 24 hours, so you sign in with Google every day. It lives in two places:

- a per-application duration under Access, and
- a global one under Access settings, governing how often you re-auth with the identity provider itself.

The shorter of the two wins, so raise both. I set mine to a week; a month is the ceiling. With that changed, the daily sign-in went away and stayed away.

<figure class="mb-diagram">
  <div class="mb-flow">
    <div class="mb-node">
      <span class="mb-node__title">Your device</span>
      <span class="mb-node__sub">any browser, desktop or phone, on any network</span>
    </div>
    <span class="mb-arrow">&rarr;<span class="mb-arrow__label">https request</span></span>
    <div class="mb-node accent">
      <span class="mb-node__title">Cloudflare edge</span>
      <span class="mb-node__tag">Access + TLS</span>
      <span class="mb-node__sub">Google sign-in checks your email, then terminates TLS; if you're not me, the request stops here</span>
    </div>
    <span class="mb-arrow">&rarr;<span class="mb-arrow__label">outbound tunnel, no inbound port</span></span>
    <div class="mb-node">
      <span class="mb-node__title">cloudflared</span>
      <span class="mb-node__sub">on the box, holding a QUIC connection open to the edge; the firewall stays closed</span>
    </div>
    <span class="mb-arrow">&rarr;<span class="mb-arrow__label">localhost:8080</span></span>
    <div class="mb-node">
      <span class="mb-node__title">code-server</span>
      <span class="mb-node__sub">bound to 127.0.0.1, no public address, no password of its own</span>
    </div>
  </div>
  <figcaption>Every request is validated at Cloudflare's edge before it reaches the box, and the box only ever connects outward. There is no open port to find.</figcaption>
</figure>

## Sessions that outlive the tab

A browser IDE is comfortable until you close the tab, and then the terminals are gone, and with them the agents running inside. I want them to stay, and most of that I get without lifting a finger.

code-server's integrated terminals are persistent. The shell and whatever's running in it survive a browser disconnect and reattach when you come back, so closing the laptop doesn't kill the `claude` process mid-task. It's still there, still streaming, when I reopen the tab on my phone an hour later.

The one default worth changing is the editor window's own clock. If you run an agent as a VS Code extension instead of in a terminal (the Claude Code sidebar, say), it lives in code-server's extension host, and that host is tied to the browser connection rather than the terminal. code-server keeps a disconnected window for `reconnection-grace-time` and then lets it go. The default is three hours, so close the laptop at lunch, come back after dinner, and you reconnect to a fresh window with the old agent gone.

I lost a few agents to that default before I went looking for the knob. One line in the config moves it:

```yaml
reconnection-grace-time: 86400
```

A day instead of three hours. The trade is that an abandoned window holds its extension host, a few hundred MB, for that whole day, so don't push it to a week on a small box. Better to keep anything long-running in a terminal, where closing the window can't touch it. The extension is for when I'm sitting there watching it work.

## Coding from the phone

The whole point of a server is that the phone is just another screen onto it. Open the same URL in mobile Safari, sign in with Google, and the session is right where you left it.

- **The terminals** work on a phone but they're fiddly: a tiny keyboard against a full-screen shell.
- **The Claude or Codex extension**, the sidebar agent rather than the terminal, is what I mostly reach for. It's the rougher half of the setup right now. The touch targets are small and the on-screen keyboard keeps getting in the way. But for reading what an agent did overnight and nudging it along from the kitchen, it's enough.
- **The Claude app pointed at the session** skips the editor entirely. You drive the agent from your phone directly, no code-server in the loop. When I just want to check on a long task or fire off one more instruction, that's the easiest of the three to reach for.

## The agent that stalls with nobody watching

This one cost me a few mornings. I'd hand off a long task, close the laptop, and come back to an agent that had done three or four steps and stopped. It looked like it had given up. It hadn't; it had asked a question with nobody in the room.

Most of what an agent does is gated by default, like editing a file or running a shell command it hasn't run before. When I'm watching, each gate is one tap. When the laptop's closed, the approval prompt has nowhere to go, and after a moment it comes back to the agent as a refusal. The agent reads that as "the owner said no" and stops.

The fix is to decide ahead of time which tools you trust and put them on the `allow` list in Claude Code's `settings.json`, so they stop asking: `Read`, `Edit`, `Write`, and the shell commands it leans on all day. The trust has to be broad enough that it doesn't trip a gate halfway through, because the first un-listed command it hits while you're gone is where it stalls. The other half is a `deny` list for the things that should never run unattended, like `rm -rf` or a force-push, and `deny` wins over `allow`, so "let it run while I'm asleep" can't quietly become "let it run `rm -rf` while I'm asleep." Get the two lists right and the finish-by-morning workflow actually holds.

## Small habits that paid off

A few one-liners I'd skip three months ago and now keep on every box:

- A ceiling on Docker's disk use, set in the daemon itself. A `builder.gc` block in `/etc/docker/daemon.json` with `maxUsedSpace`, so the build cache can't outgrow the disk no matter how busy the day was. I wanted it the morning a full build cache filled the disk and took a service down.
- `earlyoom` as a system service, so a runaway can't freeze the box waiting on the kernel's own OOM killer, which is slow and picks badly. earlyoom steps in first and takes the biggest process, with `sshd`, the tunnel, and the container runtime on a do-not-touch list so I never lock myself out. It has never had to fire, which is how I want it.
- A `MemoryHigh=5G` drop-in on the code-server unit, so the editor throttles under pressure instead of ballooning into everything else. It had quietly peaked at 6.8 GB.
- A persistent `MEMORY.md` plus per-fact files in `~/.claude/projects/...` for things I'd otherwise forget: credential locations, deployment routines, the flag names I keep relearning. Claude reads it on every session.

## The cgroup is a budget, too

The piece that broke recently lives here. code-server went sluggish one afternoon, and a chat I was halfway through dropped and reconnected on its own. The culprit was headless Chrome. I drive a browser-automation tool from the agents, and six instances had been sitting open for days, about 3 GB of them, mostly swapped out and thrashing the disk every time the kernel reached for a page.

Everything you start from a code-server terminal lives in code-server's cgroup, and a cgroup is a shared budget. Those browsers were spending from it for days after I'd stopped thinking about them. On a small box with a soft memory cap on the editor, a few gigabytes of forgotten processes is the difference between a session that holds and one that thrashes until the connection drops.

The tempting fix is a little reaper, a cron job that hunts down stray browsers, or teaching `earlyoom` which processes to sacrifice first. I did neither, and I'd argue against both. They're more machinery to babysit, standing guard over a failure I'd rather not have.

The browser tool already had the right knob: an idle timeout that shuts each instance down after twenty minutes of nothing. One environment variable, and the leak can't build up, because the thing that was leaking now closes itself. On a small box, I'd rather the cleanup live inside the tool than bolt a watchman onto the outside of it.

## What you get

Open a URL from any device, sign in with Google, and you're in a VS Code window with four shells running, each agent on different work and each remembering where it was. Close the tab, open the same URL on your phone an hour later, and the same shells and chats are right where you left them.

In rough priority order, what I'd solve when building this from scratch:

1. Sessions don't die.
2. The same chat is reachable from any device.
3. The IDE is good enough that you stop thinking about the IDE.

The persistent terminals and a longer grace time on the window cover the first. The second is free, because the agent keeps its conversation on disk. The third is the easy part.
