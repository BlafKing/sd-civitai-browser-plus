"use strict";

// Selects a model by pressing on card
function select_model(model_name, event, bool = false, content_type = null) {
    if (event) {
        var className = event.target.className;
        if (className.includes('custom-checkbox') || className.includes('model-checkbox')) {
            return;
        }
    }

    const output = bool ? gradioApp().querySelector('#model_sent textarea') : gradioApp().querySelector('#model_select textarea');

    if (output && model_name) {
        const randomNumber = Math.floor(Math.random() * 1000);
        const paddedNumber = String(randomNumber).padStart(3, '0');
        output.value = model_name + "." + paddedNumber;
        updateInput(output);
    }

    if (content_type) {
        const outputType = gradioApp().querySelector('#type_sent textarea');
        const randomNumber = Math.floor(Math.random() * 1000);
        const paddedNumber = String(randomNumber).padStart(3, '0');
        outputType.value = content_type + "." + paddedNumber;
        updateInput(outputType);
    }
}

// Changes the card size
function updateCardSize(width, height) {
    var styleSheet = document.styleSheets[0];
    var dimensionsKeyframes = `width: ${width}em !important; height: ${height}em !important;`;
    
    var fontSize = (width / 8) * 100;
    var textKeyframes = `font-size: ${fontSize}% !important;`;

    addOrUpdateRule(styleSheet, '.civmodelcard img', dimensionsKeyframes);
    addOrUpdateRule(styleSheet, '.civmodelcard .video-bg', dimensionsKeyframes);
    addOrUpdateRule(styleSheet, '.civmodelcard figcaption', textKeyframes);
}

// Toggles NSFW display
function toggleNSFWContent(hideAndBlur) {
    const sheet = document.styleSheets[0];

    const toggleRule = (selector, rules) => addOrUpdateRule(sheet, selector, rules);

    toggleRule('.civcardnsfw', hideAndBlur ? 'display: block;' : 'display: none;');
    toggleRule('.civnsfw img', hideAndBlur ? 'filter: none;' : 'filter: blur(10px);');

    const dateSections = document.querySelectorAll('.date-section');
    dateSections.forEach((section) => {
        const cards = section.querySelectorAll('.civmodelcard');
        const nsfwCards = section.querySelectorAll('.civmodelcard.civcardnsfw');
        section.style.display = !hideAndBlur && cards.length === nsfwCards.length ? 'none' : 'block';
    });

}

// Updates site with css insertions
function addOrUpdateRule(styleSheet, selector, newRules) {
    for (let i = 0; i < styleSheet.cssRules.length; i++) {
        let rule = styleSheet.cssRules[i];
        if (rule.selectorText === selector) {
            rule.style.cssText = newRules;
            return;
        }
    }
    styleSheet.insertRule(`${selector} { ${newRules} }`, styleSheet.cssRules.length);
}

// Updates card border
function updateCard(modelNameWithSuffix) {
    const lastDotIndex = modelNameWithSuffix.lastIndexOf('.');
    const modelName = modelNameWithSuffix.slice(0, lastDotIndex);
    const suffix = modelNameWithSuffix.slice(lastDotIndex + 1);
    let additionalClassName = '';
    switch(suffix) {
        case 'None':
            additionalClassName = '';
            break;
        case 'Old':
            additionalClassName = 'civmodelcardoutdated';
            break;
        case 'New':
            additionalClassName = 'civmodelcardinstalled';
            break;
        default:
            return;
    }
    const parentDiv = document.querySelector('.civmodellist');
    if (parentDiv) {
        const cards = parentDiv.querySelectorAll('.civmodelcard');
        cards.forEach((card) => {
            const onclickAttr = card.getAttribute('onclick');
            if (onclickAttr && onclickAttr.includes(`select_model('${modelName}', event)`)) {
                card.className = `civmodelcard  ${additionalClassName}`;
            }
        });
    }
}

// Enables refresh with alt+enter and ctrl+enter
document.addEventListener('keydown', function(e) {
    var handled = false;

    if (e.key !== undefined) {
        if ((e.key == "Enter" && (e.metaKey || e.ctrlKey || e.altKey))) handled = true;
    } else if (e.keyCode !== undefined) {
        if ((e.keyCode == 13 && (e.metaKey || e.ctrlKey || e.altKey))) handled = true;
    }

    if (handled) {
        var currentTabContent = get_uiCurrentTabContent();
        if (currentTabContent && currentTabContent.id === "tab_civitai_interface") {

            var refreshButton = currentTabContent.querySelector('#refreshBtn');
            if (!refreshButton) {
                refreshButton = currentTabContent.querySelector('#refreshBtnL');
            }
            if (refreshButton) {
                refreshButton.click();
            }

            e.preventDefault();
        }
    }
});

// Function for the back to top button
function BackToTop() {
    const c = Math.max(document.body.scrollTop, document.documentElement.scrollTop);
    if (c > 0) {
        window.requestAnimationFrame(BackToTop);
        document.body.scrollTop = c - c / 8;
        document.documentElement.scrollTop = c - c / 8;
    }
}

