# python library modules
import os
import argparse
# user defined modules
import tree

if __name__ == "__main__":
	# get command line arguments with argparse
	parser = argparse.ArgumentParser("")
	
	# path which contains the website
	parser.add_argument("path")
	
	args = parser.parse_args()
	
	
	# useful paths
	base_path = os.path.abspath(args.path) # absolute path to the directory that contains the website
	src_path = os.path.join(base_path, "source")
	build_path = os.path.join(base_path, "build")
	
	# build the file tree
	site_tree = tree.tree(src_path)
