# sd-civitai-browser
An extension to help download models from CivitAi without leaving WebUI  

This modified add-on is based on [v1.1.0](https://github.com/SignalFlagZ/sd-civitai-browser/releases/tag/1.1.0) from [SignalFlagZ's Fork](https://github.com/SignalFlagZ/sd-civitai-browser)  
I was still missing some features so I decided to add them myself.

NOTE: If an 'Error' shows up on the screen, it's most likely caused by the Civit API timing out, please wait a bit and try again in a few seconds!

# Preview


https://github.com/BlafKing/sd-civitai-browser/assets/9644716/33da2d2e-6bb5-4ea1-be7a-14818b3a86f6


(Theme used: [Lobe](https://github.com/canisminor1990/sd-webui-lobe-theme))  

# Changelog

v1.0

* Changed 'Get List' to 'Refresh', the button now reloads the current page unless any options have been changed.
* Removed new folder option and removed the function that puts downloads in their own seperate folders.
* Made the glow around frames always visible without hovering.
* Added orange glow for any outdated installed packages.
* Added 'Delete old version after download' option.
* Added ability to manually fill in a page number to load the corresponding page.
* Made the page refresh after a download and made it load during one.

---

v1.1

* Added dropdown box which can filter by time period.
* Changed 'Content type' from buttons to a dropdown box.
* Made selecting a tile always trigger a load, also when the same tile is selected twice.

---

v1.2

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

v1.3

* Changed 'Save Text' to 'Save Tags' the button now saves tags to a .json file which gets used in image creaton.  
  (If a LORA with saved tags is used it will automatically input all tags into the txt box in image creation.)
* Improved padding based on if Lobe theme is being used.
* Added 'Save tags after download' toggle to automatically save .json tags
* Removed "Get model info" button, click any tile to reload model info instead.
* Removed download link box. (felt unnecessary since there is a Download button)
* Removed "No" from search options, leave the search term empty to not use Search instead.
* Added border radius to cards.

---

v1.3.1

* Fixed new tag saving bugs/oversights.
* Improved trained tags display to not include the model itself.
