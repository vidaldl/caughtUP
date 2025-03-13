def pre_find_module_path(hook_api):
    import sys
    import os
    sys.path.insert(0, os.path.dirname(hook_api.module_loader.path))