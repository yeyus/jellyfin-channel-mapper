from typing import Optional
import requests

from jellyfin.auth import JellyfinAPITokenAuth
from jellyfin.channel_mappings import (
    ChannelMappingOptions,
    ChannelMappings,
    ListingProvider,
    ListingProviderChannel,
    TunerChannel,
)


class JellyfinAPI:
    """Wrapper for the jellyfin server API"""

    def __init__(self, *, endpoint: str, api_token: str):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.auth = JellyfinAPITokenAuth(api_token)

    def get_channel_mapping_options(
        self, *, provider_id: str
    ) -> Optional[ChannelMappingOptions]:
        r = self.session.get(
            f"{self.endpoint}/LiveTv/ChannelMappingOptions?providerId={provider_id}"
        )

        payload = r.json()
        return ChannelMappingOptions(
            mappings=ChannelMappings.from_json(payload["Mappings"]),
            provider_channels=ListingProviderChannel.from_json(
                payload["ProviderChannels"]
            ),
            provider_name=payload["ProviderName"],
            tuner_channels=TunerChannel.from_json(payload["TunerChannels"]),
        )

    def get_livetv_listing_providers(self):
        r = self.session.get(f"{self.endpoint}/System/Configuration/livetv")
        payload = r.json()

        listing_providers = []
        if payload:
            for provider in payload["ListingProviders"]:
                lp = ListingProvider(
                    id=provider["Id"],
                    path=provider["Path"],
                    type=provider["Type"],
                    channel_mappings=ChannelMappings.from_json(
                        provider["ChannelMappings"]
                    ),
                )

                listing_providers.append(lp)

        return listing_providers

    def set_channel_mapping(
        self,
        *,
        provider_id: str,
        provider_channel_id: str,
        tuner_channel_id: str,
    ):
        json_payload = {
            "providerId": provider_id,
            "providerChannelId": provider_channel_id,
            "tunerChannelId": tuner_channel_id,
        }

        self.session.post(
            f"{self.endpoint}/LiveTv/ChannelMappings",
            json=json_payload,
        )