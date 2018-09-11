#! usr/bin/python3

# Some random translation library

from glob import glob
from os.path import basename, splitext

lang_patharray = glob("lang/*.lang")
lang_fdata = [(splitext(basename(lang_path))[0], open(lang_path)) for lang_path in lang_patharray]
lang_metadict = {}

for name, lang_f in lang_fdata:
	content = lang_f.read()
	lang_dict = {}
	for line in content.split("\n"):
		if not (line.startswith("#") or line.strip() == ""):
			source, translate = line.strip().split(" ", 1)
			lang_dict[source] = translate.replace("%n","\n")
	lang_metadict[name] = lang_dict
	
def doTranslate(lang, source, *perct):
	temp = lang_metadict[lang][source]
	for index, formatted in enumerate(perct):
		temp = temp.replace(f"%{index}", formatted)
	return temp

def langList():
	return list(lang_metadict.keys())
	