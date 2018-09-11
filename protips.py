#! /usr/bin/python3

# Read SteamAPIs Steam AppId list.
import json
import urllib.request

# Read protonutil.conf
import configparser

# Check for files in the OS
import os.path
import os
from glob import glob

# Self explanatory
import translate

# Some helpers
def isType(var, typ):
	try:
		typ(var)
		return True
	except ValueError:
		return False

# Actual prefix manipulation
import subprocess
import shutil

# Alias this long name
trans = translate.doTranslate

# Some vars that will be useful later
ailist_f = None
ailist = None
conf = configparser.ConfigParser()

# Function to download Steam AppIds
def downloadSteamAppIds():
    if os.path.isfile("appid-list.json"): os.remove("appid-list.json")
    with urllib.request.urlopen("http://api.steampowered.com/ISteamApps/GetAppList/v2") as ailist_req:
        ailist_f = open("appid-list.json", mode="x")
        for b in ailist_req.read():
            ailist_f.write(chr(b))
        ailist_f.close()
        
# Function to ask for Proton version:
def askForProton():
    # Find Proton versions (Steam Apps that begin with Proton)
    potential_provers = glob(f"{conf['Steam']['LibraryPath']}/steamapps/common/Proton*/")
    
    # Show user and ask
    print(trans(lang, "proton-ver-found"))
    for index, prover in enumerate(potential_provers):
        print(f"{index+1}: {os.path.basename(os.path.normpath(prover))}")
    while True:
        ver = input(trans(lang, "proton-ver-prompt"))
        if isType(ver,int):
            ver = int(ver)
            if ver <= len(potential_provers):
                break
    conf["Steam"]["ProtonPath"] = potential_provers[ver-1].rstrip("/\n")
        
if not os.path.isfile("appid-list.json"):
    print("Steam appids download...")
    downloadSteamAppIds()
    
        
# Read steam appids
ailist_f = open("appid-list.json","r")
ailist = json.load(ailist_f)
print("Steam appid list ok")
ailist_f.close()

# Read conf if exists
if os.path.isfile("protonutil.conf"):
    conf.read("protonutil.conf")
else:
    # Do first time setup if not
    conf["ProtonUtil"] = {}
    
    # Ask for language
    print(translate.langList())
    lang = ""
    # Until user gives valid language
    while not lang in translate.langList():
        lang = input("Lang?:")
        conf["ProtonUtil"]["Lang"] = lang
    
    # Ask for Steam Library
    conf["Steam"] = {}
    conf["Steam"]["LibraryPath"] = input(trans(lng, "steam-lib-prompt")).strip().rstrip("/\n")
    
    # Ask for Proton version
    conf["Steam"]["ProtonPath"] = ""
    askForProton()
    # Save setup
    conf.write(open("protonutil.conf","x"))

# Load setting to shorter variables
lang = conf["ProtonUtil"]["Lang"].rstrip("/\n")
libpath = conf["Steam"]["LibraryPath"].rstrip("/\n")
propath = conf["Steam"]["ProtonPath"].rstrip("/\n")
winepath = f"{propath}/dist/bin/wine"
os.environ["WINE"] = winepath
os.environ["WINESERVER"] = winepath+"server"

# Re inform user where Steam Library is
print(trans(lang, "steam-lib-use", libpath))

print(trans(lang, "compatdata-look"))

game_dict = {}

# Find all games in compatdata
for game in glob(libpath + "/steamapps/compatdata/*/"):
    appid = int(os.path.basename(os.path.normpath(game)))
    name  = trans(lang, "no-name") # Default to unnamed language-specific
    
    # Check if a prefix has been made, then add to game dict
    if os.path.isdir(game + "pfx/"):
        for entry in ailist["applist"]["apps"]:
            if int(entry["appid"]) == appid:
                name = entry["name"]
        game_dict[appid] = name
        
# Give list of found games
print(trans(lang, "following-proton-found"))
for appid, game in game_dict.items():
    print(f"AppId {appid}: {game}")
    
# Ask until user gives valid appid
while True:
    try:
        appid = int(input(trans(lang, "appid-prompt")))
        if appid in game_dict.keys(): # Right appid given
            prefixpath = f"{libpath}/steamapps/compatdata/{appid}/pfx" # Set prefix path to a quick variable
            os.environ["WINEPREFIX"] = prefixpath # Set the environment variable for winetricks-'n'-stuff
            break # Leave the loop
    except ValueError:
        pass
    print(trans(lang,"invalid-num"))
    
### ACTUAL UTILS ###
    
# Call winetricks
def winetrick():
    install = input(trans(lang, "winetrick-prompt")).strip().split(" ")
    args = ["winetricks"]
    args.extend(install)
    #args.append("-q")
    subprocess.call(args)

# Run stuff on prefix
def prefixrun():
    program = input(trans(lang, "prefixrun-prompt"))
    subprocess.call([winepath, program])

