# docs/en/index.md
---
layout: default
title: Home
lang: en
permalink: /en/
---

# 🐾 Annie's Animal Tales

Welcome to our blog about pet adventures, care tips, and daily stories.

## Latest Stories

<div class="post-list">
  {% for post in site.posts %}
    {% if post.lang == 'en' %}
      <article>
        <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
        <time>{{ post.date | date: "%d. %B %Y" }}</time>
        <p>{{ post.description }}</p>
      </article>
    {% endif %}
  {% endfor %}
</div>
