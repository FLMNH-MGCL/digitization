import os

def main():
	ext = ".CR2"
	print("This program will help you rename " + ext + " files in a directory")
	path = input("Please type the path of the directory: ")
	
	# Valid paths must end in a separator, this checks and adds one
	# Every os fs accepts "/", yup even Windows, cool right!?
	if not path.endswith("/") or not path.endswith("\\"):
		path += "/" 
	
	
	for filename in os.listdir(path):
		#fn represents the new filename
		fn = filename 
		
		# Only rename cr2 images
		if (fn.find(ext) != -1):
			# remove extension for now
			fn = fn.replace(ext,"")
			
			#" (2)" becomes _V (Use the space to avoid double underscore
			fn = fn.replace(" (2)","_V")
			
			# Spaces to Underscore
			fn = fn.replace(" ", "_")
			
			# if not _V or _L or _D become _D
			if (fn.find("_V") == -1 and fn.find("_L") == -1 and fn.find("_D") == -1):
				fn += "_D"
				
			#Rename if the filename has changed (saves time and processing power)
			if(filename != fn + ext):
				os.rename(path + filename, path + fn +ext)
		
#Driver code 
if __name__ == '__main__': 
      
    # Calling main() function 
    main() 
