#! usr/bin/python3

# Some random translation library

# Filesystem utils
from glob import glob
from os.path import basename, splitext

# Get all language files
lang_patharray = glob("lang/*.lang")

# Get language name and file objs in tuples
lang_fdata = [(splitext(basename(lang_path))[0], open(lang_path)) for lang_path in lang_patharray]

# Dictionary of language dictionaries
lang_metadict = {}

# Process files
for name, lang_f in lang_fdata:
	# File text to process
	content = lang_f.read()
	
	# The language dictionary for this language
	lang_dict = {}
	
	# Each line is an item.
	# Format id Translation
	# Example waldo-prompt Where is Waldo?
	for line in content.split("\n"):
		if not (line.startswith("#") or line.strip() == ""): # Not empty or not commend
			source, translate = line.strip().split(" ", 1)
			lang_dict[source] = translate.replace("%n","\n") # Make an entry named after the id with the translation, replace %n with newline
	lang_metadict[name] = lang_dict #Add to metadict
	
def doTranslate(lang, source, *perct): # Get translation
	temp = lang_metadict[lang][source] # Original text
	for index, formatted in enumerate(perct): #Process replacements: %0, %1, %2...
		temp = temp.replace(f"%{index}", formatted)
	return temp # Return with replacements

def langList():
	return list(lang_metadict.keys()) # Get list of languages from metadict keys.
	
