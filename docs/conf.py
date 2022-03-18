import packaging.version
from duma_backend.version import version

# from pallets_sphinx_themes import get_version
# from pallets_sphinx_themes import ProjectLink

# TODO: may need to add project source code to sys.path here so that auto-doc works


# Project --------------------------------------------------------------

project = "duma_backend"
copyright = "tern"
author = "tern"
release, version = version, version # TODO release is meant to be short version of version

# General --------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinxcontrib.openapi",
    # "sphinxcontrib.log_cabinet",
    # "pallets_sphinx_themes",
    # "sphinx_issues",
    # "sphinx_tabs.tabs",
    "sphinx_rtd_theme",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    "flasksa": ("https://flask-sqlalchemy.palletsprojects.com/en/2.x/", None),
    "flaskmigrate": ("https://flask-migrate.readthedocs.io/en/latest/", None),
    "flaskcors": ("https://flask-cors.readthedocs.io/en/latest/", None),
    "flaskcache": ("https://flask-caching.readthedocs.io/en/latest/", None),
    "flasksession": ("https://flask-session.readthedocs.io/en/latest/", None),
    "redis": ("https://redis-py.readthedocs.io/en/stable/", None),
    # TODO: es version?
    "es": ("https://elasticsearch-py.readthedocs.io/en/v7.10.1/", None),
    "esdsl": ("https://elasticsearch-dsl.readthedocs.io/en/latest/", None),
    "authlib": ("https://docs.authlib.org/en/stable/", None),
    # "click": ("https://click.palletsprojects.com/", None),
    # "jinja": ("https://jinja.palletsprojects.com/", None),
    "itsdangerous": ("https://itsdangerous.palletsprojects.com/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/", None),
    # "wtforms": ("https://wtforms.readthedocs.io/", None),
    # "blinker": ("https://pythonhosted.org/blinker/", None),
    "pytest": ("https://docs.pytest.org/en/latest/", None),
    "flasktern": ("http://terndatateam.bitbucket.io/flask_tern/", None),
}
# issues_github_path = "pallets/flask"

todo_include_todos = True

# HTML -----------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'prev_next_buttons_location': 'both',
}
html_context = {
    "display_bitbucket": True,  # Integrate Bitbucket
    "bitbucket_user": "terndatateam", # Username
    "bitbucket_repo": "duma_backend", # Repo name
    "bitbucket_version": "master", # Version
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}
# html_static_path = ["_static"]
# html_favicon = "_static/flask-icon.png"
# html_logo = "_static/flask-icon.png"
html_title = f"duma_backend Documentation ({version})"
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [(master_doc, f"Flask-{version}.tex", html_title, author, "manual")]

# Local Extensions -----------------------------------------------------


# def github_link(name, rawtext, text, lineno, inliner, options=None, content=None):
#     app = inliner.document.settings.env.app
#     release = app.config.release
#     base_url = "https://github.com/pallets/flask/tree/"

#     if text.endswith(">"):
#         words, text = text[:-1].rsplit("<", 1)
#         words = words.strip()
#     else:
#         words = None

#     if packaging.version.parse(release).is_devrelease:
#         url = f"{base_url}master/{text}"
#     else:
#         url = f"{base_url}{release}/{text}"

#     if words is None:
#         words = url

#     from docutils.nodes import reference
#     from docutils.parsers.rst.roles import set_classes

#     options = options or {}
#     set_classes(options)
#     node = reference(rawtext, words, refuri=url, **options)
#     return [node], []


# def setup(app):
#     app.add_role("gh", github_link)
