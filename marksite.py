# python library modules
import os
import argparse
import pickle
# user defined modules
import tree

if __name__ == "__main__":
	# get command line arguments with argparse
	parser = argparse.ArgumentParser(description="Marksite utility to build and upload a website written in markdown.")
	
	# path which contains the website
	parser.add_argument("path")
	# command line actions
	parser.add_argument("-i", "--init", action="store_true", help="Init a site project")
	parser.add_argument("-l", "--list", action="store_true", help="Lists the website tree structure")
	parser.add_argument("-u", "--update", action="store_true", help="Check for changes")
	parser.add_argument("-r", "--reset", action="store_true", help="Resets a project removing all metadata")
	parser.add_argument("-b", "--build", action="store_true", help="Builds markdown files to html, applying the theme")
	parser.add_argument("-s", "--sync", action="store_true", help="Syncs the site to a remote FTP server")
	
	args = parser.parse_args()
	
	
	# useful paths
	base_path = os.path.abspath(args.path) # absolute path to the directory that contains the website
	src_path = os.path.join(base_path, "source/")
	build_path = os.path.join(base_path, "build/")
	
	if args.init:
		# build the file tree
		site_tree = tree.tree(src_path)
	
	if args.list or args.update:
		# load saved tree
		try:
			with open(os.path.join(base_path, "tree.obj"), "rb") as infile:
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
	
	if args.init or args.update:
		# save build file tree
		with open(os.path.join(base_path, "tree.obj"), "wb") as outfile:
			pickle.dump(site_tree, outfile)
