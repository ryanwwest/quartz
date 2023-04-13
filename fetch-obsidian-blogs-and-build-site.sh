# to build site into the default local quartz/public/ directory (where nginx serves the x/ryanwwest.com/ staging site), run this script with no parameters
# to build site to production (to the websitev4-publichtml local git repo which a cronjob git pushes to the ryanwwest.com hosting server) add -p flag (or add a custom directory to build public site there
set -e # fail on any error

HUGO_PUBLIC_DIR_OUTPUT="${1:-/home/rww/g/quartz/public/}"
HUGO_ARGS="--buildDrafts"
if [[ "$1" = "-p" ]] ; then  # for publishing to production
    HUGO_PUBLIC_DIR_OUTPUT="/home/rww/g/websitev4-publichtml/public_html/"
    HUGO_ARGS=""
fi
echo --- Publishing site to $HUGO_PUBLIC_DIR_OUTPUT ---

# files get listed into /tmp/blog-*.txt files, and then rsync uses the file lists to sync over any changes into g/quartz/content/
# file modification and access times are preserved, but created time cannot be preserved on linux and instead will equal the rsync run time: https://unix.stackexchange.com/questions/636160/why-rsync-on-linux-does-not-preserve-all-timestamps-creation-time
python3 list-all-obsidian-blog-files.py /s/zk/media/ /s/zk/blog/
rsync --atimes --times --files-from=/tmp/blog-markdown-paths-obsidian-to-quartz.txt /s/zk/blog/ /home/rww/g/quartz/content/
rsync --atimes --times --files-from=/tmp/blog-image-paths-obsidian-to-quartz.txt /s/zk/media/ /home/rww/g/quartz/content/media/

# hugo-obsidian creates tags and taxonomies and links in json for quartz to use
echo --- Running hugo-obsidian to create tags/links/taxonomies ---
/home/rww/go/bin/hugo-obsidian -input=content -output=assets/indices -index=true -root=.

# necessary because hugo doesn't delete existing files in public/ output folder by default, which is mostly fine but quartz creates json files in public/indices for taxonomy and link lists and the filename changes according to its md5 hash (and old versions aren't deleted). I could alternatively just change the filename to not include that in the filepath to skip this.
# this seems dangerous if the first argument passed in somehow had a space in it like '~ dir/path' which could delete an unintended folder, but I don't think that's possible with one argument alone
rm -rf "$HUGO_PUBLIC_DIR_OUTPUT"indices/*Index*.min.json

# hugo builds static html site in public/ (or another location such as production websitev4-publichtml/public_html/) using all of the above
echo --- Building static site with hugo ---
hugo --destination $HUGO_PUBLIC_DIR_OUTPUT $HUGO_ARGS

