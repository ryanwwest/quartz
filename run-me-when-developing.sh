# python script fetches markdown and images from obsidian vault, places in content/
# hugo-obsidian creates tags and taxonomies and links in json for quartz to use
# hugo builds static html site in public/ using both of the above
watch -n 5 bash -c 'python3 obsidian-to-quartz.py ~/g/zk/media/ ~/g/zk/blog/ ~/g/quartz/content/media/ ~/g/quartz/content/ && hugo-obsidian -input=content -output=assets/indices -index=true -root=. && hugo'
