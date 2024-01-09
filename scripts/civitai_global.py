def init():
    global download_queue, last_version, cancel_status, recent_model, json_data, json_info, main_folder, previous_inputs, download_fail, sortNewest, isDownloading, old_download, scan_files, ver_json, file_scan, url_list_with_numbers, print
    
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
    isDownloading = False
    old_download = False

_print = print
def print(print_message):
    _print(f'\033[96mCivitAI Browser+\033[0m: {print_message}')