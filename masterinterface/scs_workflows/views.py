from core import wfmng
from exceptions import WorkflowManagerException
from models import WorkflowExecution
from masterinterface.scs_resources.models import Workflow

def getWorkflowList(ticket):
    try:
        wfs = []
        # list in local db might be out of date
        wfs_at_wfmng = wfmng.getWorkflowsList({}, ticket)

        for wf_at_wfmng in wfs_at_wfmng:
            wf, created = WorkflowExecution.objects.get_or_create(workflowId=wf_at_wfmng['workflowId'])
            wf.update(info=wf_at_wfmng)
            wf.save()

            wfs.append(wf)

    except WorkflowManagerException, e:
        return []