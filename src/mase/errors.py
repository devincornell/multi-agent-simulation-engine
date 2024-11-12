
class AgentExistsError(Exception):
    pass

class AgentDoesNotExistError(Exception):
    pass

class OutOfBoundsError(Exception):
    pass

class MovementRuleViolationError(Exception):
    pass

class AgentHasNoMapError(Exception):
    pass

class MapIsNotAttachedError(Exception):
    pass

class AgentNotAllowedError(Exception):
    pass

class AgentIsNotHashableError(Exception):
    pass
