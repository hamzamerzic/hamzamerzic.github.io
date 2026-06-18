---
layout: post
title: My vibe coding setup, on my own server
date: 2026-05-22 14:00:00
description: A small server I own, my data on it, fronted by Cloudflare with Google auth, persistent shells so the agents I'm working with survive me closing the laptop. The same chats waiting on my phone an hour later. The setup, in the order I'd build it.
categories: software, infrastructure
giscus_comments: false
related_posts: false
published: false
---

> **TL;DR.** My vibe coding setup is one small server I own, with my data on it. Cloudflare fronts it and gates it behind Google auth. `shpool` keeps shells (and the agents inside them) alive across disconnects, so closing the laptop doesn't kill anything. The same chats are waiting on my phone an hour later. This morning a piece of it broke; the fix was a one-line systemd unit. Here's the whole thing, in the order you'd actually build it.

This is the vibe coding setup I've converged on. One server I own, my data on it, accessible from any device with a browser. I close the laptop, the agents keep working. I open my phone in the kitchen, the same conversations are still where I left them. Nothing of mine ends up on someone else's laptop or in someone else's cloud workspace.

This morning a piece of it broke. The fix was small, but it forced me to write the rest of the setup down properly. So this is not a polished build guide; it's the steps I'd follow if I were doing it again, with the lesson from this morning in the step where it belongs.

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
         alt="code-server in a desktop browser, with shpool-backed terminals and the Claude panel open."
         loading="lazy" />
  </div>
  <div class="mobile">
    <img src="{{ '/assets/img/vibe-setup/mobile.png' | relative_url }}"
         alt="The same code-server session in mobile Safari, picking up the same chat where it left off."
         loading="lazy" />
  </div>
</div>

<div class="caption mt-2">
  Same server, same shells, same chats. Desktop on the left, phone on the right.
</div>

## A small server

One 16 GB VPS at Hetzner, in Nuremberg. Around €16 a month. Pick whatever's geographically close to you; mine's a couple of hops away and the latency hasn't been an issue. The box runs a normal Ubuntu, nothing exotic.

The sizing matters more than I thought. 4 GB gets cramped the moment you run more than one agent. Each `claude` process holds 200–500 MB of working set, and I usually have four going. If you can afford 16 GB, get it and skip the swap dance entirely. I ran on 8 GB for a while and leaned on swap instead, with a swapfile on a second cheap volume bringing the total to 24 GB. It worked, but the volume was its own small tax, an extra disk to mount and reason about, and one morning it filled up and took a service down with it. So I eventually rescaled the box to 16 GB and dropped the volume. Real RAM beats swap, and one disk is one fewer thing to think about. I still keep swap on the main disk, because it won't make a small box fast, but it's the line between a spike that thrashes for a minute and one that kills an agent.

## code-server, bound to localhost

Install code-server normally. The only knob that matters is its bind address. In `~/.config/code-server/config.yaml`:

```yaml
bind-addr: 127.0.0.1:8080
auth: none
cert: false
```

That is the whole config file. No public port, no certificate, no built-in password. The actual auth and TLS happen upstream, in Cloudflare. If anything ever bypasses Cloudflare and hits the box, code-server isn't reachable: it isn't on a public address.

Run it as a systemd service so it restarts on its own. On most distros the `code-server` package ships a unit.

## Cloudflare Tunnel for ingress

`cloudflared` runs on the box as a systemd service. It opens an outbound QUIC connection to Cloudflare's edge, which then forwards traffic for my hostname back through that connection. No inbound port on the box, ever. The firewall stays closed.

Setup is a five-minute thing in the Cloudflare dashboard: create a tunnel, copy the token, drop it into a systemd unit on the box, point the tunnel's public hostname at `http://localhost:8080`. After that the unit is fire-and-forget:

```
● cloudflared.service - cloudflared
     Loaded: loaded (/etc/systemd/system/cloudflared.service; enabled)
     Active: active (running) since Sun 2026-05-17 00:03:27 UTC; 5 days ago
```

Public DNS for the hostname is a `CNAME` to a Cloudflare-managed tunnel host. You never see the certificate handling or the rotation.

## Gate it behind Google

