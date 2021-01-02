
from architectures.providers import _Azure


class _Iot(_Azure):
    _service_type = "iot"
    _icon_dir = "icons/azure/iot"


class DeviceProvisioningServices(_Iot):
    _icon = "device-provisioning-services.png"


class DigitalTwins(_Iot):
    _icon = "digital-twins.png"


class IotCentralApplications(_Iot):
    _icon = "iot-central-applications.png"


class IotHubSecurity(_Iot):
    _icon = "iot-hub-security.png"


class IotHub(_Iot):
    _icon = "iot-hub.png"


class Maps(_Iot):
    _icon = "maps.png"


class Sphere(_Iot):
    _icon = "sphere.png"


class TimeSeriesInsightsEnvironments(_Iot):
    _icon = "time-series-insights-environments.png"


class TimeSeriesInsightsEventsSources(_Iot):
    _icon = "time-series-insights-events-sources.png"


class Windows10IotCoreServices(_Iot):
    _icon = "windows-10-iot-core-services.png"


# Aliases
