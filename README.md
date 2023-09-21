# CivitAI Browser+
Extension for [Automatic1111's Stable Difussion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)  

This extension allows you to download models from CivitAi without leaving WebUI!  

This modified extension is based on [v1.1.0](https://github.com/SignalFlagZ/sd-civitai-browser/releases/tag/1.1.0) from [SignalFlagZ's Fork](https://github.com/SignalFlagZ/sd-civitai-browser)  


**NOTE: Search results are currently not impacted by the selected Base Model since the CivitAI API does not yet support this feature. If you'd like to have this feature, please upvote my feature request [here](https://civitai.featurebase.app/submissions/64ea19ac4f9cf39e6f9fb2e9) and [here](https://github.com/orgs/civitai/discussions/733)**

<h1>Features 🚀</h1>
<h3>Browse all models from CivitAI 🧩</h2>

* Explore a wide range of models at your fingertips.

<h3>Check for updates and installed models 🔄</h3>

* Easily spot new updates and identify already installed models while browsing.
* Ability to scan all installed models for available updates.

<h3>Download any Model, any version, and any file 📥</h3>

* Get the specific model version and file you need hassle-free.

<h3>Automatically assign tags to installed models 🏷️</h3>

* Assign tags by scanning all installed models for automatic use in image generation.

<h3>High-speed downloads with Aria2 🚄</h3>

* Maximize your bandwidth for lightning-fast downloads.

<h3>Actively maintained with feature requests welcome 🛠️</h3>

* Feel free to send me your feature requests, and I'll do my best to implement them!

<h1></h1>

<details>
<summary><h1>Known Issues 🐛</h1></summary>

<details>
<summary><h3>Unable to download / Frozen download</h3></summary>

**If you're experiencing issues with broken or frozen downloads, there are two possible solutions you can try:**

1. **Disable Async DNS for Aria2**:
   If you're using any DNS manager program like PortMaster, try turning on the "Disable Async DNS for Aria2" option.

   ![Disable Async DNS for Aria2](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/3cf7fab3-0df5-4995-9543-d9824b7931ff)

2. **Revert to the old download method**:
   Another solution could be to disable the "Download models using Aria2" feature.  
This will switch back to the old download method, which may resolve the issue.

   ![Revert to old download method](https://github.com/BlafKing/sd-civitai-browser-plus/assets/9644716/982b0ebb-0cac-4053-8060-285533e0e176)

These settings can be found under the "Settings" tab in Web-UI and then under the "Civit AI" tile.

</details>

</details>

<h1></h1>

# Preview 👀

https://github.com/BlafKing/sd-civitai-browser/assets/9644716/ea873c3e-a7e4-44a8-907a-e9bddf13bc55


(Theme used: [Lobe](https://github.com/canisminor1990/sd-webui-lobe-theme))  

# Changelog 📋

<h3>v1.12.1</h3>

* File deletion now uses both SHA256 and file name to detect correct file.
* Fixed a bug where the default file was incorrect when selecting a model.
* Fixed a bug where Next Page caused an error when changing content type.
* Added settings option to toggle automatically inserting 2 default sub folders.

---
<h3>v1.12</h3>

* Added ability to load all selected installed models into browser in Update Models tab.
* Installed/outdated models check is now also done using SHA256 instead of only file name.
* Added ability to select multiple content Types when searching and scanning.
* Greatly improved speed of model installed/update scanning if model ID is in associated .json

---
<h3>v1.11.2</h3>

* Redesign of model page by [ManOrMonster](https://github.com/ManOrMonster)
* <details><summary>Model page changes (https://github.com/BlafKing/sd-civitai-browser-plus/pull/33)</summary>
   
   - Redesigned the look of the model page.
   - Added link to model page on CivitAI. Click on model name to open.
   - Added link to uploader/creator page on CivitAI. Click creator name to open.
   - Added CivitAI avatar display.
   - Separate description section.
   - First sample image is marked with data attribute and downloaded as preview image instead of grabbing first in model HTML. This guarantees that the first sample image (not avatar or image in description) is used when downloading the model.
   - Sample images are marked with data attribute so that only they are downloaded when using "Save Images" (no description images or avatar).
   - Removed trained tags from info since they are displayed above.
   - Each sample image has its own section.
   - Sample images zoom in when clicked, zoom out when clicking anywhere.
   - Forced width is removed from sample image URLs so that nice big images can be viewed.
   - Metadata is arranged so that the most commonly used data is at the top, no more searching for prompts.
   - Extra metadata is in accordion labeled "More details...". This is especially useful to hide insanely large ComfyUI JSON.

</details>

---
<h3>v1.11.1</h3>

* Added error detection during Aria2 downloads.
* Avoid starting Aria2 RPC multiple times with better port check.
* Bug fix for dynamic tile status updates after deleting/downloading.
---

<h3>v1.11</h3>

* Added new feature which can scan all installed models for available updates.
* Fixed a bug which occurs if the Base Model isn't found.
* Model ID and sha256 now gets saved to matching .json after scanning or downloading a model
* Update Model functions now use Model IDs or sha256 from .json if available for faster scanning.
---

<h3>v1.10.1</h3>

* Fixed pathing for Unix systems
* Added extra check to make sure only the selected model gets deleted when pressing delete.
* Models get moved to trash instead of fully deleted.
* Added extra Aria2 RPC startup check for Windows Linux sub-systems
---
<h3>v1.10</h3>

* Added new feature which can update Tags for all installed models!
* Added tabs for Browsing and updating Tags.
* Added Buttons to select which folders to update tags in.
---
<h3>v1.9.4</h3>

* Added Civit AI settings tab
  - Option to disable downloading with Aria2. (will use old download method instead)
  - Option to disable using Async DNS. (can fix issues for some users who use DNS managing programs)
  - Option to show Aria2 logs in the CMD.
  - Option to set the amount of connections when downloading a model with Aria2.  
    (The optimal connection count is different per user, try to find the lowest option which still gives you full bandwidth speed)
---
<h3>v1.9.3</h3>

* Included Motrix Aria2 version.
* Max connections per server set to 64 and split file set 64.
* Aria2 is now shipped with this extension for Linux as well. (no need to manually install anymore!)
---

<h3>v1.9.2</h3>

* Split up script into multiple files for improved oversight/readability.
* Centered model icons
---

<h3>v1.9.1</h3>

* Added back old download function if aria2 fails.
---

<h3>v1.9</h3>

* Integrated Aria2 into the download_file function for faster downloading.
* Added more info about current download: Speed, ETA, File Size and % completion.
---

<h3>v1.8.1</h3>

* Sub Folder list now contains 2 default options: `/{Model name}` & `/{Model name}/{Version name}`
---

<h3>v1.8</h3>

* Added ability to download different file types per version.
* Downloading models now uses file ID instead of names.
* NSFW Toggle is now dynamic.
* NSFW Toggle no longer hides images tagged as "Soft".
* Rearranged/Resized UI elements.
* Version list now dynamically updates after download.
* Fixed bug where each model load ran twice.
---

<h3>v1.7.2</h3>

* Fixed a bug where Download button did not get re-enabled properly.
* Fixed a bug where tile status did not get updated properly when download failed.
---

<h3>v1.7.1</h3>

* Dynamic changing of tile status after installation & deletion now correctly detects other versions.
* Base Model filtering dims tiles instead of hiding.
* NSFW Blur increases with tile size.
---

<h3>v1.7</h3>

* Introduced seperate download progress bar, allows to keep browsing whilst downloading.
* Removed force refresh after installing, cancelling and deleting.
* Removed 'Automatically delete old version' option since this relied on a reload after installation.
* Added toggle to sort Tiles by date, this adds a header with the update date and groups models.
* Dynamic changing of tile borders after installation & deletion (doesn't detect old versions yet).
---

<h3>v1.6</h3>

* LoCon models now get saved in the Lora folder if A1111's version is 1.5 or higher.
* improved page_count detection.  
(You can fill in the page number you'd like to visit and press refresh to go to that page)
* Added 'Filter Base Model' dropdown box to dynamically hide any unselected Base models.  
(Please note: This does not impact search results, since the CivitAI API does not yet support this)
---

<h3>v1.5</h3>

* Added slider to change tile size
* Added Download Folder textbox which can be used to define a custom download path.
* Added Sub Folder Dropdown to select any available subfolder(s) as download location.
* Any nested files can now be detected as installed or outdated.
* Automatically selects corresponding folder of any installed models.
* Improved cancellation logic to prevent downloads from continuing.
* Display a timed out message instead of an error icon.
---

<h3>v1.4</h3>

* Download progress load bar is now on web page instead of CMD.
* Better margin fixes with theme detection.
* Delete option now also removes .json files.
* Buttons are now disabled during download. (except cancel button)
* Added Cancel and Delete buttons.
* Download button will now change according to circumstances:
  - Cancel button if there's a current download.
  - Delete button if the selected version is installed.
---

<h3>v1.3.1</h3>

* Fixed new tag saving bugs/oversights.
* Improved trained tags display to not include the model itself.
---

<h3>v1.3</h3>

* Changed 'Save Text' to 'Save Tags' the button now saves tags to a .json file which gets used in image creaton.  
  (If a LORA with saved tags is used it will automatically input all tags into the txt box in image creation)
* Improved padding based on if Lobe theme is being used.
* Added 'Save tags after download' toggle to automatically save .json tags.
* Removed "Get model info" button, click any tile to reload model info instead.
* Removed download link box. (felt unnecessary since there is a Download button)
* Removed "No" from search options, leave the search term empty to not use Search instead.
* Added border radius to cards.
---

<h3>v1.2</h3>

* Made the 'Version' tab show the installed version by default when selecting a model.
* Automatically saves preview image when downloading a model.
* Added [installed] text suffix for any versions that are installed in the 'Version' tab.
* Changed 'Model Filename' from a dropbox to a textbox.
* Made bottom textboxes non typeable.
* Disabled bottom buttons when no model is selected.
* Fixed margin error on the latest tile.
* Fixed error where some old model version(s) did not get removed.
* Improved version checking to be case sensitive.
---

<h3>v1.1</h3>

* Added dropdown box which can filter by time period.
* Changed 'Content type' from buttons to a dropdown box.
* Made selecting a tile always trigger a load, also when the same tile is selected twice.
---

<h3>v1.0</h3>

* Changed 'Get List' to 'Refresh', the button now reloads the current page unless any options have been changed.
* Removed new folder option and removed the function that puts downloads in their own seperate folders.
* Made the glow around frames always visible without hovering.
* Added orange glow for any outdated installed packages.
* Added 'Delete old version after download' option.
* Added ability to manually fill in a page number to load the corresponding page.
* Made the page refresh after a download and made it load during one.
