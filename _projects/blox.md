---
layout: page
title: Blox
description: A functional, lightweight neural network library for JAX
img: assets/img/blox-logo.png
permalink: /blox/
importance: 2
category: software
---

<p>
  Abstractions shape how we think. JAX comes with strong
  abstractions of its own — composable transformations over pure
  functions,
  <a href="https://docs.jax.dev/en/latest/stateful-computations.html">explicit
  state flow through function signatures</a>, an XLA compilation
  model that rewards clean code. A neural network library on top
  either keeps those abstractions visible or hides them, and the
  ones that keep them visible pay you back model after model.
</p>

<p>
  <strong>Blox</strong> is what I built: a small, modular, JAX-native
  neural network library.
</p>

<p>
  The whole mental model fits on one line:
</p>

<pre><code class="language-python">outputs, params = model(params, inputs)
</code></pre>

<p>
  Parameters go in, outputs and updated parameters come out. Because
  state flows through the signature, every JAX transformation
  (<code>jax.jit</code>, <code>jax.grad</code>, <code>jax.vmap</code>,
  <code>jax.checkpoint</code>) works on a Blox model with no
  decorators or special-cased helpers.
</p>

<p>
  I wrote it for two kinds of people. If you are learning JAX, there
  is no framework magic to reverse-engineer; what you read is what
  runs. If you are already shipping JAX in anger, you get full
  transparency for custom training loops, novel architectures, and
  scaling work where you actually want to see the execution stack.
</p>

<p>
  Install with <code>pip install jax-blox</code> (Python 3.11+, JAX
  0.10+). MIT licensed.
</p>

<div class="row mt-4">
  <div class="col-sm">
    <a class="btn btn-outline-primary" href="https://github.com/hamzamerzic/blox" target="_blank" rel="noopener">
      View on GitHub
    </a>
    <a class="btn btn-outline-primary" href="https://blox.readthedocs.io/en/latest/" target="_blank" rel="noopener">
      Read the docs
    </a>
  </div>
</div>
