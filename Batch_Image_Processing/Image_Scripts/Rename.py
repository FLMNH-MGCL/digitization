import os

def main():
	path = input("Please type the path of the directory: ")
	if not path.endswith("/") or not path.endswith("\\"):
		path + "/"
	
	
	for filename in os.listdir(path):
		fn = filename
		print(fn)
		
		fn = fn.replace(".CR2","")
		print(fn)
		#(2) becomes _V
		fn = fn.replace(" (2)","_V")
		print(fn)
		
		#Spaces to Underscore
		fn = fn.replace(" ", "_")
		print(fn)
		# if not _V or _L become _D
		if (fn.find("_V") == -1 and fn.find("_L") == -1):
			fn += "_D"
		#Write to Filename
		os.rename(path+filename, path+fn+".CR2")
		print(fn)
		
#Driver code 
if __name__ == '__main__': 
      
    # Calling main() function 
    main() 
