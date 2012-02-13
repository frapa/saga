import os
import string
import shutil

# checks if the user defined a theme
def user_theme_exists(path):
	if os.path.exists(os.path.join(path, "theme")):
		return True
	else:
		return False

# checks whether an user defined theme exists
# and copy default one if not
def check(bin_path, base_path):
	if not user_theme_exists(base_path):
		shutil.copytree(os.path.join(bin_path, "themes", "default"),
			os.path.join(base_path, "theme"))

# load theme from file
def load_theme(path):
	try:
		with open(os.path.join(path, "theme", "template.html")) as template_file:
			template = template_file.read()
	except IOError:
		print("Malformed theme")
		exit(0)
	
	return string.Template(template)
