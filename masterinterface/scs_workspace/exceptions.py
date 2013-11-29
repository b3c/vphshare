__author__ = 'm.balasso@scsitaly.com'

class WorkflowManagerException(Exception):
    def __init__(self, code, description):
        self.code = code or '500'
        self.description = description or 'Workflow Manager crashes or something else bad happens'
    def __str__(self):
        return "%s (%s)" % (self.description, self.code)