// Function to adjust alignment of Filter Accordion
function adjustFilterBoxAndButtons() {
    const element = document.querySelector("#filterBox") || document.querySelector("#filterBoxL");
    if (!element) return;

    const childDiv = element.querySelector("div:nth-child(3)");
    if (!childDiv) return;

    const isLargeScreen = window.innerWidth >= 1250;
    const isMediumScreen = window.innerWidth < 1250 && window.innerWidth > 915;
    const isNarrowScreen = window.innerWidth < 800;
    const modelBlocks = document.querySelectorAll("#civitai_preview_html .model-block");
    const civitInfo = document.querySelector(".civitai-version-info");
    
    if (modelBlocks) {
        modelBlocks.forEach(modelBlock => {
            if (isNarrowScreen) {
                modelBlock.style.flexWrap = "wrap";
                modelBlock.style.justifyContent = "center";
            } else {
                modelBlock.style.flexWrap = "nowrap";
                modelBlock.style.justifyContent = "flex-start";
            }
        });
    } if (civitInfo) {
        if (window.innerWidth < 900) {
            civitInfo.style.flexWrap = "wrap";
        } else {
            civitInfo.style.flexWrap = "nowrap";
        }
    }
    

    childDiv.style.marginLeft = isLargeScreen ? "0px" : isMediumScreen ? `${1250 - window.innerWidth}px` : "0px";
    element.style.justifyContent = isLargeScreen || isMediumScreen ? "center" : "flex-start";

    const pageBtn1 = document.querySelector("#pageBtn1");
    const pageBtn2 = document.querySelector("#pageBtn2");
    const pageBox = document.querySelector("#pageBox");
    const pageBoxMobile = document.querySelector("#pageBoxMobile");

    if (window.innerWidth < 530) {
        childDiv.style.width = "300px";
        if (pageBoxMobile) {
            pageBtn1 && pageBoxMobile.appendChild(pageBtn1);
            pageBtn2 && pageBoxMobile.appendChild(pageBtn2);
            pageBoxMobile.style.paddingBottom = "15px";
        }
    } else {
        childDiv.style.width = "400px";
        if (pageBox) {
            pageBtn1 && pageBox.insertBefore(pageBtn1, pageBox.firstChild);
            pageBtn2 && pageBox.appendChild(pageBtn2);
            pageBoxMobile.style.paddingBottom = "0px";
        }
    }
}

// Calls the function above whenever the window is resized
window.addEventListener("resize", adjustFilterBoxAndButtons);

// Function to trigger refresh button with extra checks for page slider
function pressRefresh() {
    setTimeout(() => {
        const input = document.querySelector("#pageSlider > div:nth-child(2) > div > input");
        if (document.activeElement === input) {
            input.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.keyCode === 13) {
                    input.blur();
                }
            });
            input.addEventListener('blur', function() {
                return;
            });

            return;
        }

        let button = document.querySelector("#refreshBtn");
        if (!button) {
            button = document.querySelector("#refreshBtnL");
        }
        if (button) {
            button.click();
        } else {
            console.error("Both buttons with IDs #refreshBtn and #refreshBtnL not found.");
        }
    }, 200);
}

// Update SVG Icons based on dark theme or light theme
function updateSVGIcons() {
    const isDark = document.body.classList.contains('dark');
    const filterIconUrl = isDark ? "https://gistcdn.githack.com/BlafKing/a20124cedafad23d4eecc1367ec22896/raw/04a4dae0771353377747dadf57c91d55bf841bed/filter-light.svg" : "https://gistcdn.githack.com/BlafKing/686c3438f5d0d13e7e47135f25445ef3/raw/46477777faac7209d001829a171462d9a2ff1467/filter-dark.svg";
    const searchIconUrl = isDark ? "https://gistcdn.githack.com/BlafKing/3f95619089bac3b4fd5470a986e1b3bb/raw/ebaa9cceee3436711eb560a7a65e151f1d651c6a/search-light.svg" : "https://gistcdn.githack.com/BlafKing/57573592d5857e102a4bfde852f62639/raw/aa213e9e82d705651603507e26545eb0ffe60c90/search-dark.svg";

    const element = document.querySelector("#filterBox, #filterBoxL");
    const childDiv = element?.querySelector("div:nth-child(3)");

    if (childDiv) {
        childDiv.style.cssText = `box-shadow: ${isDark ? '#ffffff' : '#000000'} 0px 0px 2px 0px; display: none;`;
    }

    const style = document.createElement('style');
    style.innerHTML = `
        #filterBox > div:nth-child(2) > span:nth-child(2)::before,
        #filterBoxL > div:nth-child(2) > span:nth-child(2)::before {
            background: url('${filterIconUrl}') no-repeat center center;
            background-size: contain;
        }
    `;
    document.head.appendChild(style);

    const refreshBtn = document.querySelector("#refreshBtn, #refreshBtnL");
    const targetSearchElement = refreshBtn?.firstChild || refreshBtnL?.firstChild;

    if (targetSearchElement) {
        targetSearchElement.src = searchIconUrl;
    }
}

