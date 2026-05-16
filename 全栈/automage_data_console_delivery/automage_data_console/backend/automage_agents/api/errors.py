from __future__ import annotations

from automage_agents.core.exceptions import AutoMageAgentError


class ApiClientError(AutoMageAgentError):
    pass


class ApiTransportError(ApiClientError):
    pass


class ApiContractError(ApiClientError):
    pass


class ApiAuthError(ApiClientError):
    pass


class ApiPermissionError(ApiClientError):
    pass
