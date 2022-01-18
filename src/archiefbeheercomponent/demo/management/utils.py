from zgw_consumers.client import ZGWClient


def get_or_create_catalogus(catalogus_data: dict, client: ZGWClient) -> dict:
    catalogus_list = client.list(
        resource="catalogus",
        query_params={
            "domein": catalogus_data["domein"],
            "rsin": catalogus_data["rsin"],
        },
    )

    if len(catalogus_list["results"]) == 0:
        return client.create(resource="catalogus", data=catalogus_data)

    return catalogus_list["results"][0]


def uuid_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1]
