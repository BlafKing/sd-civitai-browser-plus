import requests
import json
import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks

# Set the URL for the API endpoint
api_url = "https://civitai.com/api/v1/models?limit=50"
json_data = None

def api_to_data(sort_type):
    json_data = request_civit_api(f"{api_url}&types=Checkpoint&sort={sort_type}")
    return json_data


def update_model_list(sort_type):
    global json_data
    json_data = api_to_data(sort_type)
    model_dict = {}
    
    count = 0
    for item in json_data['items']:
        model_dict[item['name']] = item['name']
        
    
    return gr.Dropdown.update(choices=[v for k, v in model_dict.items()], value=None)

def update_model_versions(model_name=None):
    if model_name:
        global json_data
        versions_dict = {}
        for item in json_data['items']:
            if item['name'] == model_name:

                for model in item['modelVersions']:
                    versions_dict[model['name']] = item['name']
        return gr.Dropdown.update(choices=[k for k, v in versions_dict.items()], value=None)
    else:
        return gr.Dropdown.update(choices=[], value=None)

def update_model_info(model_name=None, model_version=None):
    if model_name and model_version:
        global json_data
        output_html = ""
        output_training = ""
        img_html = ""
        for item in json_data['items']:
            if item['name'] == model_name:
                for model in item['modelVersions']:
                    if model['name'] == model_version:
                        if model['trainedWords']:
                            output_training = " # ".join(model['trainedWords'])
                        model_url = model['downloadUrl']
                        for pic in model['images']:
                            img_html = f"{img_html}<img src={pic['url']} width=400px></img>"
                        output_html = f"<B>Model:</b> {model_name}<br><b>Version:</b> {model_version}<br><b>Download:</b> <a href={model_url}>Here</a><br><br><div align=center>{img_html}"



        return gr.HTML.update(value=output_html), gr.Textbox.update(value=output_training)
    else:
        return gr.HTML.update(value=None), gr.Textbox.update(value=None)


def request_civit_api(api_url=None):
    # Make a GET request to the API
    response = requests.get(api_url)

    # Check the status code of the response
    if response.status_code != 200:
      print("Request failed with status code: {}".format(response.status_code))
      exit()

    # New code test
    data = json.loads(response.text)


    current_page = data['metadata']['currentPage']
    total_pages = data['metadata']['totalPages']
    if data['metadata']['nextPage']:
        next_page = data['metadata']['nextPage']
    for item in data['items']:
        print('#################################################################################')
        print(f"Model Name: {item['name']}")
        print('#################################################################################')
        print()
        for model in item['modelVersions']:

        # Print the name, trainedWords, and downloadUrl for each item
            print(f"Version: {model['name']}")
            if model['trainedWords']:
                print(f"Trained words: {model['trainedWords']}")
            print(f"Download URL: {model['downloadUrl']}")
            print(f"Preview Images:")
            for pic in model['images']:
                print(pic['url'])
            print()
    print('--------------------------------------------------------------------------------')
    print(f"Page: {current_page}/{total_pages}")
    if next_page:
        print(f"Next: {next_page}")
    return data

def get_versions_of_model(model_name, json_data):
    versions_dict = {}
    for item in json_data['items']:
        if item['name'] == model_name:

            for model in item['modelVersions']:
                versions_dict[model['name']] = item['name']
                # Print the name, trainedWords, and downloadUrl for each item
                print(f"Version: {model['name']}")
                if model['trainedWords']:
                    print(f"Trained words: {model['trainedWords']}")
                print(f"Download URL: {model['downloadUrl']}")
                print(f"Preview Images:")
                for pic in model['images']:
                    print(pic['url'])
                print()


def choose_model_from_api(model_name, model_version, json_data):
    for item in json_data['items']:
        if item['name'] == model_name:

            for model in item['modelVersions']:

                # Print the name, trainedWords, and downloadUrl for each item
                print(f"Version: {model['name']}")
                if model['trainedWords']:
                    print(f"Trained words: {model['trainedWords']}")
                print(f"Download URL: {model['downloadUrl']}")
                print(f"Preview Images:")
                for pic in model['images']:
                    print(pic['url'])
                print()

#json_data = request_civit_api(api_url)

def on_ui_tabs():
    with gr.Blocks() as civitai_interface:
        with gr.Row():
            sort_type = gr.Radio(label='Site to search', choices=["Newest","Most Downloaded"], value="Newest", type="value")
            get_list_from_api = gr.Button(label="Get List", value="Get List")
        with gr.Row():
            list_models = gr.Dropdown(label="Model", choices=[], interactive=True, elem_id="quicksettings", value=None)
            #refresh_checkpoint = gr.Button(value=refresh_symbol, elem_id="refresh_sd_model_checkpoint")
            #list_models = gr.Dropdown(label="List Models", elem_id="list_models_id", choices=[v for k, v in model_dict_list.items()], value=next(iter(model_dict_list.keys())), interactive=True)
        
            list_versions = gr.Dropdown(label="Version", choices=[], interactive=True, elem_id="quicksettings", value=None)
        with gr.Row():
            txt_list = ""
            dummy = gr.Textbox(label='Trained Tags (if any)', value=f'{txt_list}', interactive=False, lines=1)
        with gr.Row():
            preview_image_html = gr.HTML()
        get_list_from_api.click(
            fn=update_model_list,
            inputs=[
            sort_type,
            ],
            outputs=[
            list_models,
            ]


        )
        list_models.change(
            fn=update_model_versions,
            inputs=[
            list_models,
            ],
            outputs=[
            list_versions,
            ]
        )
        list_versions.change(
            fn=update_model_info,
            inputs=[
            list_models,
            list_versions,
            ],
            outputs=[
            preview_image_html,
            dummy,
            ]
        )

#        refresh_checkpoint.click(
#            fn=refresh_models,
#            inputs=[],
#            outputs=[
#            list_models,
#            ]
#        )
        

    return (civitai_interface, "CivitAi", "civitai_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)