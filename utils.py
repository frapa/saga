import os
import string
# user defined modules
import tree

try:
	import misaka
except ImportError:
	print("Dependency not installed: misaka")
	exit(1)

# makes sure folders in the path exists
def assure_path(path):
	if not os.path.isdir(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))

# convert markdown file to html
def convert_file(build_path, node, template=string.Template("$body")):
	in_path = os.path.join(node.parent.get_root().path, node.path)
	out_path = os.path.join(build_path, os.path.splitext(node.path)[0] + ".html")
	
	assure_path(out_path)
	
	with open(in_path) as infile:
		body = misaka.html(infile.read(),
			misaka.EXT_TABLES | misaka.EXT_FENCED_CODE | misaka.EXT_SUPERSCRIPT)
	
	title = os.path.splitext(node.name)[0]
	css = os.path.join("../"*(len(node.path.split(os.sep)) - 1), "theme")
	html = template.safe_substitute(title=title, body=body, css_path=css)
	
	with open(out_path, "w") as outfile:
		outfile.write(html)
