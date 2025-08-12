---
layout: page
title: projects
permalink: /projects/
description:
nav: true
nav_order: 2
display_categories: [robotics]
horizontal: false
---

<!-- pages/projects.md -->
<div class="projects">
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>

  <!-- Custom text per category -->

{% case category %}
{% when "robotics" %}

<p class="category-description">
  These tools were <b>built to support my master's research in robotics</b>. They were hosted on my old site for years and kept running thanks to ongoing demand. They've been cleaned up, migrated, and redeployed here.
  <br>
  <br>
  Read more in <a href="https://hamzamerzic.info/blog/2025/website-migration/">this blog post</a>.
</p>
{% else %}
<p class="category-description">Projects related to {{ category }}.</p>
{% endcase %}

{% assign categorized_projects = site.projects | where: "category", category %}
{% assign sorted_projects = categorized_projects | sort: "importance" %}

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
  {% endfor %}
</div>
