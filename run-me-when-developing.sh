#set -x
#watch -n 5 
bash -c 'rm -rf ~/g/quartz/content/* ~/g/quartz/public/* && python3 obsidian-to-quartz.py /s/zk/media/ /s/zk/blog/ ~/g/quartz/content/media/ ~/g/quartz/content/ && hugo-obsidian -input=content -output=assets/indices -index=true -root=. && hugo'
# python script fetches markdown and images from obsidian vault, places in content/
# hugo-obsidian creates tags and taxonomies and links in json for quartz to use
# hugo builds static html site in public/ using both of the above
