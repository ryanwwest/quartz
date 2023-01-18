import sys
import os
import re
import shutil

# This script finds all of the blog entries in zk/blog along with all images that the entries reference,
# and outputs a list of file paths for all of each for rsync to copy into ~/g/quartz/content/[media/]. 
# This script previously just copied over the files without rsync, but problems with that approach:
# 1. needless recopying of unchanged data (especially as the number of images grows)
# 2. Python could be slower than rsync

# The script assumes that ALL blog markdown will be in the same folder (not nested), and the same for 
# images but in a separate folder

# usage: python3 list-all-obsidian-blog-files.py path/to/image-dir path/to/blog-dir
#    ex: python3 list-all-obsidian-blog-files.py /s/zk/media/ /s/zk/blog/

# naive because matches [[image.png^anything invalid after .png]]. should only match | after
regex = re.compile("\[\[(.*\.png|.*\.jpeg|.*\.jpg|.*\.gif).*\]\]", flags=re.IGNORECASE)

# While I store all my images in the media/ dir of my Obsidian vault, this looks through the whole vault
def find_image_filenames_in_one_blog_entry(blog_path, image_vault_dir):
    # first get the filenames in the file (could also be full paths)
    with open(blog_path, mode="rt", encoding="utf-8") as f:
        entry = f.read()
        image_filenames = re.findall(regex, entry)
        return image_filenames
            
# only lists files that match extensions TUPLE. single-level.
def enumerate_files_in_path(path, extensions):
    matches = []
    matches_with_paths = []
    directory = os.fsdecode(path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.lower().endswith(extensions):
            matches_with_paths.append(os.path.join(directory, filename))
            # rsync requires the source directory path anyway, so redundant here
            matches.append(filename)
    return matches_with_paths, matches

def get_image_paths_from_blog_entries(blog_entries, image_vault_dir):
    image_filenames = set()
    _, all_image_filenames = enumerate_files_in_path(image_vault_dir, (".png", ".jpeg", ".jpg", ".gif"))
    for entry in blog_entries:
        image_filenames.update(find_image_filenames_in_one_blog_entry(entry, image_vault_dir))
    used_image_filenames = set()
    # O(n^2) here, could likely make way more efficient
    for image_filename in image_filenames:
        found_image = False
        for all_image_filename in all_image_filenames:
            if all_image_filename.lower() == image_filename.lower():
                used_image_filenames.add(all_image_filename)
                # all_image_paths.remove(image_path) this could be more efficient, but then if two filenames are profile.png and /media/profile.png, the second one will show the below warning since it can't match anymore.
                found_image = True
                break
        if not found_image:
            print(f'warning: image filename {image_filename} not found in images directory')
    return used_image_filenames

# unused now that this script doesn't do any actual copying but defers to rsync
def copy_files_to_dir(filepaths, dest):
    for path in filepaths:
        if os.path.isfile(path):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(path, dest)
    print(f'copied {len(filepaths)} files into {dest}')

def save_pathstrings_to_file(paths, filename):
    with open(filename, 'w') as f:
        for path in paths:
            f.write(f"{path}\n")


if __name__ == "__main__":
    # while this could be the full vault, I'm just passing in zk/media so it doesn't have to 
    # search through as many files each time since I know all images are there. would have to 
    # make enumerate_files_in_path recursive if I change my mind later.
    image_vault_dir = sys.argv[1]  
    # flat directory where all blogpost markdown is found
    blog_vault_dir = sys.argv[2]
    # destination where the found image files should be copied into
    #image_out_dir = sys.argv[3]
    # destination where the blog files should be copied into
    #blog_out_dir = sys.argv[4]

    # O(n^2) operation comparing found image filenames to all images in media/ dir...  # todo improve
    # using the paths for reading the files in this script, and the filenamesalone for saving to file later
    blog_filepaths, blog_filenames_only = enumerate_files_in_path(blog_vault_dir, (".md"))
    # print(blog_files)
    image_paths = get_image_paths_from_blog_entries(blog_filepaths, image_vault_dir)

    if len(blog_filepaths) == 0 or len(image_paths) == 0:
        print("Warning: Didn't find any of either blog or image files. There might be a problem with the specified directories.")
    print(f'Saving {len(blog_filepaths)} blog article .md filepaths and {len(image_paths)} blog image filepaths to /tmp/blog-*.txt')
    save_pathstrings_to_file(blog_filenames_only, "/tmp/blog-markdown-paths-obsidian-to-quartz.txt")
    save_pathstrings_to_file(image_paths, "/tmp/blog-image-paths-obsidian-to-quartz.txt")
    # print(image_paths)
    #copy_files_to_dir(image_paths, image_out_dir)
    # this is surely less efficient than a more basic file copy mechanism like cp
    #copy_files_to_dir(blog_files, blog_out_dir)