Cloudflare Access is the bit that turns "code-server on a tunnel" into "code-server I can leave running for years". In the Cloudflare dashboard, add Google as an identity provider, then set one Access policy on the hostname: emails matching yours.

That's the whole auth setup. There is no on-box config. Every request that reaches code-server has already been validated by Cloudflare; if you're not me, you see a Google sign-in page that rejects you, and code-server never gets the request.

This is the part that took longest to get right in my head. I kept reaching for VPNs and SSH-over-something. Cloudflare Access is just better for this: standard browser flow, every device, no client to install, no key to lose, audit log in the dashboard.

The one setting that decides whether this is pleasant or a chore is the Access session duration. Out of the box it's 24 hours, so you sign in with Google once a day, every day. It lives in two places. There's a per-application duration under Access, and a global one under Access settings that governs how often you re-authenticate with the identity provider itself; the shorter of the two wins, so raise both. I set mine to a week. A month is the ceiling. With that changed the daily sign-in went away, and the "leave it running for years" part finally held.

## Persistent shells with `shpool`

A browser-based IDE is comfortable until you close the tab. The terminals don't survive. The agents inside them definitely don't. I want them to.

[`shpool`](https://github.com/shell-pool/shpool) is a small Rust daemon that owns a pool of long-lived shells and lets you `attach` and `detach` from them. Think `tmux` minus the multiplexing UI, plus the assumption that you'll connect from many places.

The pattern:

```bash
shpool attach mobius     # creates the session if it doesn't exist
claude --resume          # pick the conversation up from disk
```

I keep four of these running, one per thread in my head: `mobius`, `thesis`, `website`, and `code-server-blog` (this one). Each has its own `claude` inside. To context-switch I detach with `Ctrl+\ d` and `shpool attach <next>`. Output that streamed while I was elsewhere is still there.

> **What broke this morning.** Around lunchtime the agents started "dying": heartbeat timeout, attach torn down. Then code-server felt sluggish. The kernel had OOM-killed a Chrome tab overnight; I hadn't noticed.
>
> Proximate cause: I had thirteen disconnected `shpool` sessions, each holding a 200–500 MB `claude` process inside. About 2.8 GB of "ghost" agents I'd never reaped. Once swap filled, `shpool`'s 300 ms internal heartbeat couldn't get scheduled in time, and the daemon kept tearing attaches down to protect itself. Reaping the stale sessions fixed the symptom.
>
> Structural cause: I checked the daemon's cgroup.
>
> ```
> /user.slice/user-1000.slice/user@1000.service/app.slice/code-server.service
> ```
>
> The `shpool` daemon was running inside code-server's cgroup. I'd started it months ago from a code-server terminal. It daemonised off into the background, but the cgroup membership stuck. Whenever code-server itself restarted, the kernel tore the cgroup down and took every session with it. The reason "agents survive me closing the laptop" had worked at all is that I'd just been lucky about not restarting code-server.

The fix is a `shpool.service` systemd **user** unit, not a system one. Drop this at `~/.config/systemd/user/shpool.service`:

```ini
[Unit]
Description=shpool persistent shell daemon

[Service]
ExecStart=%h/.cargo/bin/shpool ... daemon
Restart=on-failure
KillMode=process

[Install]
WantedBy=default.target
```

Then:

```bash
loginctl enable-linger $USER
systemctl --user enable --now shpool.service
```

`enable-linger` is the bit nobody mentions in tutorials. Without it, your user systemd shuts down when you have no active login session, and `--user` services go with it. With it, the user manager stays alive across logouts. The `shpool` daemon now lives in its own cgroup at `…/app.slice/shpool.service`, with no parent that can take it down.

The same trick generalises. If you want X to outlive the thing that started it, X should be a `--user` systemd unit, not a process started from a shell. `tmux` has the same trap. Anything you launch from inside code-server has the same trap. The cgroup is the unit of persistence on Linux, not the daemonisation.

## The editor window has its own clock

`shpool` keeps the terminal agents alive. The editor window is a separate thing with a separate clock, and it took me a while to keep the two straight in my head.

If you run an agent as a VS Code extension rather than in a terminal, the Claude Code sidebar being the obvious one, it lives inside code-server's extension host. That host is tied to the browser connection, not to `shpool`. code-server keeps a disconnected window alive for `reconnection-grace-time` and then lets it go. The default is three hours. Close the laptop at lunch, come back after dinner, and you reconnect to a fresh window. New extension host, old agent gone, the conversation cold-resumed from disk if you're lucky. For a while I thought the agents were "stopping" on their own; they were being torn down on a timer I didn't know was there.

One line in the same config file moves the timer:

```yaml
reconnection-grace-time: 86400
```

A day instead of three hours. The trade is that an abandoned window holds its extension host, a few hundred MB, for that whole day, so don't set it to a week on a small box. The sturdier answer is to not depend on the window at all. Anything I want running while I'm gone goes in `shpool`, in a terminal, where its life is decoupled from the browser. The extension is for when I'm sitting there watching it work.

## Surviving the disconnect isn't the same as working through it

Keeping the window alive gets you a live agent. It doesn't get you a working one, and that gap cost me a few mornings. I'd hand off a long task, close the laptop, and come back to an agent that had done three or four steps and stopped. It looked like it had hit a wall and given up. It hadn't. It had asked me a question with nobody in the room.

Most of what an agent does is gated by default, like editing a file, taking a screenshot, or running a shell command it hasn't run before. When I'm watching, each gate is one tap. When I've closed the laptop, the approval prompt has nowhere to go, and after a moment it comes back to the agent as a refusal. The agent reads that as "the owner said no" and stops. From my end it's an agent that quit a few steps in; really it's an agent waiting on an answer that can't arrive.

The fix is to decide ahead of time which tools you trust and put them on the `allow` list in Claude Code's `settings.json`, so they stop asking (`Read`, `Edit`, `Write`, and the shell commands the agent leans on all day). The trust has to be broad enough that it doesn't trip a gate halfway through; the first un-listed command it hits while you're gone is where it stalls. The other half of the bargain is a `deny` list for the handful of things that should never run unattended (`rm -rf`, a force-push, anything that pipes the internet into a shell), and `deny` wins over `allow`, so "let it run while I'm asleep" can't quietly become "let it run `rm -rf` while I'm asleep." Get the two lists right and the laptop-closed, finished-by-morning workflow this whole post is selling actually holds. Get them wrong and the persistent shells just keep a stalled agent warm.

## Small habits that paid off

A few one-liners that I wouldn't have bothered with three months ago and now wouldn't go without:

- `default_dir = "."` in `~/.config/shpool/config.toml`, so new sessions inherit the calling directory instead of dumping you in `$HOME`.
- A ceiling on Docker's disk use. I started with a `docker-prune.timer` user unit running `docker system prune --filter until=72h` daily, and one morning's 14.6 GB build cache showed why I wanted it. But a time-based prune doesn't save you when a single day of cache plus a few superseded images fill the disk to 100%, which is what eventually happened, and a service that needed to write to that disk fell over. What actually holds is a ceiling the daemon enforces on its own, a `builder.gc` block in `/etc/docker/daemon.json` with `maxUsedSpace` set, so the cache can't outgrow the disk no matter how busy the day was.
- `earlyoom` as a system service, so a runaway can't freeze the box waiting on the kernel's own OOM killer, which is slow and picks badly. earlyoom steps in first and takes the biggest process, with `sshd` and the tunnel on a do-not-touch list so I never lock myself out.
- A `MemoryHigh=5G` drop-in on the code-server unit, so the editor throttles under pressure instead of ballooning into everything else. It had quietly peaked at 6.8 GB.
- A persistent `MEMORY.md` plus per-fact files in `~/.claude/projects/...` for things I'd otherwise forget, like credential locations, deployment routines, and the names of every weird flag I had to learn the hard way. Claude reads it on every session.

## What you get

Open a URL from any device. Sign in with Google. Land in a VS Code window with four shells running, each with a different agent doing different work, each remembering where you left it. Close the tab. Open the same URL on your phone an hour later. Same shells. Same chats. Same place.

In rough priority order, what I'd solve when building this from scratch:

1. Sessions don't die.
2. The same chat is reachable from any device.
3. The IDE is good enough that you stop thinking about the IDE.

(1) breaks if you skip the cgroup trick. (2) you get for free from the agent storing its conversation on disk. (3) is the easy bit.

The rest is just writing.
