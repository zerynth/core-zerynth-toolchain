import sys
import os
import json
import re


# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    #'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    #'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["."]

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'


with open("docs.json","r") as ff:
    conf = json.load(ff)

with open("layout.html","w") as ff:
  ff.write('{% extends "!layout.html" %}\n\n')
  ff.write('{%- block extrahead %}\n')
  ff.write('<link rel="shortcut icon" href="_static/favicon.ico" type="image/x-icon"/>\n')
  ff.write('<link rel="icon" href="/_static/favicon.ico" type="image/x-icon"/>\n')
  ff.write('<link rel="icon" type="image/png" sizes="32x32" href="/_static/favicon-32x32.png">\n')
  ff.write('<link rel="icon" type="image/png" sizes="96x96" href="/_static/favicon-96x96.png">\n')
  ff.write('<link rel="icon" type="image/png" sizes="16x16" href="/_static/favicon-16x16.png">\n')
  ff.write('{% endblock %}\n')
  ff.write('{%- block footer %}\n')
  ff.write(' <script type="text/javascript">\n')
  # ff.write(' var vurl\n')
  # ff.write(' if(location.href.indexOf("127.0.0.1")>=0) vurl=location.protocol+"//"+location.host+"/docs"\n')
  # ff.write(' else vurl="http://doc.zerynth.com"\n')
  # ff.write(' $(document).ready(function(){\n')
  # ff.write('                   $(\'.wy-breadcrumbs a:contains("Docs")\').before(\'<a href="\'+vurl+\'">Zerynth</a> &#187;\')\n')
  # ff.write('                   $(\'.wy-side-nav-search > a\').removeClass("fa-home").removeClass("fa")\n')
  # ff.write('                   $(\'.wy-side-nav-search\').prepend(\'<div class="zerynth-circle"><a href="\'+vurl+\'"><span style="color:#1c5e60" class="zerynth-Logo2"></span></a></div>\')\n')
  # ff.write(' })\n')
  ff.write(' </script>\n')
  ff.write(' <script>\n')
  ff.write(" (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){")
  ff.write(" (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),")
  ff.write(" m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)")
  ff.write(" })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');")
  ff.write(" ga('create', 'UA-64288331-2', 'auto');")
  ff.write(" ga('send', 'pageview');")
  ff.write("</script>")
  ff.write('{% endblock %}\n')

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ""#conf.get("version","")
# The full version, including alpha/beta/rc tags.
release = version

tocdepth = conf.get("tocdepth",2)

# General information about the project.
project = conf.get("title","")
copyright = conf.get("copyright","")


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#html_theme = 'alabaster'
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_style = 'zerynth.css'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static','custom']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr'
html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'ZerynthDocumentationdoc'


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('http://docs.python.org/3.4', None)}



####VIPER DOCSTRING EXTRACTION
import ast
import glob


class VDocExtractor(ast.NodeVisitor):
  def __init__(self):
    self.docstring = ""

  def visit_FunctionDef(self,node):
    ss =ast.get_docstring(node)
    if ss:
      self.docstring+=ss+"\n"
    self.generic_visit(node)

  def visit_ClassDef(self,node):
    ss =ast.get_docstring(node)
    if ss:
      self.docstring+=ss+"\n"
    self.generic_visit(node)

  def visit_Module(self,node):
    ss =ast.get_docstring(node)
    if ss:
      self.docstring+=ss+"\n"
    self.generic_visit(node)


curdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.abspath(os.path.join(curdir,".."))


def fw_mod_docstring(f,fms,src,pref=""):
  with open(src) as ff:
    cnt = ff.read()
  tree = ast.parse(cnt)
  vdoc = VDocExtractor()
  vdoc.visit(tree)
  if fms=="__builtins__":
    fms = "Zerynth Builtins"
  f.write(("*"*len(pref+fms))+"\n")
  f.write(pref+fms+"\n")
  f.write(("*"*len(pref+fms))+"\n\n")
  f.write(vdoc.docstring)



def generate(conf,tocname="__toc.rst"):
  if "files" in conf:
    rsts = []
    for item in conf["files"]:
      title = item[0]
      file = item[1]
      if file.endswith(".rst"):
        rsts.append(os.path.relpath(os.path.join(curdir,file),curdir))
      elif file.endswith(".py"):
        filename = os.path.relpath(file,os.path.dirname(curdir))
        rstfile = os.path.join(curdir,filename.replace(".py","").replace("/","_").replace("\\","_")+".rst")
        pyfile = os.path.join(libdir,file)
        with open(rstfile,"w") as ww:
          with open(pyfile,"r") as rr:
            contents = rr.read()
          tree = ast.parse(contents)
          vdoc = VDocExtractor()
          vdoc.visit(tree)
          ww.write(vdoc.docstring)
        rsts.append(os.path.relpath(rstfile,curdir))
      elif file.endswith(".c") or file.endswith(".h"):
        filename = os.path.relpath(file,os.path.dirname(curdir))
        rstfile = os.path.join(curdir,filename[:-2].replace("/","_").replace("\\","_")+"_"+file[-1]+".rst")
        cfile = os.path.join(libdir,file)
        with open(rstfile,"w") as ww:
          with open(cfile,"r") as rr:
            contents = rr.read()
            lines= contents.split("\n")
            ww.write(".. default-domain:: c\n\n")
            incomment=False
            for line in lines:
              if not incomment:
                if line.startswith("///") or line.startswith("//!"):
                  ww.write(re.sub("^/+","",line)+"\n")
                elif line.startswith("/**"):
                  incomment=True
              else:
                if line.startswith("*/"):
                  incomment=False
                else:
                  ww.write(line+"\n")
        rsts.append(os.path.relpath(rstfile,curdir))
      elif file.endswith(".json"):
        with open(file,"r") as jj:
          cc = json.load(jj)
        tocfile=file.replace(".json",".rst")
        generate(cc,tocname=tocfile)
        rsts.append(os.path.relpath(tocfile,curdir))

    with open(tocname,"w") as ww:
      if tocname!="__toc.rst":
        if "label" in conf:
          ww.write(".. _"+conf["label"]+":\n\n");  
        ww.write("*"*len(conf["title"]))
        ww.write("\n")
        ww.write(conf["title"]+"\n")
        ww.write("*"*len(conf["title"]))
        ww.write("\n\n")
        ww.write(conf["text"])
        ww.write("\n\n")
      ww.write(
    """
    Contents:

    .. toctree::
       :maxdepth: """+str(tocdepth)+"""

""")
      for rst in rsts:
        ww.write("       "+rst.replace(".rst","")+"\n")
      ww.write("\n")
  else:
    with open(tocname,"w") as ww:
      ww.write("")

generate(conf)
