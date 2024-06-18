from typing import Any, List


class ChannelMappingOptions:
    def __init__(
        self,
        *,
        mappings: List["ChannelMappings"],
        provider_channels: List["ListingProviderChannel"],
        provider_name: str,
        tuner_channels: List["TunerChannel"],
    ) -> None:
        self.mappings = mappings or []
        self.provider_channels = provider_channels or []
        self.provider_name = provider_name
        self.tuner_channels = tuner_channels or []


class ListingProvider:
    def __init__(
        self,
        *,
        id: str,
        path: str,
        type: str,
        channel_mappings: List["ChannelMappings"],
    ):
        self.id = id
        self.path = path
        self.type = type
        self.channel_mappings = channel_mappings or []

    def __str__(self) -> str:
        return f"ListingProvider[id={self.id},path={self.path},type={self.type}]"


class ListingProviderChannel:
    def __init__(self, id: str, name: str) -> None:
        self.name = name
        self.id = id
    
    @staticmethod
    def from_json(json: Any):
        channels = []
        for channel in json:
            m = ListingProviderChannel(
                id=channel["Id"],
                name=channel["Name"],
            )
            channels.append(m)
        return channels


class TunerChannel:
    def __init__(
        self,
        *,
        id: str,
        name: str,
        provider_channel_id: str,
        provider_channel_name: str,
    ) -> None:
        self.id = id
        self.name = name
        self.provider_channel_id = provider_channel_id
        self.provider_channel_name = provider_channel_name

    @staticmethod
    def from_json(json: Any):
        channels = []
        for channel in json:
            m = TunerChannel(
                id=channel["Id"],
                name=channel["Name"],
                provider_channel_id=channel.get("ProviderChannelId", None),
                provider_channel_name=channel.get("ProviderChannelName", None),
            )
            channels.append(m)
        return channels


class ChannelMappings:
    def __init__(self, *, name: str, value: str):
        self.name = name
        self.value = value

    @staticmethod
    def from_json(json: Any):
        mappings = []
        for mapping in json:
            m = ChannelMappings(name=mapping["Name"], value=mapping["Value"])
            mappings.append(m)
        return mappings

    def __str__(self) -> str:
        return f"ChannelMapping[name={self.name}, value={self.value}]"
