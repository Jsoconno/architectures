
from architectures.providers import _Azure


class _Devops(_Azure):
    _service_type = "devops"
    _icon_dir = "icons/azure/devops"


class ApplicationInsights(_Devops):
    _icon = "application-insights.png"


class Artifacts(_Devops):
    _icon = "artifacts.png"


class Boards(_Devops):
    _icon = "boards.png"


class Devops(_Devops):
    _icon = "devops.png"


class DevtestLabs(_Devops):
    _icon = "devtest-labs.png"


class Pipelines(_Devops):
    _icon = "pipelines.png"


class Repos(_Devops):
    _icon = "repos.png"


class TestPlans(_Devops):
    _icon = "test-plans.png"


# Aliases
