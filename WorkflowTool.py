
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowTool import WorkflowTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from config import CollectorWorkflow

class WorkflowTool(BaseTool):

    id = CollectorWorkflow
    meta_type = ToolNames.WorkflowTool
    security = ClassSecurityInfo()

    #XXX this should not make it into 1.0
    # Refactor me, my maker was tired
    def flattenTransitions(self, objs, container=None):
        """ this is really hokey - hold on!!"""
        if hasattr(objs, 'startswith'):
            return ()

        transitions=[]
        t_names=[]

        if container is None:
            container = self
        for o in [getattr(container, oid, None) for oid in objs]:
            trans=()
            try:
                trans=self.getTransitionsFor(o, container)
            except: #yikes
                pass
            if trans:
                for t in trans:
                    if t['name'] not in t_names:
                        transitions.append(t)
                        t_names.append(t['name'])

        return tuple(transitions[:])

    security.declarePublic('getTransitionsFor')
    def getTransitionsFor(self, obj=None, container=None, REQUEST=None):
        if type(obj) is type([]):
            return self.flattenTransitions(objs=obj, container=container)
        result = {}
        chain = self.getChainFor(obj)
        for wf_id in chain:
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                sdef = wf._getWorkflowStateOf(obj)
                if sdef is not None:
                    for tid in sdef.transitions:
                        tdef = wf.transitions.get(tid, None)
                        if tdef is not None and \
                           tdef.trigger_type == TRIGGER_USER_ACTION and \
                           tdef.actbox_name and \
                           wf._checkTransitionGuard(tdef, obj) and \
                           not result.has_key(tdef.id):
                            result[tdef.id] = {
                                    'id': tdef.id,
                                    'title': tdef.title,
                                    'title_or_id': tdef.title_or_id(),
                                    'name': tdef.actbox_name
                                    }
        return tuple(result.values())
WorkflowTool.__doc__ = BaseTool.__doc__

InitializeClass(WorkflowTool)