// Creates a tooltip if the user wants to filter liked models without a personal API key
function createTooltip(element, hover_element, insertText) {
    if (element) {
        const tooltip = document.createElement('div');
        tooltip.className = 'browser_tooltip';
        tooltip.textContent = insertText;
        tooltip.style.cssText = 'display: none; text-align: center; white-space: pre;';

        hover_element.addEventListener('mouseover', () => {
            tooltip.style.display = 'block';
        });
        hover_element.addEventListener('mouseout', () => {
            tooltip.style.display = 'none';
        });
        element.appendChild(tooltip);
    }
}

// Function that closes filter dropdown if clicked outside the dropdown
function setupClickOutsideListener() {
    var filterBox = document.getElementById("filterBoxL") || document.getElementById("filterBox");
    var filterButton = filterBox.getElementsByTagName("div")[1];
    var dropDown = filterBox.getElementsByTagName("div")[2];

    function clickOutsideHandler(event) {
        var target = event.target;
        if (!filterBox.contains(target)) {
            if (!dropDown.contains(target)) {
                if (filterButton.className.endsWith("open")) {
                    filterButton.click();
                }
            }
        }
    }
    document.addEventListener("click", clickOutsideHandler);
}

// Create hyperlink in settings to CivitAI account settings
function createLink(infoElement) {

    const existingText = "(You can create your own API key in your CivitAI account settings, this required for some downloads, Requires UI reload)";
    const linkText = "CivitAI account settings";
    
    const [textBefore, textAfter] = existingText.split(linkText);
    
    const link = document.createElement('a');
    link.textContent = linkText;
    link.href = 'https://civitai.com/user/account';
    link.target = '_blank';
    
    while (infoElement.firstChild) infoElement.removeChild(infoElement.firstChild);
    
    infoElement.appendChild(document.createTextNode(textBefore));
    infoElement.appendChild(link);
    infoElement.appendChild(document.createTextNode(textAfter));
}

// Function to update the visibility of backToTopDiv based on the intersection with civitaiDiv
function updateBackToTopVisibility(entries) {
    var backToTopDiv = document.getElementById('backToTopContainer');
    var civitaiDiv = document.getElementById('civitai_preview_html');
    
    if (civitaiDiv.clientHeight > 0 && entries[0].isIntersecting && window.scrollY !== 0) {
        backToTopDiv.style.visibility = 'visible';
    } else {
        backToTopDiv.style.visibility = 'hidden';
    }
}

// Options for the Intersection Observer
var options = {
    root: null,
    rootMargin: '0px 0px -60px 0px',
    threshold: 0
};

// Create an Intersection Observer instance
const observer = new IntersectionObserver(updateBackToTopVisibility, options);

function handleCivitaiDivChanges() {
    var civitaiDiv = document.getElementById('civitai_preview_html');
    observer.unobserve(civitaiDiv);
    observer.observe(civitaiDiv);
}

document.addEventListener("scroll", handleCivitaiDivChanges)

// Create the accordion dropdown inside the settings tab
function createAccordion(containerDiv, subfolders, name) {
    if (containerDiv == null || subfolders.length == 0) {
        return;
    }
    var accordionContainer = document.createElement('div'); 
    accordionContainer.id = 'settings-accordion';
    var toggleButton = document.createElement('button');
    toggleButton.id = 'accordionToggle';
    toggleButton.innerHTML = name + '<div style="transition: transform 0.15s; transform: rotate(90deg)">▼</div>';
    toggleButton.onclick = function () {
        accordionDiv.style.display = (accordionDiv.style.display === 'none') ? 'block' : 'none';
        toggleButton.lastChild.style.transform = accordionDiv.style.display === 'none' ? 'rotate(90deg)' : 'rotate(0)';
    };
    
    accordionContainer.appendChild(toggleButton);
    var accordionDiv = document.createElement('div');
    accordionDiv.classList.add('accordion');
    accordionDiv.append(...subfolders);
    accordionDiv.style.display = 'none';
    accordionContainer.appendChild(accordionDiv);
    containerDiv.appendChild(accordionContainer);
}

