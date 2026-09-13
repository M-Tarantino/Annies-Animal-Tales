---
layout: default
title: Home
lang: en
---

<section class="home-hero">
  <h1>🐾 Welcome to Annie's Animal Tales</h1>
  <p class="hero-subtitle">Adventures, care tips and daily stories from the animal world.</p>
</section>

<section class="home-latest">
  <h2>Latest Posts</h2>
  {% if site.posts_en.size > 0 %}
    {% for post in site.posts_en limit:3 %}
      <article class="post-preview">
        {% if post.image %}<img src="{{ site.baseurl }}{{ post.image }}" alt="{{ post.title }}">{% endif %}
        <div class="post-preview-content">
          <h2><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h2>
          <p>{{ post.description }}</p>
          <time>{{ post.date | date: "%B %d, %Y" }}</time>
        </div>
      </article>
    {% endfor %}
    <div class="home-cta"><a href="{{ site.baseurl }}/en/archive/" class="btn">All Posts →</a></div>
  {% else %}
    <p>No posts yet.</p>
  {% endif %}
</section>