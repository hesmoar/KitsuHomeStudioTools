import gazu
import pprint
from kitsu_home_pipeline.utils.auth import kitsu_auto_login

def find_asset_info():
    kitsu_auto_login()
    project_id = gazu.project.all_open_projects()[0]["id"]
    pprint.pprint(f"Project ID: {project_id}")
    asset_info = gazu.asset.all_assets_for_project(project_id)
    asset_entity_type = gazu.asset.
    print("These are the assets in the project:")
    pprint.pprint(asset_info)

find_asset_info()