// Adds a button to the cards in txt2img and img2img
function createCardButtons(event) {
    const clickedElement = event.target;
    const validButtonNames = ['Textual Inversion', 'Hypernetworks', 'Checkpoints', 'Lora'];
    const validParentIds = ['txt2img_textual_inversion_cards_html', 'txt2img_hypernetworks_cards_html', 'txt2img_checkpoints_cards_html', 'txt2img_lora_cards_html'];

    const hasMatchingButtonName = clickedElement && clickedElement.innerText && validButtonNames.some(buttonName =>
        clickedElement.innerText.trim() === buttonName
    );

    const flexboxDivs = document.querySelectorAll('.layoutkit-flexbox');
    let isLobeTheme = false;
    flexboxDivs.forEach(div => {
        const anchorElements = div.querySelectorAll('a');
        const hasGitHubLink = Array.from(anchorElements).some(anchor => anchor.href === 'https://github.com/lobehub/sd-webui-lobe-theme/releases');
        if (hasGitHubLink) {
            isLobeTheme = true;
        }
    });

    if (hasMatchingButtonName || isLobeTheme) {
        const checkForCardDivs = setInterval(() => {
            const cardDivs = document.querySelectorAll('.card');

            if (cardDivs.length > 0) {
                clearInterval(checkForCardDivs);
                
                const cardScale = document.querySelector('#setting_extra_networks_card_text_scale > div > div > input').valueAsNumber * 100;
                const viewBoxHeight = (cardScale < 100) ? (100 - cardScale) * 2 : -(cardScale - 100) * 2;

                cardDivs.forEach(cardDiv => {
                    const buttonRow = cardDiv.querySelector('.button-row');
                    const actions = cardDiv.querySelector('.actions');
                    if (!actions) {
                        return;
                    }
                    const nameSpan = actions.querySelector('.name');
                    let modelName  = nameSpan.textContent.trim();
                    let currentElement = cardDiv.parentElement;
                    let content_type = null;

                    while (currentElement) {
                        const parentId = currentElement.id;
                        if (validParentIds.includes(parentId)) {
                            content_type = parentId;
                            break;
                        }
                        currentElement = currentElement.parentElement;
                    }

                    const existingDiv = buttonRow.querySelector('.goto-civitbrowser.card-button');
                    if (existingDiv) {
                        return;
                    }

                    const metaDataButton = buttonRow.querySelector('.metadata-button.card-button');
                    
                    const newDiv = document.createElement('div');
                    newDiv.classList.add('goto-civitbrowser', 'card-button');
                    newDiv.addEventListener('click', function (event) {
                        event.stopPropagation();
                        modelInfoPopUp(modelName, content_type);
                    });

                    const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    if (isLobeTheme) {
                        svgIcon.setAttribute('width', '25');
                        svgIcon.setAttribute('height', '25');
                    } else {
                        if (metaDataButton) {
                            metaDataButton.style.paddingTop = '5px';
                            metaDataButton.style.width = '42px';
                            metaDataButton.style.fontSize = '230%';
                        }
                        svgIcon.setAttribute('width', '40');
                        svgIcon.setAttribute('height', '40');
                        newDiv.setAttribute('style', 'width: 42px !important;');
                    }
                    svgIcon.setAttribute('viewBox', `75 ${viewBoxHeight} 500 500`);
                    svgIcon.setAttribute('fill', 'white');
                    svgIcon.setAttribute('style', `scale: ${cardScale}%;`);

                    svgIcon.innerHTML = `
                        <path d="M 352.79 218.85 L 319.617 162.309 L 203.704 162.479 L 146.28 259.066 L 203.434 355.786 L 319.373 355.729 L 352.773 299.386 L 411.969 299.471 L 348.861 404.911 L 174.065 404.978 L 87.368 259.217 L 174.013 113.246 L 349.147 113.19 L 411.852 218.782 L 352.79 218.85 Z"/>
                        <path d="M 304.771 334.364 L 213.9 334.429 L 169.607 259.146 L 214.095 183.864 L 305.132 183.907 L 330.489 227.825 L 311.786 259.115 L 330.315 290.655 Z M 278.045 290.682 L 259.294 259.18 L 278.106 227.488 L 240.603 227.366 L 221.983 259.128 L 240.451 291.026 Z"/>
                    `;

                    newDiv.appendChild(svgIcon);
                    buttonRow.insertBefore(newDiv, buttonRow.firstChild);
                });
            }
        }, 100);
    }
}
document.addEventListener('click', createCardButtons);

function modelInfoPopUp(modelName, content_type) {
    select_model(modelName, null, true, content_type);

    // Create the overlay
    var overlay = document.createElement('div');
    overlay.classList.add('civitai-overlay');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(20, 20, 20, 0.95)';
    overlay.style.zIndex = '1001';
    overlay.style.overflowY = 'auto';

    // Create the close button
    var closeButton = document.createElement('div');
    closeButton.classList.add('civitai-overlay-close');
    closeButton.textContent = '×';
    closeButton.style.zIndex = '1011';
    closeButton.style.position = 'fixed';
    closeButton.style.right = '22px';
    closeButton.style.top = '0';
    closeButton.style.cursor = 'pointer';
    closeButton.style.color = 'white';
    closeButton.style.fontSize = '32pt';
    closeButton.addEventListener('click', hidePopup);
    document.addEventListener('keydown', handleKeyPress);

    // Create the pop-up window
    var inner = document.createElement('div');
    inner.classList.add('civitai-overlay-inner');
    inner.style.position = 'absolute';
    inner.style.top = '50%';
    inner.style.left = '50%';
    inner.style.width = 'auto';
    inner.style.transform = 'translate(-50%, -50%)';
    inner.style.background = 'var(--body-background-fill)';
    inner.style.padding = '2em';
    inner.style.borderRadius = 'var(--block-radius)';
    inner.style.borderStyle = 'solid';
    inner.style.borderWidth = 'var(--block-border-width)';
    inner.style.borderColor = 'var(--block-border-color)';
    inner.style.zIndex = '1001';

    // Placeholder model content until model is loaded by other function
    var modelInfo = document.createElement('div');
    modelInfo.classList.add('civitai-overlay-text');
    modelInfo.textContent = 'Loading model info, please wait!';
    modelInfo.style.fontSize = '24px';
    modelInfo.style.color = 'white';
    modelInfo.style.fontFamily = 'var(--font)';

    document.body.style.overflow = 'hidden';
    document.body.appendChild(overlay);
    overlay.appendChild(closeButton);
    overlay.appendChild(inner);
    inner.appendChild(modelInfo);

    overlay.addEventListener('click', function (event) {
        if (event.target === overlay) {
            hidePopup();
        }
    });

    setDynamicWidth(inner);

    // Update width on window resize
    window.addEventListener('resize', function() {
        setDynamicWidth(inner);
    });
}

