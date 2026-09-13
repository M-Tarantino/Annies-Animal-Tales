---
layout: default
title: Blog Archive
lang: en
permalink: /en/archive/
---

# 📚 Blog Archive

{% if site.posts_en.size > 0 %}
<div class="archive-list">
  {% for post in site.posts_en %}
    <div class="archive-item">
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a>
      <time class="archive-date">{{ post.date | date: "%m.%d.%Y" }}</time>
    </div>
  {% endfor %}
</div>
{% else %}
<p>No posts yet.</p>
{% endif %}