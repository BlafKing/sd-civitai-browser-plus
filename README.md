# CivitAI Browser+
Add-on for [Automatic1111's Stable Difussion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)  

This extension allows you to download models from CivitAi without leaving WebUI!  

This modified add-on is based on [v1.1.0](https://github.com/SignalFlagZ/sd-civitai-browser/releases/tag/1.1.0) from [SignalFlagZ's Fork](https://github.com/SignalFlagZ/sd-civitai-browser)  

**(If you'd like to be able to filter search results on Base Model version, please upvote [my feature request here!](https://civitai.featurebase.app/submissions/64ea19ac4f9cf39e6f9fb2e9))**

# Preview


https://github.com/BlafKing/sd-civitai-browser/assets/9644716/ea873c3e-a7e4-44a8-907a-e9bddf13bc55


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

---

v1.4
* Download progress load bar is now on web page instead of CMD.
* Better margin fixes with theme detection.
* Delete option now also removes .json files.
* Buttons are now disabled during download (except cancel button).
* Added Cancel and Delete buttons.
* Download button will now change according to circumstances:
  - Cancel button if there's a current download.
  - Delete button if the selected version is installed.

---

v1.5
* Added slider to change tile size
* Added Download Folder textbox which can be used to define a custom download path.
* Added Sub Folder Dropdown to select any available subfolder(s) as download location.
* Any nested files can now be detected as installed or outdated.
* Automatically selects corresponding folder of any installed models.
* Improved cancellation logic to prevent downloads from continuing.
* Display a timed out message instead of an error icon.

---

v1.6
* LoCon models now get saved in the Lora folder if A1111's version is 1.5 or higher.
* improved page_count detection.  
(You can fill in the page number you'd like to visit and press refresh to go to that page)
* Added 'Filter Base Model' dropdown box to dynamically hide any unselected Base models.  
(Please note: This does not impact search results, since the CivitAI API does not yet support this)

---

v1.7
* Introduced seperate download progress bar, allows to keep browsing whilst downloading.
* Removed force refresh after installing, cancelling and deleting.
* Removed 'Automatically delete old version' option since this relied on a reload after installation.
* Added toggle to sort Tiles by date, this adds a header with the update date and groups models.
* Dynamic changing of tile borders after installation & deletion (doesn't detect old versions yet).

---

v1.7.1
* Dynamic changing of tile status after installation & deletion now correctly detects other versions.
* Base Model filtering dims tiles instead of hiding
* NSFW Blur increases with tile size

---

v1.7.2
* Fixed a bug where Download button did not get re-enabled properly.
* Fixed a bug where tile status did not get updated properly when download failed.

---

v1.8
* Added ability to download different file types per version.
* Downloading models now uses file ID instead of names.
* NSFW Toggle is now dynamic
* NSFW Toggle no longer hides images tagged as "Soft"
* Rearranged/Resized UI elements
* Fixed bug where each model load ran twice