function setDynamicWidth(inner) {
    var windowWidth = window.innerWidth;
    var dynamicWidth = Math.min(Math.max(windowWidth - 150, 350), 900);
    inner.style.width = dynamicWidth + 'px';
}

// Function to hide the popup
function hidePopup() {
    var overlay = document.querySelector('.civitai-overlay');
    if (overlay) {
        document.body.removeChild(overlay);
        document.body.style.overflow = 'auto';
        window.removeEventListener('resize', setDynamicWidth);
    }
}

// Function to handle key presses
function handleKeyPress(event) {
    if (event.key === 'Escape') {
        hidePopup();
    }
}

function inputHTMLPreviewContent(html_input) {
    var inner = document.querySelector('.civitai-overlay-inner')
    let startIndex = html_input.indexOf("'value': '");
    if (startIndex !== -1) {
        startIndex += "'value': '".length;
        const endIndex = html_input.indexOf("', 'type': None,", startIndex);
        if (endIndex !== -1) {
            let extractedText = html_input.substring(startIndex, endIndex);
            var modelIdNotFound = extractedText.includes(">Model ID not found.<br>The");

            extractedText = extractedText.replace(/\\n\s*</g, '<');
            extractedText = extractedText.replace(/\\n/g, ' ');
            extractedText = extractedText.replace(/\\t/g, '');
            extractedText = extractedText.replace(/\\'/g, "'");
            
            var overlayText = document.querySelector('.civitai-overlay-text');
            var modelInfo = document.createElement('div');
            
            overlayText.parentNode.removeChild(overlayText);
            if (!modelIdNotFound) {
                inner.style.top = 0;
                inner.style.transform = 'translate(-50%, 0)';
            }
            modelInfo.innerHTML = extractedText;
            inner.appendChild(modelInfo);
        }
    }
}

function metaToTxt2Img(type, element) {
    const selection = window.getSelection();
    if (selection.toString().length > 0) {
        return;
    }
    const genButton = gradioApp().querySelector('#txt2img_extra_tabs > div > button')
    let input = element.querySelector('dd').textContent;
    let inf;
    if (input.endsWith(',')) {
        inf = input + ' ';
    } else {
        inf = input + ', ';
    }
    let is_positive = false
    let is_negative = false
    switch(type) {
        case 'Prompt':
            is_positive = true
            break;
        case 'Negative prompt':
            inf = 'Negative prompt: ' + inf;
            is_negative = true
            break;
        case 'Seed':
            inf = 'Seed: ' + inf;
            inf = inf + inf + inf;
            break;
        case 'Size':
            inf = 'Size: ' + inf;
            inf = inf + inf + inf;
            break;
        case 'Model':
            inf = 'Model: ' + inf;
            inf = inf + inf + inf;
            break;
        case 'Clip skip':
            inf = 'Clip skip: ' + inf;
            inf = inf + inf + inf;
            break;
        case 'Sampler':
            inf = 'Sampler: ' + inf;
            inf = inf + inf + inf;
            break;
        case 'Steps':
            inf = 'Steps: ' + inf;
            inf = inf + inf + inf;
            break;
        case 'CFG scale':
            inf = 'CFG scale: ' + inf;
            inf = inf + inf + inf;
            break;
    }
    const prompt = gradioApp().querySelector('#txt2img_prompt textarea');
    const neg_prompt = gradioApp().querySelector('#txt2img_neg_prompt textarea');
    const cfg_scale = gradioApp().querySelector('#txt2img_cfg_scale > div:nth-child(2) > div > input');
    let final = '';
    let cfg = 'CFG scale: ' + cfg_scale.value + ", "
    let prompt_addon = cfg + cfg + cfg
    if (is_positive) {
        final = inf + "\nNegative prompt: " + neg_prompt.value + "\n" + prompt_addon;
    } else if (is_negative) {
        final = prompt.value + "\n" + inf + "\n" + prompt_addon;
    } else {
        final = prompt.value + "\nNegative prompt: " + neg_prompt.value + "\n" + inf;
    }
    genInfo_to_txt2img(final, false)
    hidePopup();
    sendClick(genButton);
}

// Creates a list of the selected models
var selectedModels = [];
var selectedTypes = [];
function multi_model_select(modelName, modelType, isChecked) {
    if (arguments.length === 0) {
        selectedModels = [];
        selectedTypes = [];
        return;
    }
    if (isChecked) {
        if (!selectedModels.includes(modelName)) {
            selectedModels.push(modelName);
        }
        selectedTypes.push(modelType)
    } else {
        var modelIndex = selectedModels.indexOf(modelName);
        if (modelIndex > -1) {
            selectedModels.splice(modelIndex, 1);
        }
        var typesIndex = selectedTypes.indexOf(modelType);
        if (typesIndex > -1) {
            selectedTypes.splice(typesIndex, 1);
        }
    }
    const selected_model_list = gradioApp().querySelector('#selected_model_list textarea');
    selected_model_list.value = JSON.stringify(selectedModels);

    const selected_type_list = gradioApp().querySelector('#selected_type_list textarea');
    selected_type_list.value = JSON.stringify(selectedTypes);
    
    updateInput(selected_model_list);
    updateInput(selected_type_list);
}

// Metadata button click detector
document.addEventListener('click', function(event) {
    var target = event.target;
    if (target.classList.contains('edit-button') && target.classList.contains('card-button')) {
        var parentDiv = target.parentElement;
        var actionsDiv = parentDiv.nextElementSibling;
        if (actionsDiv && actionsDiv.classList.contains('actions')) {
            var nameSpan = actionsDiv.querySelector('.name');
            if (nameSpan) {
                var nameValue = nameSpan.textContent;
                onEditButtonCardClick(nameValue);
            }
        }
    }
}, true);

// CivitAI Link Button Creation
function onEditButtonCardClick(nameValue) {
    var checkInterval = setInterval(function() {
        var globalPopupInner = document.querySelector('.global-popup-inner');
        var titleElement = globalPopupInner.querySelector('.extra-network-name');
        if (titleElement.textContent.trim() === nameValue.trim()) {
            var descriptionSpan = Array.from(globalPopupInner.querySelectorAll('span')).find(span => span.textContent.trim() === "Description");
            if (descriptionSpan) {
                var descriptionTextarea = descriptionSpan.nextElementSibling;
                if (descriptionTextarea.value.startsWith('Model URL:')) {
                    var matches = descriptionTextarea.value.match(/"([^"]+)"/);
                    if (matches && matches[1]) {
                        var modelUrl = matches[1];

                        var grandParentDiv = descriptionTextarea.parentElement.parentElement.parentElement.parentElement;
                        var imageDiv = grandParentDiv.nextElementSibling
                        var openInCivitaiDiv = document.querySelector('.open-in-civitai');
                        if (!openInCivitaiDiv) {
                            openInCivitaiDiv = document.createElement('div');
                            openInCivitaiDiv.classList.add('open-in-civitai');
                            imageDiv.appendChild(openInCivitaiDiv);
                        }
                        openInCivitaiDiv.innerHTML = '<a href="' + modelUrl + '" target="_blank" onclick="window.open(this.href, \'_blank\'); return false;">Open on CivitAI</a>';
                    }
                    else {
                        var openInCivitaiDiv = document.querySelector('.open-in-civitai');
                        if (openInCivitaiDiv) {
                            openInCivitaiDiv.remove();
                        }
                    }
                } else {
                    var openInCivitaiDiv = document.querySelector('.open-in-civitai');
                    if (openInCivitaiDiv) {
                        openInCivitaiDiv.remove();
                    }
                }
            }
            clearInterval(checkInterval);
        }
    }, 100);
}

