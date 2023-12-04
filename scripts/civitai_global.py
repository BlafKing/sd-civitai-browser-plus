from modules.shared import cmd_opts
import json

try:
    with open(cmd_opts.ui_config_file, 'r') as f:
        config = json.load(f)
    tile_count_value = config["civitai_interface/Tile count:/value"]
except:
    tile_count_value = 15

def init():
    global download_queue, last_version, cancel_status, recent_model, json_data, json_info, main_folder, previous_inputs, download_fail, sortNewest, inputs_changed, isDownloading, tile_count, old_download, scan_files, ver_json, file_scan, url_list_with_numbers, print
    print = ('\033[96mCivitAI Browser+\033[0m:')
    
    cancel_status = None
    recent_model = None
    json_data = None
    json_info = None
    main_folder = None
    previous_inputs = None
    last_version = None
    ver_json = None
    url_list_with_numbers = None
    download_queue = []
    
    file_scan = False
    scan_files = False
    download_fail = False
    sortNewest = False
    inputs_changed = False
    isDownloading = False
    old_download = False
    tile_count = tile_count_value