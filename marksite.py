# python library modules
import os
import sys
import argparse
import pickle
import theme
import ftplib
import shutil
# user defined modules
import tree
import utils

if __name__ == "__main__":
	# get command line arguments with argparse
	parser = argparse.ArgumentParser(description="Marksite utility to build and upload a website written in markdown.")
	
	# path which contains the website
	parser.add_argument("path", default=".", nargs="?", help="path to the website project directory (default to working directory)")
	# command line actions
	parser.add_argument("-i", "--init", action="store_true", help="init a site project")
	parser.add_argument("-l", "--list", action="store_true", help="lists the website tree structure")
	parser.add_argument("-u", "--update", action="store_true", help="check for changes")
	parser.add_argument("-r", "--reset", action="store_true", help="resets a project removing all metadata")
	#parser.add_argument("-b", "--build", action="store_true", help="builds markdown files to html, applying the theme")
	parser.add_argument("-s", "--sync", action="store_true", help="syncs the site to a remote FTP server")
	
	args = parser.parse_args()
	
	# useful paths
	base_path = os.path.abspath(args.path) # absolute path to the directory that contains the website
	src_path = os.path.join(base_path, "source/")
	build_path = os.path.join(base_path, ".build/")
	bin_path = os.path.abspath(os.path.dirname(sys.argv[0]))
	
	tree_file = ".tree.pickle"
	
	if args.init:
		# build the file tree
		site_tree = tree.tree(src_path)
	
	if args.list or args.update or args.sync:
		# load saved tree
		try:
			with open(os.path.join(base_path, tree_file), "rb") as infile:
				site_tree = pickle.load(infile)
		except IOError:
			# this means file does not exists
			print("This project as not been inizialized.")
			exit(1)
	
	if args.list:
		# print tree structure
		print(site_tree)
	
	if args.update:
		# update file tree
		site_tree = tree.update(site_tree)
		
		# build markdown files
		try:
			os.mkdir(build_path)
		except OSError:
			# folder already exists
			pass
		
		# set theme if not user-defined
		theme.check(bin_path, base_path)
		# load theme
		template = theme.load_theme(base_path)
		
		for node in site_tree.iter():
			if node.ext in (".md", ".markdown"):
				utils.convert_file(build_path, node, template)
		
		print("Website built sussessfully.")
	
	if args.sync:
		# load ftp settings
		# ok, it's pretty difficult to read i know :)
		with open(os.path.join(base_path, "settings.txt")) as set_file:
			raw = [line.strip() for line in set_file.readlines()]
			settings = dict([[t.strip() for t in line.split("=")]
								for line in raw if line != ""])
		
		# open connection and upload files...
		with ftplib.FTP(settings["host"], settings["user"], settings["password"]) as ftp:
			for node in site_tree.iter():
				if isinstance(node, tree.Folder) and node.parent != None:
					if node.status == tree.NEW:
						path = os.path.join(settings["root"], node.path)
						
						print("Creating {}".format(path))
						
						ftp.mkd(path)
						node.status = tree.UP_TO_DATE
					elif node.status == tree.DELETED:
						path = os.path.join(settings["root"], node.path)
						
						print("Removing {}".format(path))
						
						ftp.rmd(path)
				elif isinstance(node, tree.File):
					if node.status in (tree.NEW, tree.CHANGED):
						if node.ext in (".md", ".markdown"):
							local_path = os.path.join(build_path,
								os.path.splitext(node.path)[0] + ".html")
							server_path = os.path.join(settings["root"],
								os.path.splitext(node.path)[0] + ".html")
						else:
							local_path = os.path.join(src_path, node.path)
							server_path = os.path.join(settings["root"], node.path)
						
						with open(local_path, "rb") as in_file:
							ftp.storbinary("STOR {}".format(server_path), in_file)
						
							print("File {0} {1}".format(node.path,
								{tree.NEW:"uploaded", tree.CHANGED:"updated"}[node.status]))
							node.status = tree.UP_TO_DATE
					
			
			print("Syncronization successful.")
					
	
	if args.init or args.update or args.sync:
		# save build file tree
		with open(os.path.join(base_path, tree_file), "wb") as outfile:
			pickle.dump(site_tree, outfile)
	
	if args.reset:
		if os.path.exists(os.path.join(base_path, tree_file)):
			os.remove(os.path.join(base_path, tree_file))
		
		if os.path.exists(build_path):
			shutil.rmtree(build_path)
