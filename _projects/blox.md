---
layout: page
title: Blox
description: A small, functional neural network library for JAX — built to keep JAX's strengths visible instead of paper over them
img: assets/img/blox-logo.png
permalink: /blox/
importance: 2
category: software
---

<style>
  .action-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin: 1.5rem 0 0.5rem;
  }
  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.15rem;
    font-size: 0.95em;
    font-weight: 500;
    line-height: 1.2;
    text-decoration: none !important;
    border-radius: 0.5rem;
    border: 1px solid transparent;
    transition:
      transform 0.15s ease,
      box-shadow 0.2s ease,
      background 0.2s ease;
  }
  .action-btn.primary {
    background: var(--global-theme-color);
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
  .action-btn.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.14);
    color: #fff !important;
  }
  .action-btn.ghost {
    background: transparent;
    color: var(--global-text-color) !important;
    border-color: rgba(127, 127, 127, 0.35);
  }
  .action-btn.ghost:hover {
    background: rgba(127, 127, 127, 0.08);
    border-color: var(--global-theme-color);
    color: var(--global-theme-color) !important;
    transform: translateY(-1px);
  }
  .action-btn i {
    font-size: 1.05em;
  }
  .compare-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.95em;
  }
  .compare-table th,
  .compare-table td {
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid rgba(127, 127, 127, 0.18);
    vertical-align: top;
    text-align: left;
  }
  .compare-table thead th {
    background: rgba(127, 127, 127, 0.06);
    font-weight: 600;
    border-bottom: 2px solid rgba(127, 127, 127, 0.25);
  }
  .compare-table tbody th {
    font-weight: 500;
    color: var(--global-muted-color);
    width: 22%;
  }
  .compare-table .blox-col {
    background: linear-gradient(
      135deg,
      rgba(127, 127, 127, 0.03),
      rgba(127, 127, 127, 0.09)
    );
    border-left: 2px solid var(--global-theme-color);
  }
  .compare-table thead .blox-col {
    color: var(--global-theme-color);
  }
</style>

<p class="lead">
  Abstractions shape how we think. JAX comes with strong abstractions of its
  own — composable transformations over pure functions,
  <a href="https://docs.jax.dev/en/latest/stateful-computations.html">explicit
  state flow through function signatures</a>, an XLA compilation model that
  rewards clean code. A neural network library on top either keeps those
  abstractions visible or hides them, and the ones that keep them visible pay
  you back model after model.
</p>

<p class="mt-3">
  <strong>Blox</strong> is what I built: a small, modular, JAX-native neural
  network library. The whole mental model fits on one line:
</p>

<pre style="background: rgba(127, 127, 127, 0.08); border-left: 3px solid var(--global-theme-color); border-radius: 0.4rem; padding: 1rem 1.25rem; font-size: 1.05em; margin: 1.5rem 0;"><code class="language-python">outputs, params = model(params, inputs)</code></pre>

<p>
  Parameters go in, outputs and updated parameters come out. Because state
  flows through the signature, every JAX transformation
  (<code>jax.jit</code>, <code>jax.grad</code>, <code>jax.vmap</code>,
  <code>jax.checkpoint</code>) works on a Blox model with no decorators or
  special-cased helpers.
</p>

<h3 class="mt-5">Who it's for</h3>

<div class="row mt-3">
  <div class="col-md-6 mb-3">
    <div class="p-3" style="background: rgba(127, 127, 127, 0.05); border-radius: 0.5rem; height: 100%;">
      <h5 class="mb-2">📘 Learners</h5>
      <p class="mb-0" style="font-size: 0.95em;">
        No framework magic to reverse-engineer. What you read is what runs —
        the cleanest way to understand how neural networks actually work at
        the JAX level.
      </p>
    </div>
  </div>
  <div class="col-md-6 mb-3">
    <div class="p-3" style="background: rgba(127, 127, 127, 0.05); border-radius: 0.5rem; height: 100%;">
      <h5 class="mb-2">⚙️ Practitioners</h5>
      <p class="mb-0" style="font-size: 0.95em;">
        Full transparency for custom training loops, novel architectures, and
        scaling work where you actually want to see the execution stack.
      </p>
    </div>
  </div>
</div>

<h3 class="mt-5">Blox vs Equinox vs Flax NNX</h3>

