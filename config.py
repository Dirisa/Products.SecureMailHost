"""
$Id: config.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, ERROR, INFO, PROBLEM

from Products.Archetypes.public import DisplayList
from Products.PloneSoftwareCenter.utils import data_file_path

# Use ExternalStorage for PSCFile?
USE_EXTERNAL_STORAGE = True

# Change to point to where content should be stored, it can be an
# absolute or a relative path.
# A relative path is based on '$INSTANCE_HOME/var' directory (the
# Data.fs dir) or, if present, on ENVIRONMENT_VARIABLE defined by
# the ExternalStorage config (default: EXTERNAL_STORAGE_BASE_PATH)
EXTERNAL_STORAGE_PATH = 'files'

# security
security = ModuleSecurityInfo()
security.declarePublic('CATEGORY_LIST')

PROJECTNAME = 'PloneSoftwareCenter'
ADD_CONTENT_PERMISSION = 'Add PloneSoftwareCenter Content'
SKINS_DIR = 'skins'
HARD_DEPS = 'ArchAddOn',
SOFT_DEPS = 'ATReferenceBrowserWidget',
RELEASES_ID = 'releases'
IMPROVEMENTS_ID = 'roadmap'

GLOBALS = globals()


if USE_EXTERNAL_STORAGE:
    try:
        import Products.ExternalStorage
    except ImportError:
        LOG('PloneSoftwareCenter',
            PROBLEM, "ExternalStorage N/A, falling back to AttributeStorage")
        USE_EXTERNAL_STORAGE = False
