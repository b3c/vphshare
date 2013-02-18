__author__ = "Matteo Balasso (m.balasso@scsitaly.com)"


from workflows.models import Workflow
SuscriptionRequestWorkflow = Workflow.objects.create(name="SuscriptionRequestWorkflow")
