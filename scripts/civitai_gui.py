import gradio as gr
from modules import script_callbacks, shared
import os
import fnmatch
import re
import scripts.civitai_global as gl
import scripts.civitai_download as _download
import scripts.civitai_file_manage as _file
import scripts.civitai_api as _api

gl.init()

def insert_sub(model_name, version_name, content_type):
    sub_folders = ["None"]
    try:
        version = version_name.replace(" [Installed]", "")
    except:
        pass
    
    if model_name is not None and content_type is not None:
        model_folder = os.path.join(_api.contenttype_folder(content_type))
        for root, dirs, _ in os.walk(model_folder):
            for d in dirs:
                sub_folder = os.path.relpath(os.path.join(root, d), model_folder)
                if sub_folder:
                    sub_folders.append(f'\\{sub_folder}')
    
    sub_folders.remove("None")
    sub_folders = sorted(sub_folders)
    sub_folders.insert(0, "None")
    sub_folders.insert(1, (f'\\{model_name}'))
    sub_folders.insert(2, (f'\\{model_name}\\{version}'))
    
    list = set()
    sub_folders = [x for x in sub_folders if not (x in list or list.add(x))]
    
    return gr.Dropdown.update(choices=sub_folders)

def on_ui_tabs():    
    base_path = "extensions"
    lobe_directory = None

    for root, dirs, files in os.walk(base_path):
        for dir_name in fnmatch.filter(dirs, '*lobe*'):
            lobe_directory = os.path.join(root, dir_name)
            break
        if lobe_directory:
            break

    component_id = "lobe_toggles" if lobe_directory else "toggles"
    toggle1 = None if lobe_directory else "toggle1"
    toggle2 = None if lobe_directory else "toggle2"
    toggle3 = None if lobe_directory else "toggle3"
    
    with gr.Blocks() as civitai_interface:
        with gr.Tab("Browser"):
            with gr.Row():
                with gr.Column(scale=2, min_width=200):
                    content_type = gr.Dropdown(label='Content Type:', choices=["Checkpoint","TextualInversion","LORA","LoCon","Poses","Controlnet","Hypernetwork","AestheticGradient", "VAE"], value="Checkpoint", type="value")
                with gr.Column(scale=2, min_width=200):
                    period_type = gr.Dropdown(label='Time Period:', choices=["All Time", "Year", "Month", "Week", "Day"], value="All Time", type="value")
                with gr.Column(scale=2, min_width=200):
                    sort_type = gr.Dropdown(label='Sort By:', choices=["Newest","Most Downloaded","Highest Rated","Most Liked"], value="Most Downloaded", type="value")
                with gr.Column(scale=2, min_width=200):
                    base_filter = gr.Dropdown(label='Filter Base Model:', multiselect=True, choices=["SD 1.4","SD 1.5","SD 2.0","SD 2.1", "SDXL 0.9", "SDXL 1.0", "Other"], value=None, type="value")
                with gr.Column(scale=1, min_width=200, elem_id=component_id):
                    create_json = gr.Checkbox(label=f"Save tags after download", value=False, elem_id=toggle1)
                    toggle_date = gr.Checkbox(label="Divide cards by date", value=False, elem_id=toggle2)
                    show_nsfw = gr.Checkbox(label="NSFW content", value=False, elem_id=toggle3)
            with gr.Row():
                with gr.Column(scale=3,min_width=300):
                    search_term = gr.Textbox(label="Search Term:", interactive=True, lines=1)
                with gr.Column(scale=2,min_width=120):
                    use_search_term = gr.Radio(label="Search:", choices=["Model name", "User name", "Tag"],value="Model name")
                with gr.Column(scale=1,min_width=160 ):
                    size_slider = gr.Slider(minimum=4, maximum=20, value=8, step=0.25, label='Tile size:')
                with gr.Column(scale=1,min_width=160 ):
                    tile_slider = gr.Slider(label="Tile count:", min=5, max=50, value=15, step=1, max_width=100)
            with gr.Row():
                with gr.Column(scale=5):
                    refresh = gr.Button(label="Refresh", value="Refresh")
                with gr.Column(scale=3,min_width=80):
                    get_prev_page = gr.Button(value="Prev Page", interactive=False)
                with gr.Column(scale=3,min_width=80):
                    get_next_page = gr.Button(value="Next Page", interactive=False)
                with gr.Column(scale=1,min_width=50):
                    pages = gr.Textbox(label='Pages', show_label=False)
            with gr.Row():
                list_html = gr.HTML(value='<div style="font-size: 24px; text-align: center; margin: 50px !important;">Please press \'Refresh\' to load selected content!</div>')
            with gr.Row():
                download_progress = gr.HTML(value='<div style="min-height: 0px;"></div>', elem_id="DownloadProgress")
            with gr.Row():
                list_models = gr.Dropdown(label="Model:", choices=[], interactive=False, elem_id="quicksettings1", value=None)
                list_versions = gr.Dropdown(label="Version:", choices=[], interactive=False, elem_id="quicksettings", value=None)
                file_list = gr.Dropdown(label="File:", choices=[], interactive=False, elem_id="file_list", value=None)
            with gr.Row():
                with gr.Column(scale=4):
                    install_path = gr.Textbox(label="Download Folder:", visible=True, interactive=False, max_lines=1)
                with gr.Column(scale=2):
                    sub_folder = gr.Dropdown(label="Sub Folder:", choices=[], interactive=False, value=None)
            with gr.Row():
                with gr.Column(scale=13):
                    trained_tags = gr.Textbox(label='Trained Tags (if any):', value=None, interactive=False, lines=1)
                with gr.Column(scale=1, min_width=120):
                    base_model = gr.Textbox(label='Base Model:', value='', interactive=False, lines=1)
                with gr.Column(scale=5):
                    model_filename = gr.Textbox(label="Model Filename:", interactive=False, value=None)
            with gr.Row():
                save_tags = gr.Button(value="Save Tags", interactive=False)
                save_images = gr.Button(value="Save Images", interactive=False)
                download_model = gr.Button(value="Download Model", interactive=False)
                cancel_model = gr.Button(value="Cancel Download", interactive=False, visible=False)
                delete_model = gr.Button(value="Delete Model", interactive=False, visible=False)
            with gr.Row():
                preview_html = gr.HTML()
            with gr.Row():
                #Invisible triggers/variables
                model_id = gr.Textbox(label='Model ID:', value=None, visible=False)
                dl_url = gr.Textbox(label='DL URL:', value=None, visible=False)
                event_text = gr.Textbox(elem_id="eventtext1", visible=False)
                download_start = gr.Textbox(value=None, visible=False)
                download_finish = gr.Textbox(value=None, visible=False)
                tag_start = gr.Textbox(value=None, visible=False)
                tag_finish = gr.Textbox(value=None, visible=False)
                delete_finish = gr.Textbox(value=None, visible=False)
                current_model = gr.Textbox(value=None, visible=False)
        with gr.Tab("Update All Tags"):
            with gr.Row():
                selected_tags = gr.CheckboxGroup(elem_id="selected_tags", label="Update tags for:", choices=["Checkpoint", "Hypernetwork", "TextualInversion", "AestheticGradient", "LORA", "LoCon", "VAE", "Controlnet", "Poses"])
            with gr.Row():
                save_tags = gr.Button(value="Update Selected Tags", interactive=True, visible=True)
                cancel_tags = gr.Button(value="Cancel Updating Tags", interactive=False, visible=False)
            with gr.Row():
                tag_progress = gr.HTML(value='<div style="min-height: 0px;"></div>', elem_id="DownloadProgress")
        def changeInput():
            gl.contentChange = True
            
        def ToggleDate(toggle_date):
            gl.sortNewest = toggle_date
            
        def select_subfolder(sub_folder):
            if sub_folder == "None":
                newpath = gl.main_folder
            else:
                newpath = gl.main_folder + sub_folder
            return gr.Textbox.update(value=newpath)
        
        toggle_date.input(
            fn=ToggleDate,
            inputs=[toggle_date]
        )
        
        def update_tile_count(slider_value):
            gl.tile_count = slider_value
        
        tile_slider.release(
            fn=update_tile_count,
            inputs=[tile_slider],
            outputs=[]
        )
        
        content_type.input(
            fn=changeInput,
            inputs=[]
        )
        
        sub_folder.select(
            fn=select_subfolder,
            inputs=[sub_folder],
            outputs=[install_path]
        )
                
        save_tags.click(
            fn=_file.save_tag_start,
            inputs=[tag_start],
            outputs=[
                tag_start,
                save_tags,
                cancel_tags,
                tag_progress
            ]
        )
        
        tag_start.change(
            fn=_file.save_all_tags,
            inputs=[selected_tags, tag_finish],
            outputs=[
                tag_progress,
                tag_finish,
            ]
        )
        
        tag_finish.change(
            fn=_file.save_tag_finish,
            outputs=[
                save_tags,
                cancel_tags
            ]
        )
        
        cancel_tags.click(
            fn=_file.cancel_tag
        )
        
        download_finish.change(
            fn=None,
            inputs=[current_model],
            _js="(modelName) => updateCard(modelName)"
        )
        
        delete_finish.change(
            fn=None,
            inputs=[current_model],
            _js="(modelName) => updateCard(modelName)"
        )

        list_html.change(
            fn=None,
            inputs=[show_nsfw],
            _js="(hideAndBlur) => toggleNSFWContent(hideAndBlur)"
        )
        
        show_nsfw.change(
            fn=None,
            inputs=[show_nsfw],
            _js="(hideAndBlur) => toggleNSFWContent(hideAndBlur)"
        )

        list_html.change(
            fn=None,
            inputs=[base_filter],
            _js="(baseModelValue) => filterByBaseModel(baseModelValue)"
        )
        
        base_filter.change(
            fn=None,
            inputs=[base_filter],
            _js="(baseModelValue) => filterByBaseModel(baseModelValue)"
        )
        
        list_html.change(
            fn=None,
            inputs=[size_slider],
            _js="(size) => updateCardSize(size, size * 1.5)"
        )

        size_slider.change(
            fn=None,
            inputs=[size_slider],
            _js="(size) => updateCardSize(size, size * 1.5)"
        )
        
        model_filename.change(
            fn=insert_sub,
            inputs=[
                list_models,
                list_versions,
                content_type
                ],
            outputs=[sub_folder]
        )
        
        download_model.click(
            fn=_download.download_start,
            inputs=[
                download_start,
                list_models,
                model_filename,
                list_versions
                ],
            outputs=[
                download_model,
                cancel_model,
                download_start,
                download_progress
            ]
        )
        
        download_start.change(
            fn=_download.download_create_thread,
            inputs=[
                download_finish,
                dl_url,
                model_filename,
                preview_html,
                create_json,
                trained_tags,
                install_path,
                list_models,
                content_type,
                list_versions
                ],
            outputs=[
                download_progress,
                current_model,
                download_finish
            ]
        )
        
        cancel_model.click(
            fn=_download.download_cancel,
            inputs=[
                delete_finish,
                content_type,
                list_models,
                list_versions,
                model_filename
                ],
            outputs=[
                download_model,
                cancel_model,
                download_progress
            ]
        )
        
        download_finish.change(
            fn=_download.download_finish,
            inputs=[
                model_filename,
                list_versions,
                list_models,
                content_type
                ],
            outputs=[
                download_model,
                cancel_model,
                delete_model,
                download_progress,
                list_versions
            ]
        )
        
        delete_model.click(
            fn=_file.delete_model,
            inputs=[
                delete_finish,
                content_type,
                model_filename,
                list_models,
                list_versions
                ],
            outputs=[
                download_model,
                cancel_model,
                delete_model,
                delete_finish,
                current_model,
                list_versions
            ]
        )
        
        save_tags.click(
            fn=_file.save_json,
            inputs=[
                model_filename,
                install_path,
                trained_tags
                ],
            outputs=[trained_tags]
        )
        
        save_images.click(
            fn=_file.save_images,
            inputs=[
                preview_html,
                model_filename,
                content_type,
                install_path
                ],
            outputs=[]
        )
        
        list_models.select(
            fn=_api.update_model_versions,
            inputs=[
                list_models,
                content_type
            ],
            outputs=[
                list_versions,
                install_path,
                sub_folder
            ]
        )
        
        list_versions.change(
            fn=_api.update_model_info,
            inputs=[
                list_models,
                list_versions
                ],
            outputs=[
                preview_html,
                trained_tags,
                base_model,
                download_model,
                delete_model,
                file_list
            ]
        )
        
        list_versions.input(
            fn=_api.update_file_info,
            inputs=[
                list_models,
                list_versions,
                file_list
            ],
            outputs=[
                model_filename,
                model_id
            ]
        )
        
        file_list.change(
            fn=_api.update_file_info,
            inputs=[
                list_models,
                list_versions,
                file_list
            ],
            outputs=[
                model_filename,
                model_id
            ]
        )
        
        model_id.change(
            fn=_api.update_dl_url,
            inputs=[
                trained_tags,
                list_models,
                list_versions,
                model_id
                ],
            outputs=[
                dl_url,
                save_tags,
                save_images,
                download_model
                ]
        )
        
        get_next_page.click(
            fn=_api.update_next_page,
            inputs=[
                show_nsfw,
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                pages
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_tags,
                save_images,
                download_model,
                install_path,
                sub_folder
            ]
        )
        
        refresh.click(
            fn=_api.update_model_list,
            inputs=[
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                show_nsfw,
                pages
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_tags,
                save_images,
                download_model,
                install_path,
                sub_folder,
                file_list
            ],
        )
        
        get_prev_page.click(
            fn=_api.update_prev_page,
            inputs=[
                show_nsfw,
                content_type,
                sort_type,
                period_type,
                use_search_term,
                search_term,
                pages
                ],
            outputs=[
                list_models,
                list_versions,
                list_html,
                get_prev_page,
                get_next_page,
                pages,
                save_tags,
                save_images,
                download_model
            ]
        )
        
        
        def update_models_dropdown(model_name, content_type):
            model_name = re.sub(r'\.\d{3}$', '', model_name)
            (ret_versions, install_path, sub_folder) = _api.update_model_versions(model_name, content_type)
            (html, tags, _, DwnButton, _, filelist) = _api.update_model_info(model_name,ret_versions['value'])
            (filename, id) = _api.update_file_info(model_name, ret_versions['value'], filelist['value'])
            (dl_url, _, _, _) = _api.update_dl_url(tags, model_name, ret_versions['value'], id['value'])
            return  gr.Dropdown.update(value=model_name),ret_versions ,html,dl_url['value'],tags,filename,install_path['value'],sub_folder, DwnButton, filelist, id
        
        event_text.change(
            fn=update_models_dropdown,
            inputs=[
                event_text,
                content_type,
                ],
            outputs=[
                list_models,
                list_versions,
                preview_html,
                dl_url,
                trained_tags,
                model_filename,
                install_path,
                sub_folder,
                download_model,
                file_list,
                model_id
            ]
        )

    return (civitai_interface, "Civit AI", "civitai_interface"),

def on_ui_settings():
    section = ("civitai_browser_plus", "Civit AI")

    if not (hasattr(shared.OptionInfo, "info") and callable(getattr(shared.OptionInfo, "info"))):
        def info(self, info):
            self.label += f" ({info})"
            return self
        shared.OptionInfo.info = info
    
    shared.opts.add_option("use_aria2", shared.OptionInfo(True, "Download models using Aria2", section=section).info("Disable to use the old download method"))
    shared.opts.add_option("disable_dns", shared.OptionInfo(False, "Disable Async DNS for Aria2", section=section).info("Useful for users who use PortMaster or other software that controls the DNS"))
    shared.opts.add_option("show_log", shared.OptionInfo(False, "Show Aria2 Logs in CMD", section=section).info("Requires Web-UI Restart"))
    shared.opts.add_option("split_aria2", shared.OptionInfo(64, "Number of connections to use for downloading a model", gr.Slider, lambda: {"maximum": "64", "minimum": "1", "step": "1"}, section=section).info("Only applies to Aria2"))
    
script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_ui_settings(on_ui_settings)