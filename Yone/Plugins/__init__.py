# BSD 2-Clause License

# Copyright (c) 2022, Kushal
# All rights reserved.

from Yone import LOAD, LOGGER, NO_LOAD


def __list_all_modules():
    import glob
    from os.path import basename, dirname, isfile
    import os
    path =r'./Yone/Plugins/'
    list_of_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            list_of_files.append(os.path.join(root,file))
# This generates a list of modules in this folder for the * in __help__ to work.

    all_modules = [
        basename(name)[:-3]
        for name in list_of_files
        if isfile(name) and name.endswith(".py") and not name.endswith("__init__.py")
    ]

    if LOAD or NO_LOAD:
        to_load = LOAD
        if to_load:
            if not all(
                any(mod == module_name for module_name in all_modules)
                for mod in to_load
            ):
                LOGGER.error("Invalid loadorder names. Quitting.")
                quit(1)

            all_modules = sorted(set(all_modules) - set(to_load))
            to_load = list(all_modules) + to_load

        else:
            to_load = all_modules

        if NO_LOAD:
            LOGGER.info(f"Not loading: {NO_LOAD}")
            return [item for item in to_load if item not in NO_LOAD]

        return to_load

    return all_modules


ALL_MODULES = __list_all_modules()
LOGGER.info("Modules to load: %s", str(ALL_MODULES))
__all__ = ALL_MODULES + ["ALL_MODULES"]