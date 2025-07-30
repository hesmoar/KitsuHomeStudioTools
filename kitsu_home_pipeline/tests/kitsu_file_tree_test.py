from kitsu_home_pipeline.utils.auth import kitsu_auto_login
from kitsu_home_pipeline.utils.kitsu_utils import get_file_tree

kitsu_auto_login()
get_file_tree("AnimaOrquesta_Test")