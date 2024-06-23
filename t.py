from jinja2 import Template

# Define the template content with comments
template_content = """
    some-package>=1.0.0,
{%- if project_type == 'django' %}
    'django-extensions>=3.2.3',
{%- endif %}
    another-package>=2.0.0,
"""

# Create a template object
template = Template(template_content)

# Define the context (variables) to pass to the template
context_django = {"project_type": "django"}
context_non_django = {"project_type": "flask"}

# Render the template with the context where project_type is 'django'
rendered_content_django = template.render(context_django)

# Render the template with the context where project_type is not 'django'
rendered_content_non_django = template.render(context_non_django)

# Print the rendered contents
print("===Rendered content with project_type 'django':")
print(rendered_content_django)
print("\n====Rendered content with project_type not 'django':")
print(rendered_content_non_django)
