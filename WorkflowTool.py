
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowTool import WorkflowTool as BaseTool
from Products.CMFPlone import ToolNames

from config import CollectorWorkflow

class WorkflowTool(BaseTool):

    id = CollectorWorkflow
    meta_type = ToolNames.WorkflowTool

WorkflowTool.__doc__ = BaseTool.__doc__

InitializeClass(WorkflowTool)
