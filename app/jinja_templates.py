from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

# Templates
env = Environment(loader=FileSystemLoader("app/templates"))

class Templates:
    @staticmethod
    def TemplateResponse(template_name: str, context: dict):
        template = env.get_template(template_name)
        return HTMLResponse(template.render(**context))

# Make templates available
templates = Templates()
