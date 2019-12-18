class OpportunityException(Exception):
    def __init__(self, opportunity, message):
        self.opportunity = opportunity
        self.message = message
        super().__init__(message)


class OpportunityRemovedException(OpportunityException):
    pass