<p>
  JAX has more than one answer to "what neural-net library do I use on top?" The
  choice mostly comes down to where state lives and how it crosses JAX's
  transformation boundaries.
</p>

<table class="compare-table">
  <thead>
    <tr>
      <th></th>
      <th>Equinox</th>
      <th>Flax NNX</th>
      <th class="blox-col">Blox</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Where parameters live</th>
      <td>Inside the module — the module <em>is</em> the parameter tree.</td>
      <td>Inside mutable <code>Module</code> instances as <code>Param</code> variables.</td>
      <td class="blox-col">In a separate <code>Params</code> container, passed in and out of the model.</td>
    </tr>
    <tr>
      <th scope="row">Model object</th>
      <td>An immutable PyTree (a dataclass-shaped one).</td>
      <td>A mutable Python class with reference semantics.</td>
      <td class="blox-col">A plain Python object describing the graph; the call signature is a pure function.</td>
    </tr>
    <tr>
      <th scope="row">Params / graph separation</th>
      <td>Coupled — params and module structure are the same tree.</td>
      <td>Coupled — both live inside the <code>Module</code>.</td>
      <td class="blox-col">Decoupled — static <code>Graph</code> describes structure, dynamic <code>Params</code> holds arrays.</td>
    </tr>
    <tr>
      <th scope="row">Using JAX transforms</th>
      <td><code>jax.jit</code> / <code>jax.grad</code> work directly; non-array fields need <code>eqx.filter_*</code> variants.</td>
      <td>Cross transform boundaries via <code>nnx.split</code> / <code>nnx.merge</code> to swap between mutable and functional form.</td>
      <td class="blox-col"><code>jax.jit</code>, <code>jax.grad</code>, <code>jax.vmap</code>, <code>jax.checkpoint</code> all called directly. No wrappers.</td>
    </tr>
    <tr>
      <th scope="row">Implicit / global state</th>
      <td>None.</td>
      <td>None — RNGs and shapes are threaded by the user.</td>
      <td class="blox-col">None. RNG counters live inside <code>Params</code> alongside the rest of the state.</td>
    </tr>
    <tr>
      <th scope="row">Non-trainable state (RNG, batch-norm stats)</th>
      <td>Stored as PyTree leaves alongside weights; filtering decides what gets gradients.</td>
      <td>Different <code>Variable</code> subclasses (<code>Param</code>, <code>BatchStat</code>, …) split via <code>nnx.split</code>.</td>
      <td class="blox-col">All state in one container; <code>params.split()</code> divides trainable from non-trainable at the gradient boundary.</td>
    </tr>
    <tr>
      <th scope="row">Surface area to learn</th>
      <td>Small — modules, filtering, a handful of helpers.</td>
      <td>Larger — Module system, Variables, split/merge, transform wrappers.</td>
      <td class="blox-col">Small — <code>Graph</code>, <code>Module</code>, <code>Params</code>, <code>Rng</code>. Three source files.</td>
    </tr>
  </tbody>
</table>

<p>
  Equinox is a good fit if you like the "model is a PyTree" mental model and
  are comfortable reaching for <code>filter_</code> variants when non-array
  fields show up. Flax NNX is the right pick if mutable, PyTorch-style module
  objects feel natural and you don't mind learning when to cross into the
  functional API. Blox optimises for a different thing: keeping the model
  graph and the parameter tree as two separate objects, so the same params
  can drive different graphs (actor and learner, static and dynamic scan,
  train and eval), and so every JAX transform applies to a plain function
  with no library-specific wrapper in the way.
</p>

<h3 class="mt-5">Install</h3>

<pre style="background: rgba(127, 127, 127, 0.08); border-radius: 0.4rem; padding: 0.85rem 1.1rem; margin: 1rem 0 1.5rem;"><code>pip install jax-blox</code></pre>

<p style="font-size: 0.9em; color: var(--global-muted-color);">
  Python 3.11+, JAX 0.10+. MIT licensed.
</p>

<div class="action-row">
  <a class="action-btn primary" href="https://github.com/hamzamerzic/blox" target="_blank" rel="noopener">
    <i class="fab fa-github"></i> View on GitHub
  </a>
  <a class="action-btn ghost" href="https://blox.readthedocs.io/en/latest/" target="_blank" rel="noopener">
    <i class="fas fa-book"></i> Read the docs
  </a>
</div>
