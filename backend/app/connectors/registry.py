from app.connectors.base import BaseConnector


class ConnectorRegistry:
    _registry: dict[str, type[BaseConnector]] = {}

    @classmethod
    def register(cls, source: str):
        def decorator(
            connector_cls: type[BaseConnector],
        ) -> type[BaseConnector]:
            cls._registry[source] = connector_cls
            return connector_cls

        return decorator

    @classmethod
    def get(cls, source: str) -> type[BaseConnector]:
        if source not in cls._registry:
            raise KeyError(f"Unknown connector: {source}")
        return cls._registry[source]

    @classmethod
    def list_sources(cls) -> list[str]:
        return list(cls._registry.keys())
