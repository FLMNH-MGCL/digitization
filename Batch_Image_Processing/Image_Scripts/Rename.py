import os

def main():
	i = 0
	path = input("Please type the path of the directory: ")
	if not path.endswith("/") or not path.endswith("\\"):
		path + "/"
	
	
	for filename in os.listdir(path):
		fn = filename
		
		fn.replace(".CR2","\0")
		#(2) becomes _V
		fn.replace("(2)","_V")
		
		#Spaces to Underscore
		fn.replace(" ", "_")
		# if not _V or _L become _D
		if (fn.find("_V") == -1 and fn.find("_L") == -1):
			fn += "_D"
		#Write to Filename
		os.rename(path+filename, path+fn)
		
#Driver code 
if __name__ == '__main__': 
      
    # Calling main() function 
    main() 
