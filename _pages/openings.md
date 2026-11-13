---
layout: page
permalink: /openings/
title: openings
description: Positions and projects to work with me.
nav: true
nav_order: 4
---

{% assign openings = site.data.openings %}
{% assign today = site.time | date: '%Y-%m-%d' %}

{% if openings and openings.size > 0 %}

{% for job in openings %}
{% assign closed = false %}
{% if job.deadline %}
{% capture deadline %}{{ job.deadline | date: '%Y-%m-%d' }}{% endcapture %}
{% if deadline < today %}{% assign closed = true %}{% endif %}
{% endif %}

### {{ job.title }}

{% if job.type %}**{{ job.type }}**{% endif %}{% if job.location %} · {{ job.location }}{% endif %}{% if job.duration %} · {{ job.duration }}{% endif %}

{{ job.summary | markdownify }}

{% if closed %}
_Applications closed on {{ job.deadline | date: '%-d %B %Y' }}._
{% else %}
{% if job.deadline %}**Deadline:** {{ job.deadline | date: '%-d %B %Y' }}{% endif %}{% if job.apply_url %}{% if job.deadline %} · {% endif %}[How to apply]({{ job.apply_url }}){% endif %}
{% endif %}

---

{% endfor %}

{% else %}

There are no advertised positions at the moment.

{% endif %}

#### Informal enquiries

I am always happy to hear from people interested in neutron and X-ray scattering, ionic liquids and deep eutectic solvents, or scientific software for scattering data. If you are thinking about a Masters or PhD project, a postdoctoral fellowship application, or a research visit, send me an [email](mailto:{{ site.data.socials.email }}) with a short description of your background and what you would like to work on.
