extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "m2r2"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

project = "python-core-example"
copyright = "python-core-example"

exclude_patterns = ["_build"]

html_theme = "alabaster"

html_theme_options = {
    "description": "A library for python-core-example.",
}
