import os
import hashlib

# file and directory status costants
NEW = 0
CHANGED = 1
BUILT = 2
UP_TO_DATE = 3
DELETED = 4


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
		self.name = os.path.basename(path)
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
			self.status = NEW
		else:
			raise IOError("Argument must be path to a valid file. Got '{0}'.".format(abs_path))
	
	# checks if file has same md5 as before
	# set status = CHANGED if it has
	def update(self):
		abs_path = os.path.join(self.parent.get_root().path, self.path)
		
		# calculate new md5 of the file
		new_md5 = md5_file(abs_path)
		
		if new_md5 != self.md5:
			self.md5 = new_md5
			self.status = CHANGED


# subclass of Node representing a directory
class Folder(Node):
	def __init__(self, path, parent):
		super(Folder, self).__init__(path, parent)
		
		self.children = {}
		self.status = NEW
	
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
	
	# return string representation of the object
	def __str__(self):
		s = self.name
		cd = self # current directory
		level = 1 # indentation level
		
		for name, child in cd.children.items():
			# newline and identation
			s += "\n" + " |   " * (level - 1) + " +-- "
			
			if isinstance(child, Folder):
				s += str(child).replace("\n", "\n{0}".format(" |   " * level))
			else:
				s += name
		
		return s


# functions which builds and return a tree object
# made up of nodes
def tree(path):
	# this is the tree which starts with the root folder
	t = Folder(path, None)
	
	# assign name to project
	if path[-1] == os.sep:
		t.name = os.path.basename(os.path.dirname(path[:-1]))
	
	# walk directory tree and build the tree object
	for root, dirs, files in os.walk(path):
		# path relative from source directory to current directory
		rel_path = root.replace(t.path, "")
		# current directory node object
		cd = t.get_path(rel_path.split(os.sep))
		
		for d in dirs:
			rpath = os.path.join(rel_path, d) # relative path of folder
			cd.add_child(d, Folder(rpath, cd))
			
		for f in files:
			rpath = os.path.join(rel_path, f) # relative path of file
			cd.add_child(f, File(rpath, cd))
	
	return t

# functions which update passed tree, adding new files, marking
# old files if they changed and marking deleted files as no more existent
def update(t):
	# walk directories to update the tree object
	for root, dirs, files in os.walk(t.path):
		# path relative from source directory to current directory
		rel_path = root.replace(t.path, "")
		# current directory node object
		cd = t.get_path(rel_path.split(os.sep))
		
		for d in dirs:
			if d not in cd.children:
				rpath = os.path.join(rel_path, d) # relative path of folder
				cd.add_child(d, Folder(rpath, cd))
			
		for f in files:
			if f in cd.children:
				cd.children[f].update()
			else:
				rpath = os.path.join(rel_path, f) # relative path of file
				cd.add_child(f, File(rpath, cd))
		
		for child in cd.children:
			if child not in dirs + files:
				child.status = DELETED
	
	return t
