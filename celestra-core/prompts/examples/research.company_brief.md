---
name: research.company_brief
version: 1
description: Produce a company research brief
required_variables: [company_name]
---
Produce a concise enterprise research brief for {{ company_name }}.

{% if industry is defined and industry %}Industry focus: {{ industry }}{% endif %}
{% if questions is defined and questions %}
Answer these questions:
{% for q in questions %}- {{ q }}
{% endfor %}
{% endif %}

Structure:
- Overview
- Products
- Market
- Risks
- Sources to verify
