from typing import (
    Any,
    Dict,
    List,
    Optional,
)
from warnings import warn

from easypost.easypost_object import convert_to_easypost_object
from easypost.requestor import (
    RequestMethod,
    Requestor,
)
from easypost.services.base_service import BaseService


class BetaCarrierMetadataService(BaseService):
    def __init__(self, client):
        self._client = client

    def retrieve_carrier_metadata(
        self,
        carriers: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get metadata for all carriers on the EasyPost platform."""
        warn(
            'This method is deprecated, use the "retrieve" function of "carrier_metadata" on the client instead.',
            DeprecationWarning,
            stacklevel=2,
        )

        params = {
            "carriers": ",".join(carriers) if carriers else None,
            "types": ",".join(types) if types else None,
        }

        response = Requestor(self._client).request(
            method=RequestMethod.GET,
            url="/metadata",
            params=params,
            beta=True,
        )

        return convert_to_easypost_object(response=response.get("carriers", []))