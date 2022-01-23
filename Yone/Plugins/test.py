import os
from os.path import basename, dirname, isfile
path =r'Yone/Plugins/'
list_of_files = []

for root, dirs, files in os.walk(path):
	for file in files:
		list_of_files.append(os.path.join(root,file))
for name in list_of_files:
    print(name)

    mod_paths = name
all_modules = [
        basename(name)[:-3]
        for name in list_of_files
        if isfile(name) and name.endswith(".py") and not name.endswith("__init__.py")
    ]

print(all_modules)
