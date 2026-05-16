class AutoMageAgentError(Exception):
    pass


class ConfigurationError(AutoMageAgentError):
    pass


class UserProfileError(AutoMageAgentError):
    pass


class ContractPendingError(AutoMageAgentError):
    pass