function sendClick(location) {
    const clickEvent = new MouseEvent('click', {
        view: window,
        bubbles: true,
        cancelable: true
    });
    location.dispatchEvent(clickEvent);
}

let currentDlCancelled = false;

function cancelCurrentDl() {
    currentDlCancelled = true;
}

let allDlCancelled = false;

function cancelAllDl() {
    allDlCancelled = true;
}

function setSortable() {
    new Sortable(document.getElementById('queue_list'), {
        onEnd: function(evt) {
            const gradio_input = document.querySelector('#civitai_dl_list.prose').innerHTML;
            const gradio_html = gradioApp().querySelector('#queue_html_input textarea');
            let output = gradioApp().querySelector('#arrange_dl_id textarea');
            output.value = evt.item.getAttribute('dl_id') + "." +  evt.newIndex;
            updateInput(output);
            gradio_html.value = gradio_input;
            updateInput(gradio_html);
        }
    });
}

function cancelQueueDl() {
    const cancelBtn = gradioApp().querySelector('#html_cancel_input textarea');
    const randomNumber = Math.floor(Math.random() * 1000);
    const paddedNumber = String(randomNumber).padStart(3, '0');
    cancelBtn.value = paddedNumber;
    updateInput(cancelBtn);cancelBtn
}

function setDownloadProgressBar() {
    const gradio_html = gradioApp().querySelector('#queue_html_input textarea');
    let browserContainer = document.querySelector('#DownloadProgress');
    let browserProgress = browserContainer.querySelector('.progress-bar');
    if (!browserProgress || !browserProgress.style.width) {
        setTimeout(setDownloadProgressBar, 500);
        return;
    }

    let dlList = document.getElementById('civitai_dl_list');
    let nonQueue = dlList.querySelector('.civitai_nonqueue_list');
    let dlItem = dlList.querySelector('.civitai_dl_item');
    let dlBtn = dlItem.querySelector('.dl_action_btn > span');
    dlBtn.innerText = "Cancel";
    dlBtn.setAttribute('onclick', 'cancelQueueDl()');
    let dlId = dlItem.getAttribute('dl_id');
    let selector = '.civitai_dl_item[dl_id="' + parseInt(dlId) + '"]';

    let dlProgressBar = null;
    let percentage = null;
    let dlText = null;

    nonQueue.appendChild(dlItem);

    const interval = setInterval(() => {
        browserContainer = document.querySelector('#DownloadProgress');
        browserProgress = browserContainer.querySelector('.progress-bar');
        dlText = browserContainer.querySelector('.progress-level-inner');
        if (!dlText) {
            return;
        }
        dlText = dlText.innerText
        percentage = parseFloat(browserProgress.style.width);

        dlItem = dlList.querySelector(selector);
        dlProgressBar = dlItem.querySelector('.dl_progress_bar');

        dlProgressBar.textContent = percentage.toFixed(1) + '%';
        dlProgressBar.style.width = percentage + '%';

        if (percentage >= 100) {
            clearInterval(interval);
            dlBtn = dlItem.querySelector('.dl_action_btn > span');
            dlBtn.innerText = "Remove";
            dlBtn.setAttribute('onclick', 'removeDlItem(' + parseInt(dlId) + ', this)');
            dlItem.className = 'civitai_dl_item_completed';
            dlProgressBar.textContent = 'Completed';
            dlProgressBar.style.width = '100%';
            const gradio_input = document.querySelector('#civitai_dl_list.prose').innerHTML;
            gradio_html.value = gradio_input
            updateInput(gradio_html);
            return;
        }

        if (currentDlCancelled) {
            clearInterval(interval);
            dlBtn = dlItem.querySelector('.dl_action_btn > span');
            dlBtn.innerText = "Remove";
            dlBtn.setAttribute('onclick', 'removeDlItem(' + parseInt(dlId) + ', this)');
            currentDlCancelled = false;
            dlItem.className = 'civitai_dl_item_failed';
            dlProgressBar.textContent = 'Cancelled';
            dlProgressBar.style.width = "0%";
            const gradio_input = document.querySelector('#civitai_dl_list.prose').innerHTML;
            gradio_html.value = gradio_input
            updateInput(gradio_html);
            return;
        } else if (allDlCancelled) {
            clearInterval(interval);
            allDlCancelled = false;
            let dlItems = dlList.querySelectorAll('.civitai_dl_item');
            dlItems.forEach(function(item) {
                dlBtn = dlItem.querySelector('.dl_action_btn > span');
                dlBtn.innerText = "Remove";
                dlBtn.setAttribute('onclick', 'removeDlItem(' + parseInt(dlId) + ', this)');
                dlProgressBar = item.querySelector('.dl_progress_bar');
                dlProgressBar.textContent = 'Cancelled';
                dlProgressBar.style.width = "0%";
                nonQueue.appendChild(item);
                item.className = 'civitai_dl_item_failed';
            });
            const gradio_input = document.querySelector('#civitai_dl_list.prose').innerHTML;
            gradio_html.value = gradio_input
            updateInput(gradio_html);
            return;
        } else if (dlText.includes('Encountered an error during download of') || dlText.includes('not found on CivitAI servers') || dlText.includes('requires a personal CivitAI API to be downloaded')) {
            clearInterval(interval);
            dlBtn = dlItem.querySelector('.dl_action_btn > span');
            dlBtn.innerText = "Remove";
            dlBtn.setAttribute('onclick', 'removeDlItem(' + parseInt(dlId) + ', this)');
            dlItem.className = 'civitai_dl_item_failed';
            dlProgressBar.textContent = 'Failed';
            dlProgressBar.style.width = "0%";
            const gradio_input = document.querySelector('#civitai_dl_list.prose').innerHTML;
            gradio_html.value = gradio_input
            updateInput(gradio_html);
            return;
        }
    }, 500);
}

