import os
import hashlib

# file and directory status costants
NEW = 0
CHANGED = 1
TO_BE_REMOVED = 2


# efficentley calculate md5 of a file
# this function assumes the path is a
# valid path to a file
def md5_file(path):
	hash_str = ""	
	
	with open(path, "rb") as f:
		md5 = hashlib.md5()
		md5.update(f.read(md5.block_size*100))
		hash_str = md5.hexdigest()
	
	return hash_str


# class representing a node (file or folder)
# a node can be the parent of other nodes
class Node:
	def __init__(self, path, parent):
		self.path = path
		self.parent = parent
	
	def get_parent(self):
		if self.parent != None:
			return self.parent
		else:
			# there is no parent, which means this node is the root node
			# so raise error
			raise Exception("This node has no parent (root node).")
	
	def get_root(self):
		node = self
		try:
			while True:
				node = node.get_parent()
		except Exception:
			return node
	

# subclass of Node representing a file
class File(Node):
	def __init__(self, path, parent):
		abs_path = os.path.join(parent.get_root().path, path)
		
		# check whether path arguments is a valid file path
		# raise error if not
		if os.path.isfile(abs_path):
			super(File, self).__init__(path, parent)
			
			# calculate md5 for the file
			self.md5 = md5_file(abs_path)
		else:
			raise IOError("Argument must be path to a valid file.")


# subclass of Node representing a directory
class Folder(Node):
	def __init__(self, path, parent):
		super(Folder, self).__init__(path, parent)
		
		self.children = {}
	
	def add_child(self, name, node):
		self.children[name] = node
	
	# recursive way to get the node object from its relative path (list)
	def get_path(self, path):
		try:
			path.remove('')
		except ValueError:
			pass
		
		if len(path) == 0:
			return self
		elif len(path) == 1:
			return self.children[path[0]]
		else:
			return self.children[path[0]].get_path(path[1:])


# functions which builds and return a tree object
# made up of nodes
def tree(path):
	# this is the tree which starts with the root folder
	t = Folder(path, None)
	
	# walk directory tree and build the tree object
	for root, dirs, files in os.walk(path):
		# path relative from source directory to current directory
		rel_path = root.replace(t.path, "")
		# current directory node object
		cd = t.get_path(rel_path.split(os.sep))
		print(cd)
		
		for d in dirs:
			rpath = os.path.join(rel_path, d) # relative path of folder
			cd.add_child(d, Folder(rpath, cd))
			
		for f in files:
			rpath = os.path.join(rel_path, f) # relative path of file
			cd.add_child(f, File(rpath, cd))
	
	return t
