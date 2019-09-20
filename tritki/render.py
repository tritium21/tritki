import jinja2

import tritki.markdown

env = jinja2.Environment(
    loader=jinja2.PackageLoader('tritki', 'templates'),
    autoescape=jinja2.select_autoescape(
        enabled_extensions=[],
        disabled_extensions=['html'],
        default_for_string=False,
        default=False,
    ),
)

def render(article):
    converted = tritki.markdown.convert(article.content)
    template = env.get_template('article.html')
    rendered = template.render(title=article.title, content=converted)
    return rendered