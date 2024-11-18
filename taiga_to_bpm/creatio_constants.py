# Standard Library
from enum import Enum

HEADERS_V3_TEMPLATE = {
    "Content-Type": "application/json;odata=verbose",
    "ForceUseSession": "true",
    "Accept": "application/json;odata=verbose",
    "BPMCSRF": "",
}

HEADERS_V4_TEMPLATE = {
    "Content-Type": "application/json; charset=utf-8",
    "ForceUseSession": "true",
    "Accept": "application/json; charset=utf-8",
    "BPMCSRF": "",
}


class ODATA_version(Enum):
    """
    Enumerator for different ODATA protocol versions
    """

    v3 = {
        "service_path": "/0/ServiceModel/EntityDataService.svc",
        "headers": HEADERS_V3_TEMPLATE,
    }
    v4 = {
        "service_path": "/0/odata",
        "headers": HEADERS_V4_TEMPLATE,
    }
    v4core = {
        "service_path": "/odata",
        "headers": HEADERS_V4_TEMPLATE,
    }
    test = {
        "service_path": "/0/ServiceModel/EntityDataService.svc",
        "headers": "test",
    }
