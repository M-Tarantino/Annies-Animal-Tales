# docs/en/stories.md
---
layout: default
title: Stories
lang: en
permalink: /en/stories/
---

<section class="stories-hero">
  <h1>✨ Children's Stories</h1>
  <p class="stories-subtitle">Magical stories for the little ones — to laugh, dream and learn.</p>
</section>

{% assign en_stories = site.posts | where: "lang", "en" %}
{% if en_stories.size > 0 %}
<div class="stories-grid">
  {% for story in en_stories %}
    {% if story.path contains '_kindergeschichten' %}
      <article class="story-card">
        {% if story.image %}<div class="story-card-image"><img src="{{ site.baseurl }}{{ story.image }}" alt="{{ story.title }}" loading="lazy"></div>{% endif %}
        <div class="story-card-content">
          <h2><a href="{{ site.baseurl }}{{ story.url }}">{{ story.title }}</a></h2>
          <div class="story-card-meta">
            <time>{{ story.date | date: "%m.%d.%Y" }}</time>
            {% if story.age_group %}<span class="age-badge">{{ story.age_group }}</span>{% endif %}
            {% if story.reading_time %}<span>📖 {{ story.reading_time }} min</span>{% endif %}
          </div>
          <p>{{ story.description }}</p>
          <a href="{{ site.baseurl }}{{ story.url }}" class="story-link">Read Story →</a>
        </div>
      </article>
    {% endif %}
  {% endfor %}
</div>
{% else %}
<div style="text-align: center; padding: 3rem; background: white; border-radius: 12px;">
  <p>✨ No stories yet. The first adventure is coming soon! 🐾</p>
</div>
{% endif %}