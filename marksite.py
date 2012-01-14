import sys
import os
import argparse
import hashlib
import itertools
import string
import shutil
import ftplib
import markdown

class Folder:
	def __init__(self, cli):
		self.program_path = os.path.abspath(os.path.dirname(sys.argv[0]))
		self.base_path = os.path.abspath(cli.path) + os.sep
		self.compile_path = os.path.join(self.base_path, ".compile")
		
		# copy theme
		if os.path.exists(os.path.join(self.base_path, "template.html")):
			self.theme_path = self.base_path
		else:
			self.theme_path = os.path.join(self.program_path, "themes", "default")
			
			if os.path.exists(os.path.join(self.base_path, "style")):
				shutil.rmtree(os.path.join(self.base_path, "style"))
			
			shutil.copytree(os.path.join(self.theme_path, "style"),
				os.path.join(self.base_path, "style"))
		
		self.folders = []
		self.files = {}
		for root, dirs, fs in os.walk(self.base_path):
			r_dirs = []
			for folder in dirs:
				if folder[0] == '.' or folder == "__pycache__":
					r_dirs.append(folder)
				else:
					self.folders.append(os.path.join(root.replace(self.base_path, ""), folder))
			
			for d in r_dirs:
				dirs.remove(d) 
		
			for f in fs:
				name, ext = os.path.splitext(f)
				if not (root == self.base_path and f == "crusade_settings.py") and ext not in (".pyc"):
					with open(os.path.join(root, f), "rb") as f_obj:
						digest = hashlib.md5(f_obj.read()).hexdigest()
				
					self.files[os.path.join(root.replace(self.base_path, ""), f)] = digest
		
		if cli.reset:
			shutil.rmtree(self.compile_path)
		
		self.new_dirs = []
		self.deleted_dirs = []
		self.new_files = []
		self.changed_files = []
		self.deleted_files = []
		if not os.path.exists(self.compile_path):
			os.mkdir(self.compile_path)
			self.new_dirs = self.folders
			self.new_files = self.files.keys()
		else:
			sys.path.append(self.compile_path)
			tree = __import__('crusade_tree', globals(), locals(), [], -1)
		
			if self.folders != tree.folders:
				for folder in folders:
					if self.folder not in tree.folders:
						self.new_dirs.append(folder)
			
				for self.folder in tree.folders:
					if folder not in self.folders:
						self.deleted_dirs.append(folder)
		
			if self.files != tree.files:
				for f in self.files:
					if f not in tree.files:
						self.new_files.append(f)
					elif self.files[f] != tree.files[f]:
						self.changed_files.append(f)
			
				for f in tree.files:
					if f not in self.files:
						self.deleted_files.append(f)
	
	def compile_markdown(self):
		template = None
		with open(os.path.join(self.theme_path, "template.html")) as tf:
			template = string.Template(tf.read())
		
		# compiles all markdown files
		for mdf in itertools.chain(self.new_files, self.changed_files):
			name, ext = os.path.splitext(mdf)
			if ext == ".md":
				with open(os.path.join(self.base_path, mdf)) as in_file:
					try:
						os.makedirs(os.path.dirname(os.path.join(self.compile_path, mdf)))
					except OSError:
						pass
				
					with open(os.path.join(self.compile_path, name + ".html"), "w") as out_file:
						site_name = os.path.basename(self.base_path[:-1])
						path_to_page = os.path.dirname(name).split(os.sep)
						if path_to_page == [""]:
							title = site_name
						else:
							path_to_page.insert(0, site_name)
							title = " » ".join(path_to_page)
						
						css_path = os.path.join("../" * (len(os.path.dirname(mdf).split(os.sep))-1), "style")
						body = markdown.markdown(in_file.read(), ['extra'])
						
						html = template.substitute(title=title,
							css_path=css_path, body=body)
						
						out_file.write(html)
	
	def sync(self):
		# sync files
		sys.path.append(self.base_path)
		settings = __import__('crusade_settings', globals(), locals(), [], -1)
	
		ftp = ftplib.FTP(settings.host, settings.username, settings.password)
		ftp.cwd(settings.root)
	
		for d in self.new_dirs:
			try:
				ftp.mkd(d)
			except ftplib.error_perm:
				# directory already exists
				print("error with directory: {}".format(d))
	
		for f in itertools.chain(self.new_files, self.changed_files):
			name, ext = os.path.splitext(f)
			if ext == ".md":
				with open(os.path.join(self.compile_path, name + ".html"), "rb") as f_obj:
					ftp.storbinary("STOR {}".format(name + ".html"), f_obj)
			else:
				with open(os.path.join(self.base_path, f), "rb") as f_obj:
					ftp.storbinary("STOR {}".format(f), f_obj)
	
		for d in self.deleted_dirs:
			ftp.rmd(d)
	
		for f in self.deleted_files:
			name, ext = os.path.splitext(f)
			if ext == ".md":
				ftp.delete(f[:-3] + ".html")
			else:
				ftp.delete(f)
		
		ftp.quit()
	
	def update(self):
		tree_str = "folders = {fol}\nfiles = {fil}".format(fol=repr(self.folders), fil=repr(self.files))
		with open(os.path.join(self.compile_path, "crusade_tree.py"), "w") as tree_file:
			tree_file.write(tree_str)

if __name__ == "__main__":
	parser = argparse.ArgumentParser("")
	parser.add_argument("path")
	parser.add_argument("-r", "-reset", dest="reset", action="store_true", default=False)
	cli = parser.parse_args()
	
	folder = Folder(cli)
	folder.compile_markdown()
	folder.sync()
	folder.update()
