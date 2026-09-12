# docs/en/archive.md
---
layout: default
title: Blog Archive
lang: en
permalink: /en/archive/
---

# 📚 Blog Archive

{% assign en_posts = site.posts | where: "lang", "en" %}
{% if en_posts.size > 0 %}
<div class="archive-list">
  {% for post in en_posts %}
    <div class="archive-item">
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
      <time class="archive-date">{{ post.date | date: "%m.%d.%Y" }}</time>
    </div>
  {% endfor %}
</div>
{% else %}
<p>No posts yet.</p>
{% endif %}