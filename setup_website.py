import sys
import os

if __name__ == "__main__":
	host = input("ftp host: ")
	nickname = input("nickname: ")
	password = input("password (will be stored as plain txt): ")
	root = input("root folder (on the ftp host): ")
	
	path = os.getcwd()
	
	with open(os.path.join(path, "settings.txt"), "w") as outfile:
		outfile.write("host = {0}\n".format(host))
		outfile.write("nickname = {0}\n".format(nickname))
		outfile.write("password = {0}\n".format(password))
		outfile.write("root = {0}".format(root))
	
	try:
		os.mkdir(os.path.join(path, "source"))
	except OSError:
		pass
	
	print("Setup completed!")
	print("You can now start adding file to the source directory!")
