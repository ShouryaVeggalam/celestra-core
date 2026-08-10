"""
SDK module — first-party client surfaces for Celestra applications.

- `CelestraClient`: remote HTTP access to a Core deployment
- `CelestraSDK`: in-process access to wired platform services
"""

from sdk.client import CelestraAPIError, CelestraClient
from sdk.local import CelestraSDK

__all__ = [
    "CelestraAPIError",
    "CelestraClient",
    "CelestraSDK",
]
