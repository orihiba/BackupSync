import sys
from os import walk, system
from os.path import getmtime, join, isdir, exists, isfile
from time import ctime
from shutil import copytree, copy2

IGNORELIST_PATH = ".ignorelist"

g_new_dirs = []
g_ignorelist = []

def copy_item(src, dst, file_or_dir):
    if file_or_dir == "dir":
        copytree(src, dst)
    else:
        copy2(src, dst)      


def should_copy(src_file, dst_file, file_or_dir):
    # Check ignorelist
    if src_file in g_ignorelist:
        return False
    
    # New item
    if not exists(dst_file):
        if file_or_dir == "dir":
            g_new_dirs.append(src_file)
    
        ans = input("New %s: %s (date: %s).\n\tCopy to %s? [y] {i to ignore item and add to ignorelist} " % (file_or_dir, src_file, ctime(getmtime(src_file)), dst_file))
        if ans == "i":
            add_to_ignorelist(src_file)           
        
        return ans == "y" or len(ans) == 0
       
    # Updated item
    # Relevant only for files
    if file_or_dir == "dir":
        return False

    if getmtime(src_file) > getmtime(dst_file):
        ans = input("Updated %s: %s (date: %s).\n\tCopy and override to %s (date: %s)? [y] " % (file_or_dir, src_file, ctime(getmtime(src_file)), dst_file, ctime(getmtime(dst_file))))
        return ans == "y" or len(ans) == 0


def iterate_files_or_dirs(src_dir, dst_dir, files, file_or_dir):
    for name in files:
        src_file = join(src_dir, name)
        dst_file = join(dst_dir, name)
        
        if should_copy(src_file, dst_file, file_or_dir):
            copy_item(src_file, dst_file, file_or_dir)


def get_dir_relative_location(src_dir, cur_location):
    if not cur_location.startswith(src_dir):
        print("Error...")
        sys.exit(2)

    # Remove first slash
    return cur_location[len(src_dir):].lstrip("\\")
        

def should_skip_dir(cur_dir):
    for dir in g_new_dirs:
        if dir in cur_dir:
            return True
            
    if cur_dir in g_ignorelist:
        return True


def get_ignorelist():
    if not isfile(IGNORELIST_PATH):
        return

    with open(IGNORELIST_PATH, "rb") as f:
        for item in list(f):
            g_ignorelist.append(str(item.strip().decode('UTF-8')))
    

def add_to_ignorelist(filename):
    g_ignorelist.append(filename)
    
    # Create ignorelist file if doesn't exist
    if not isfile(IGNORELIST_PATH):
        with open(IGNORELIST_PATH, "w") as f:
            pass
        system("attrib +h " + IGNORELIST_PATH)
    
    # Update ignorelist file
    with open(IGNORELIST_PATH, "ab") as f:
        data = bytes(filename + "\n", 'UTF-8')
        f.write(data)
     
     
def main(src_dir, bk_dir):
    get_ignorelist()

    for root, dirs, files in walk(src_dir, topdown=True):
        if should_skip_dir(root):
            continue
    
        dir_location = get_dir_relative_location(src_dir, root)
        iterate_files_or_dirs(root, join(bk_dir, dir_location), dirs, "dir")
        iterate_files_or_dirs(root, join(bk_dir, dir_location), files, "file")
        

if __name__ == "__main__":
    if len(sys.argv) != 3 or not isdir(sys.argv[1]) or not isdir(sys.argv[2]):
        print("usage: backup_sync.py <src dir> <backup dir>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])