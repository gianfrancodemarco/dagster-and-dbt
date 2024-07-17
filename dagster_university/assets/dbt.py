import os
from pathlib import Path

from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets

from ..resources import dbt_resource
from .constants import DBT_DIRECTORY

if os.getenv("DAGSTER_DBT_PARSE_PROJECT_ON_LOAD"):
    dbt_manifest_path = (
        dbt_resource.cli(["--quiet", "parse"]).wait()
        .target_path.joinpath("manifest.json")
    )
else:
    dbt_manifest_path = os.path.join(DBT_DIRECTORY, "target", "manifest.json")


class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]
        if resource_type == "source":
            return AssetKey(f"taxi_{name}")
        else:
            return super().get_asset_key(dbt_resource_props)


@dbt_assets(
    manifest=dbt_manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator()
)
def dbt_analytics(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
