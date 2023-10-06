from modules.shared import cmd_opts
import json
try:
    with open(cmd_opts.ui_config_file, 'r') as f:
        config = json.load(f)
    tile_count_value = config["civitai_interface/Tile count:/value"]
except:
    tile_count_value = 15

def init():
    global last_version, current_download, cancel_status, recent_model, json_data, json_info, main_folder, previous_search_term, previous_tile_count, previous_inputs, download_fail, sortNewest, contentChange, inputs_changed, isDownloading, pageChange, tile_count, old_download, scan_files, ver_json, file_scan, url_list_with_numbers
    cancel_status = None
    recent_model = None
    json_data = None
    json_info = None
    main_folder = None
    previous_search_term = None
    previous_tile_count = None
    previous_inputs = None
    last_version = None
    current_download = None
    ver_json = None
    url_list_with_numbers = None
    
    file_scan = False
    scan_files = False
    download_fail = False
    sortNewest = False
    contentChange = False
    inputs_changed = False
    isDownloading = False
    pageChange = False
    old_download = False
    tile_count = tile_count_value