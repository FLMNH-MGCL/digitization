import os
import re

def FixName(imageName):
	# remove male/female distinction
	imageName = imageName.replace("_M", "")
	imageName = imageName.replace("_F", "")
	
	# substitute repeating underscores with single underscore
	imageName = re.sub("\_+", "_", imageName)
	return imageName

# count digit occurences in string
def CountDigits(string):
	return sum(c.isdigit() for c in string)

def main():
	imageName = input("Enter a file name: \n --> ")
	
	newName = FixName(imageName)
	
	print(newName)
	print(str(CountDigits(newName)))

# Driver Code
if __name__ == '__main__':
    main()