# Set a 32 bit prefix from a 64 bit one
def convert32():
    try:
        # Only allow if it's a number and it's the appid
        convert_confirm = int(input(trans(lang, "convert32-prompt")))
        if convert_confirm != appid:
            raise ValueError("Not AppId")
        else:
            # Done right!
            if not os.path.isdir(prefixpath+".bak64"): # Is there no backup?
                shutil.move(prefixpath, prefixpath+".bak64") # Make one.
                os.mkdir(prefixpath) # Setup a new prefix
                os.environ["WINEARCH"] = "win32" # A 32-bit one!
                subprocess.call([winepath, "wineboot"]) # Create a default prefix
                del os.environ["WINEARCH"] # Do not let it contaminate other settings
                shutil.rmtree(prefixpath+"/drive_c/windows/system32") # Delete default wine libs
                shutil.rmtree(prefixpath+"/drive_c/users") # Delete default user dir
                shutil.rmtree(prefixpath+"/drive_c/Program Files") # Delete default program files dir
                shutil.copytree(prefixpath+".bak64/drive_c/windows/syswow64",prefixpath+"/drive_c/windows/system32") # Copy 32-bit libraries
                shutil.copytree(prefixpath+".bak64/drive_c/windows/syswow64",prefixpath+"/drive_c/windows/syswow64") # Copy them again because Proton really wants to see this one.
                shutil.copytree(prefixpath+".bak64/drive_c/Program Files (x86)",prefixpath+"/drive_c/Program Files") # Copy 32-bit steam libs
                shutil.copytree(prefixpath+".bak64/drive_c/users",prefixpath+"/drive_c/users") # Copy users dir
            else: # There IS a backup!
                print(trans(lang,"already32-info")) # Tell backup will be restored
                shutil.rmtree(prefixpath) # Remove 32bit prefix
                shutil.move(prefixpath+".bak64", prefixpath) # Move the old 64bit to its place
                print(trans(lang,"done")) # DONE!
            
    except ValueError: # Not a number or not appid
        print(trans(lang, "convert32-abort"))

# Enable 32 bit proton
def proton32():
    # Same confirmation stuff
    try:
        convert_confirm = int(input(trans(lang, "convert32-prompt")))
        if convert_confirm != appid:
            raise ValueError("Not AppId")
        else: # It really wants to live
            if not os.path.isfile(propath+"/proton.bak64"): # Check if backup has been made
                os.rename(propath+"/proton", propath+"/proton.bak64") # Make backup
                with open(propath+"/proton.bak64") as proton_f: # Open the backup
                    proton32_f = open(propath+"/proton","x") # Create new proton executable
                    proton32_f.write(proton_f.read().replace("wine64", "wine")) # Disable force wine64
                    proton_f.close() 
                    proton32_f.close() # Close both files
                    shutil.copymode(propath+"/proton.bak64",propath+"/proton") # Copy exec permission
            else: # Same backup stuff
                print(trans(lang,"already32-info"))
                os.remove(propath+"/proton")
                shutil.move(propath+"/proton.bak64", propath+"/proton")
                print(trans(lang,"done"))
    except ValueError: # Same abort if NaN or NaAI
        print(trans(lang, "convert32-abort"))
    
def hackerman():
    oldpwd = os.getcwd()
    os.chdir(prefixpath)
    subprocess.call([os.environ["SHELL"]])
    os.chdir(oldpwd)
    # Just chdir to prefix, start the shell, move back

def setLib():
    libpath = input(trans(lang, "steam-lib-prompt"))
    conf["Steam"]["LibraryPath"] = libpath
    
def saveAndExit():
    conf.write(open("protonutil.conf","w"))
    exit()
    
# Poor man's Select Case
opts = {
    "1": winetrick,
    "2": prefixrun,
    "3": convert32,
    "4": proton32,
    "5": hackerman,
    "a": downloadSteamAppIds,
    "p": askForProton,
    "l": setLib,
    "q": saveAndExit
}
    
while True:
    print(trans(lang, "you-appid", game_dict[appid]))
    print(trans(lang, "todo-prompt"))
    print()
    print(f"1: {trans(lang, 'winetrick-install')}")
    print(f"2: {trans(lang, 'prefixrun')}")
    print(f"3: {trans(lang, 'convert32')}")
    print(f"4: {trans(lang, 'proton32')}")
    print(f"5: {trans(lang, 'hackerman')}")
    print(f"A: {trans(lang, 'reappid')}")
    print(f"P: {trans(lang, 'proton-change')}")
    print(f"L: {trans(lang, 'lib-change')}")
    print(f"Q: {trans(lang, 'close-this')}")
    print()
    opt = input(trans(lang, "pick-trick")).lower()
    if opt in opts.keys(): # Valid option: Call It & Loop!
        opts[opt]()
        if opt in ["a", "p", "l", "q"]: #options that only take effect after restart
            print(trans(lang, "next-start"))
    else: # Invalid: loop.
        print(trans(lang,"invalid-num"))