function removeDlItem(dl_id, element) {
    const gradio_html = gradioApp().querySelector('#queue_html_input textarea');
    const output = gradioApp().querySelector('#remove_dl_id textarea');
    var dl_item = element.parentNode.parentNode;
    dl_item.parentNode.removeChild(dl_item);
    output.value = dl_id
    updateInput(output);

    const gradio_input = document.querySelector('#civitai_dl_list.prose').innerHTML;
    gradio_html.value = gradio_input;
    updateInput(gradio_html);
}

// Selects all models
function selectAllModels() {
    const checkboxes = Array.from(document.querySelectorAll('.model-checkbox'));
    const allChecked = checkboxes.every(checkbox => checkbox.checked);
    const allUnchecked = checkboxes.every(checkbox => !checkbox.checked);
    if (allChecked || allUnchecked) {
        checkboxes.forEach(sendClick);
    } else {
        checkboxes.filter(checkbox => !checkbox.checked).forEach(sendClick);
    }
}

// Deselects all models
function deselectAllModels() {
    setTimeout(() => {
        const checkboxes = Array.from(document.querySelectorAll('.model-checkbox'));
        checkboxes.filter(checkbox => checkbox.checked).forEach(sendClick);
    }, 1000);
}

// Sends Image URL to Python to pull generation info
function sendImgUrl(image_url) {
    const randomNumber = Math.floor(Math.random() * 1000);
    const genButton = gradioApp().querySelector('#txt2img_extra_tabs > div > button')
    const paddedNumber = String(randomNumber).padStart(3, '0');
    const input = gradioApp().querySelector('#civitai_text2img_input textarea');
    input.value = paddedNumber + "." + image_url;
    updateInput(input);
    hidePopup();
    sendClick(genButton);
}

