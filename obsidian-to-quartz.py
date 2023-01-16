import sys
import os
import re
import shutil

# This script fetches all of the blog entries in zk/blog along with all images that the entries reference,
# and puts them into content/ and content/media/.

# usage: python3 obsidian-to-quartz.py ~/g/zk/media/ ~/g/zk/blog/ ~/g/quartz/content/media/ ~/g/quartz/content/

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
    directory = os.fsdecode(path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.lower().endswith(extensions):
            matches.append(os.path.join(directory, filename))
    return matches

def get_image_paths_from_blog_entries(blog_entries, image_vault_dir):
    image_filenames = set()
    all_image_paths = enumerate_files_in_path(image_vault_dir, (".png", ".jpeg", ".jpg", ".gif"))
    for entry in blog_entries:
        image_filenames.update(find_image_filenames_in_one_blog_entry(entry, image_vault_dir))
    used_image_filepaths = set()
    # O(n^2) here, could likely make way more efficient
    for image_filename in image_filenames:
        found_image_path = False
        for image_path in all_image_paths:
            if image_path.lower().endswith(image_filename.lower()):
                used_image_filepaths.add(image_path)
                # all_image_paths.remove(image_path) this could be more efficient, but then if two filenames are profile.png and /media/profile.png, the second one will show the below warning since it can't match anymore.
                found_image_path = True
                break
        if not found_image_path:
            print(f'warning: image filename {image_filename} not found in images directory')
    return used_image_filepaths

def copy_files_to_dir(filepaths, dest):
    for path in filepaths:
        if os.path.isfile(path):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(path, dest)
    print(f'copied {len(filepaths)} files into {dest}')


if __name__ == "__main__":
    # while this could be the full vault, I'm just passing in zk/media so it doesn't have to 
    # search through as many files each time since I know all images are there. would have to 
    # make enumerate_files_in_path recursive if I change my mind later.
    image_vault_dir = sys.argv[1]  
    # flat directory where all blogpost markdown is found
    blog_vault_dir = sys.argv[2]
    # destination where the found image files should be copied into
    image_out_dir = sys.argv[3]
    # destination where the blog files should be copied into
    blog_out_dir = sys.argv[4]


    # O(n^2) operation comparing found image filenames to all images in media/ dir...
    # todo improve
    blog_files = enumerate_files_in_path(blog_vault_dir, (".md"))
    # print(blog_files)
    image_paths = get_image_paths_from_blog_entries(blog_files, image_vault_dir)
    # print(image_paths)
    copy_files_to_dir(image_paths, image_out_dir)
    # this is surely less efficient than a more basic file copy mechanism like cp
    copy_files_to_dir(blog_files, blog_out_dir)