// Sends txt2img info to txt2img tab
function genInfo_to_txt2img(genInfo, do_slice=true) {
    let insert = gradioApp().querySelector('#txt2img_prompt textarea');
    let pasteButton = gradioApp().querySelector('#paste');
    if (genInfo) {
        insert.value = do_slice ? genInfo.slice(5) : genInfo;
        insert.dispatchEvent(new Event('input', { bubbles: true }));
        pasteButton.dispatchEvent(new Event('click', { bubbles: true }));
    }
}

// Hide installed models
function hideInstalled(toggleValue) {
    const modelList =  document.querySelectorAll('.column.civmodellist > .civmodelcardinstalled')
    modelList.forEach(item => {
        item.style.display = toggleValue ? 'none' : 'block';
    });
}

// Runs all functions when the page is fully loaded
function onPageLoad() {
    const divElement = document.getElementById('setting_custom_api_key');
    let civitaiDiv = document.getElementById('civitai_preview_html');
    let queue_list = document.querySelector("#queue_list");
    const infoElement = divElement?.querySelector('.info');
    if (!infoElement) {
        return;
    }

    clearInterval(intervalID);
    updateSVGIcons();

    let subfolderDiv = document.querySelector("#settings_civitai_browser_plus > div > div");
    let downloadDiv = document.querySelector("#settings_civitai_browser_download > div > div");
    if (subfolderDiv || downloadDiv) {
        let div = subfolderDiv || downloadDiv;
        let subfolders = div.querySelectorAll("[id$='subfolder']");
        createAccordion(div, subfolders, "Default sub folders");
    }

    let upscalerDiv = document.querySelector("#settings_civitai_browser_plus > div > div > #settings-accordion > div");
    let downloadDivSub = document.querySelector("#settings_civitai_browser_download > div > div > #settings-accordion > div");
    if (upscalerDiv || downloadDivSub) {
        let div = upscalerDiv || downloadDivSub;
        let upscalers = div.querySelectorAll("[id$='upscale_subfolder']");
        createAccordion(div, upscalers, "Upscalers");
    }

    let settingsDiv = document.querySelector("#settings_civitai_browser > div > div");
    if (subfolderDiv || settingsDiv) {
        let div = subfolderDiv || settingsDiv;
        let subfolders = div.querySelectorAll("[id^='setting_insert_sub']");
        createAccordion(div, subfolders, "Insert sub folder options");
    }

    
    let toggle4L = document.getElementById('toggle4L');
    let toggle4 = document.getElementById('toggle4');
    if (toggle4L || toggle4) {
        let like_toggle = toggle4L || toggle4;
        let insertText = 'Requires an API Key\nConfigurable in CivitAI settings tab';
        createTooltip(like_toggle, like_toggle, insertText);
    }

    let hash_toggle_hover = document.querySelector('#skip_hash_toggle > label');
    let hash_toggle = document.querySelector('#skip_hash_toggle');
    if (hash_toggle) {
        let insertText = 'This option generates unique hashes for models that were not downloaded with this extension.\nA hash is required for any of the options below to work, a model with no hash will be skipped.\nInitial hash generation is a one-time process per file.';
        createTooltip(hash_toggle, hash_toggle_hover, insertText);
    }

    observer.observe(civitaiDiv);
    adjustFilterBoxAndButtons();
    setupClickOutsideListener();
    createLink(infoElement);
    updateBackToTopVisibility([{isIntersecting: false}]);
}

// Checks every second if the page is fully loaded
let intervalID = setInterval(onPageLoad, 1000);