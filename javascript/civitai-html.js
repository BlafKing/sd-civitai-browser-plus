"use strict";

// Selects a model by pressing on card
function select_model(model_name, event, bool = false, content_type = null, sendToBrowser = false) {
    if (event) {
        var className = event.target.className;
        if (className.includes('custom-checkbox') || className.includes('model-checkbox')) {
            return;
        }
    }

    let output;
    if (sendToBrowser) {
        output = gradioApp().querySelector('#send_to_browser textarea')
    } else {
        output = bool ? gradioApp().querySelector('#model_sent textarea') : gradioApp().querySelector('#model_select textarea');
    }

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

// Clicks the first item in the browser cards list
function clickFirstFigureInColumn() {
    setTimeout(() => {
        const columnDiv = document.querySelector('.column.civmodellist');
        if (columnDiv) {
            const firstFigure = columnDiv.querySelector('figure');
            if (firstFigure) {
                firstFigure.click();
            }
        }
    }, 500);
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
    const nsfwCards = document.querySelectorAll('.civcardnsfw');
    nsfwCards.forEach(card => {
        card.style.display = hideAndBlur ? 'block' : 'none';
    })

    const nsfwImages = document.querySelectorAll('.civnsfw img');
    nsfwImages.forEach(img => {
        img.style.filter = hideAndBlur ? 'none' : 'blur(10px)';
    });

    const dateSections = document.querySelectorAll('.date-section');
    dateSections.forEach(section => {
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
function keydownHandler(e) {
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
}
document.addEventListener('keydown', keydownHandler);

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
            function keydownHandler(event) {
                if (event.key === 'Enter' || event.keyCode === 13) {
                    input.blur();
                    input.removeEventListener('keydown', keydownHandler);
                    input.removeEventListener('blur', blurHandler);
                }
            }

            function blurHandler() {
                input.removeEventListener('keydown', keydownHandler);
                input.removeEventListener('blur', blurHandler);
            }

            input.addEventListener('keydown', keydownHandler);
            input.addEventListener('blur', blurHandler);

            return;
        }
        let output = gradioApp().querySelector('#page_slider_trigger textarea');
        if (output) {
            const randomNumber = Math.floor(Math.random() * 1000);
            const paddedNumber = String(randomNumber).padStart(3, '0');
            output.value = paddedNumber;
            updateInput(output);
        }
    }, 200);
}

// Update SVG Icons based on dark theme or light theme
function updateSVGIcons() {
    const isDark = document.body.classList.contains('dark');
    const filterIconUrl = isDark ? "https://gistcdn.githack.com/BlafKing/a20124cedafad23d4eecc1367ec22896/raw/04a4dae0771353377747dadf57c91d55bf841bed/filter-light.svg" : "https://gistcdn.githack.com/BlafKing/686c3438f5d0d13e7e47135f25445ef3/raw/46477777faac7209d001829a171462d9a2ff1467/filter-dark.svg";
    const searchIconUrl = isDark ? "https://gistcdn.githack.com/BlafKing/3f95619089bac3b4fd5470a986e1b3bb/raw/ebaa9cceee3436711eb560a7a65e151f1d651c6a/search-light.svg" : "https://gistcdn.githack.com/BlafKing/57573592d5857e102a4bfde852f62639/raw/aa213e9e82d705651603507e26545eb0ffe60c90/search-dark.svg";

    if (isDark) {
        
    }

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
        #refreshBtn > img,
        #refreshBtnL > img {
            content: url('${searchIconUrl}');
        }
            
        /* Gradio 4 */
        #filterBox > button:nth-child(2),
        #filterBoxL > button:nth-child(2) {
            background: url('${filterIconUrl}') no-repeat center center !important;
            background-size: 22px !important;
        }
        #filterBox > button:nth-child(2) > span,
        #filterBoxL > button:nth-child(2) > span {
            visibility: hidden;
        }
    `;
    document.head.appendChild(style);
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
    var filterButton = filterBox.children[1];
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

// Create the accordion dropdown inside the settings tab
function createAccordion(containerDiv, subfolders, name, id_name) {
    if (containerDiv == null) {
        return;
    }
    var accordionContainer = document.createElement('div'); 
    accordionContainer.id = id_name;
    accordionContainer.className = 'settings-accordion';
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
    if (subfolders && subfolders.length > 0) {
        accordionDiv.append(...subfolders);
    }
    
    accordionDiv.style.display = 'none'; // Initially hidden
    accordionContainer.appendChild(accordionDiv);
    containerDiv.appendChild(accordionContainer);
}

// Adds a button to the cards in txt2img and img2img
function createCivitAICardButtons() {
    const copyButton = document.querySelector('.copy-path-button');
    let fontSize = '1.8rem';
    if (!copyButton) {
        const editButton = document.querySelector('.edit-button');
        if (editButton) {
            const originalDisplay = editButton.parentElement.style.display;
            editButton.parentElement.style.display = 'flex';
            const editButtonBeforeStyle = window.getComputedStyle(editButton, ':before');
            fontSize = editButtonBeforeStyle.getPropertyValue('font-size');
            editButton.parentElement.style.display = originalDisplay;
        }
    }

    const checkForCardDivs = setInterval(() => {
        const cardDivs = document.querySelectorAll('.card');
        if (cardDivs.length > 0) {
            clearInterval(checkForCardDivs);
            
            cardDivs.forEach(cardDiv => {
                const buttonRow = cardDiv.querySelector('.button-row');
                if (!buttonRow) return;
                
                buttonRow.addEventListener('click', function(event) {
                    event.stopPropagation();
                });
                
                if (!buttonRow.querySelector('.goto-civitbrowser.card-button')) {
                    const modelName = cardDiv.querySelector('.actions .name')?.textContent.trim();
                    if (!modelName) return;

                    const newDiv = document.createElement('div');
                    newDiv.className = 'goto-civitbrowser card-button';
                    const svgIcon = createSVGIcon(fontSize);
                    newDiv.appendChild(svgIcon);

                    newDiv.onclick = () => modelInfoPopUp(modelName, cardDiv.parentElement.id);
                    buttonRow.insertBefore(newDiv, buttonRow.firstChild);
                }
            });
        }
    }, 200);

    setTimeout(() => {
        clearInterval(checkForCardDivs);
    }, 5000);
}

function createSVGIcon(fontSize) {
    const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgIcon.setAttribute('width', fontSize);
    svgIcon.setAttribute('height', fontSize);
    svgIcon.setAttribute('viewBox', '75 85 350 350');
    svgIcon.setAttribute('fill', 'white');
    if (fontSize == "1.8rem") {
        svgIcon.setAttribute('style', 'margin-top: -2px');
    }
    svgIcon.innerHTML = `
        <path d="M 352.79 218.85 L 319.617 162.309 L 203.704 162.479 L 146.28 259.066 L 203.434 355.786 L 319.373 355.729 L 352.773 299.386 L 411.969 299.471 L 348.861 404.911 L 174.065 404.978 L 87.368 259.217 L 174.013 113.246 L 349.147 113.19 L 411.852 218.782 L 352.79 218.85 Z"/>
        <path d="M 304.771 334.364 L 213.9 334.429 L 169.607 259.146 L 214.095 183.864 L 305.132 183.907 L 330.489 227.825 L 311.786 259.115 L 330.315 290.655 Z M 278.045 290.682 L 259.294 259.18 L 278.106 227.488 L 240.603 227.366 L 221.983 259.128 L 240.451 291.026 Z"/>
    `;

    return svgIcon;
}

function addOnClickToButtons() {
    const tabs = ['img2img_extra_tabs', 'txt2img_extra_tabs'].map(id => document.getElementById(id));
    const buttonIds = [
        'txt2img_checkpoints_extra_refresh',
        'img2img_checkpoints_extra_refresh',
        'txt2img_extra_refresh',
        'img2img_extra_refresh',
    ];

    buttonIds.forEach(buttonId => {
        let button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', (event) => {
                createCivitAICardButtons(button);
            });
        }
    });

    tabs.forEach(tab => {
        if (tab) {
            const buttons = tab.querySelectorAll('div > button:not(:first-child)');
            buttons.forEach(button => {
                button.addEventListener('click', (event) => {
                    createCivitAICardButtons(button);
                });
            });
        }
    });
}

function modelInfoPopUp(modelName=null, content_type=null, no_message=false) {
    const sendToBrowserElement = gradioApp().querySelector('#setting_civitai_send_to_browser input');
    let sendToBrowser = false;
    if (sendToBrowserElement) {
        sendToBrowser = sendToBrowserElement.checked;
    }
    if (modelName) {
        select_model(modelName, null, true, content_type, sendToBrowser);
    }
    if (sendToBrowser) {
        const tabNav = document.querySelector('.tab-nav');
        const buttons = tabNav.querySelectorAll('button');
        for (const button of buttons) {
            if (button.textContent.includes('Browser+')) {
                button.click();
                
                const firstButton = document.querySelector('#tab_civitai_interface > div > div > div > button');
                if (firstButton) {
                    firstButton.click();
                }
            }
        }
    } else {
        const createElementWithStyle = (tag, styles = {}) => {
            const el = document.createElement(tag);
            Object.assign(el.style, styles);
            return el;
        };

        const overlay = createElementWithStyle('div', {
            position: 'fixed',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(20, 20, 20, 0.95)',
            zIndex: '1001',
            overflowY: 'auto'
        });
        overlay.classList.add('civitai-overlay');
        overlay.addEventListener('keydown', handleKeyPress);
        overlay.addEventListener('click', event => {
            if (event.target === overlay) hidePopup();
        });

        const closeButton = createElementWithStyle('div', {
            zIndex: '1011',
            position: 'fixed',
            right: '22px',
            top: '0',
            cursor: 'pointer',
            color: 'white',
            fontSize: '32pt'
        });
        closeButton.classList.add('civitai-overlay-close');
        closeButton.textContent = '×';
        closeButton.addEventListener('click', hidePopup);

        const inner = createElementWithStyle('div', {
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: 'auto',
            transform: 'translate(-50%, -50%)',
            background: 'var(--neutral-950)',
            padding: '2em',
            borderRadius: 'var(--block-radius)',
            borderStyle: 'solid',
            borderWidth: 'var(--block-border-width)',
            borderColor: 'var(--block-border-color)',
            zIndex: '1001'
        });
        inner.classList.add('civitai-overlay-inner');
        
        var modelInfo;
        if (!no_message) {
            modelInfo = createElementWithStyle('div', {
                fontSize: '24px',
                color: 'white',
                fontFamily: 'var(--font)'
            });
            modelInfo.classList.add('civitai-overlay-text');
            modelInfo.textContent = 'Loading model info, please wait!';
        }

        document.body.style.overflow = 'hidden';
        document.body.appendChild(overlay);
        overlay.append(closeButton, inner);
        if (!no_message) {
            inner.appendChild(modelInfo);
        }

        setDynamicWidth(inner);
        window.addEventListener('resize', () => setDynamicWidth(inner));
    }
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
    //console.log("Last 500 characters of HTML input:", html_input.slice(-500));
    var inner = document.querySelector('.civitai-overlay-inner')
    let startIndex = html_input.indexOf("'value': '");
    if (startIndex !== -1) {
        startIndex += "'value': '".length;
        let endIndex = html_input.indexOf(", 'placeholder'", startIndex);
        if (endIndex === -1) {
            endIndex = html_input.indexOf("', 'type': None,", startIndex);
        }
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

            inner.style.top = 'unset';
            inner.style.transform = 'translate(-50%, 0%)'

            setDescriptionToggle();
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

function setDescriptionToggle() {
    const popUp = document.querySelector(".civitai-overlay-inner");
    let toggleButton = null;
    let descriptionDiv = null;

    if (popUp) {
        descriptionDiv = popUp.querySelector(".model-description");
        toggleButton = popUp.querySelector(".description-toggle-label");
    } else {
        descriptionDiv = document.querySelector(".model-description");
        toggleButton = document.querySelector(".description-toggle-label");
    }

    if (descriptionDiv && descriptionDiv.scrollHeight <= 400) {
        toggleButton.style.visibility = "hidden";
        toggleButton.style.height = "0";
        descriptionDiv.style.position = "unset";
    }
}

function submitNewSubfolder(subfolderId, subfolderValue) {
    const output = gradioApp().querySelector('#create_subfolder textarea');
    output.value = subfolderId + ".add." + subfolderValue;
    updateInput(output)
}

function deleteSubfolder(subfolderId) {
    const output = gradioApp().querySelector('#create_subfolder textarea');
    output.value = subfolderId + ".delete.";
    updateInput(output)
}

function createCustomSubfolder(subfolderDiv, subfolderId, subfolderValue) {
    if (typeof subfolderId === 'undefined') {
        console.error('subfolderId is required.');
        return;
    }

    const newContainerDiv = document.createElement("div");
    newContainerDiv.classList.add("svelte-1f354aw", "container", "CivitDefaultSubfolder");
    newContainerDiv.style.display = "flex";
    newContainerDiv.style.alignItems = "center";

    newContainerDiv.setAttribute("subfolder_id", subfolderId);

    const newTextArea = document.createElement("textarea");
    newTextArea.setAttribute("data-testid", "textbox");
    newTextArea.classList.add("scroll-hide", "svelte-1f354aw");
    newTextArea.setAttribute("dir", "ltr");
    newTextArea.setAttribute("placeholder", "{BASEMODEL}/{NSFW}/{AUTHOR}/{MODELNAME}/{MODELID}/{VERSIONNAME}/{VERSIONID}");
    newTextArea.setAttribute("rows", "1");
    newTextArea.style.overflowY = "scroll";
    newTextArea.style.height = "42px";
    newTextArea.style.flex = "1";

    if (typeof subfolderValue !== 'undefined') {
        newTextArea.value = subfolderValue;
    }

    newTextArea.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            submitNewSubfolder(subfolderId, newTextArea.value);
        }
    });

    const saveButton = document.createElement("button");
    saveButton.textContent = "Save";
    saveButton.classList.add("save-button", "lg", "primary", "gradio-button", "svelte-cmf5ev");
    saveButton.setAttribute("title", "")
    saveButton.style.marginRight = "10px";
    saveButton.addEventListener("click", function() {
        submitNewSubfolder(subfolderId, newTextArea.value);
    });

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.classList.add("delete-button", "lg", "primary", "gradio-button", "svelte-cmf5ev");
    deleteButton.style.marginRight = "10px";
    deleteButton.addEventListener("click", function() {
        deleteSubfolder(subfolderId);
        newContainerDiv.remove();
    });

    newContainerDiv.appendChild(deleteButton);
    newContainerDiv.appendChild(saveButton);
    newContainerDiv.appendChild(newTextArea);

    subfolderDiv.appendChild(newContainerDiv);
}

function insertExistingSubfolders(input) {
    const subfolder = document.querySelectorAll("civitai-custom-subfolder-div");
    createCustomSubfolder(subfolder, Id, Value);
}

function createSubfolderButton() {
    const subfolderParent = document.getElementById("create-sub-accordion");
    const subfolderDiv = subfolderParent.querySelector(".accordion");
    
    const subfolder = document.createElement("div");
    subfolder.classList.add("flex-column-layout", "civitai-custom-subfolder-div");

    const customSubfoldersList = document.querySelector('#custom_subfolders_list');
    const textarea = customSubfoldersList.querySelector('textarea');
    const subfoldersString = textarea ? textarea.value : '';

    const subfoldersArray = subfoldersString.split('␞␞');

    for (let i = 0; i < subfoldersArray.length; i += 2) {
        const subfolderId = subfoldersArray[i];
        const subfolderValue = subfoldersArray[i + 1];

        createCustomSubfolder(subfolder, subfolderId, subfolderValue);
    }

    const buttonContainer = document.createElement("div");
    buttonContainer.classList.add("sub-folder-button-container");
    buttonContainer.style.display = "flex";
    buttonContainer.style.gap = "10px";
    
    const optionsDiv = document.createElement("div");
    optionsDiv.classList.add("placeholder-options-container");
    optionsDiv.style.display = "flex";
    optionsDiv.style.justifyContent = "center";

    const plusButton = document.createElement("button");
    plusButton.textContent = "Create new default sub folder entry";
    plusButton.classList.add("plus-button", "lg", "primary", "gradio-button", "svelte-cmf5ev");
    plusButton.style.marginTop = "10px";
    plusButton.addEventListener("click", function() {
        const existingSubfolderDivs = document.querySelectorAll("div.CivitDefaultSubfolder");
        let highestSubfolderId = 0;

        existingSubfolderDivs.forEach((div) => {
            const subfolderId = parseInt(div.getAttribute('subfolder_id'), 10);
            if (subfolderId > highestSubfolderId) {
                highestSubfolderId = subfolderId;
            }
        });

        const newSubfolderId = highestSubfolderId + 1;
        createCustomSubfolder(subfolder, newSubfolderId);
    });

    // Create the guide button
    const guide_html = `
    <div style="text-align: center;">
        <div>These options can be used to add sub-folder options.</div>
        <div>There are a few placeholders you can use which will be automatically replaced with the selected model's information:</div>
        <div>‎</div>
        <div>{BASEMODEL}: Replaced with the base model name.</div>
        <div>{NSFW}: Creates a folder named "nsfw", folder will not be created if model is sfw.</div>
        <div>{AUTHOR}: Replaced with the author of the model.</div>
        <div>{MODELNAME}: Replaced with the name of the model.</div>
        <div>{MODELID}: Replaced with the unique ID of the model.</div>
        <div>{VERSIONNAME}: Replaced with the version name of the model.</div>
        <div>{VERSIONID}: Replaced with the unique ID of the model version.</div>
        <div>‎</div>
        <div>For example, if I select a model called 'ReV Animated'</div>
        <div>and it's version is called 'V2 Rebirth' then the following:</div>
        <div>{MODELNAME}/{VERSIONNAME}</div>
        <div>Will be replaced with:</div>
        <div>ReV Animated/V2 Rebirth</div>
        <div>‎</div>
        <div>Always use '/' as a seperator, regardless of your OS</div>
    </div>
    `;
    const guideButton = document.createElement("button");
    guideButton.textContent = "Guide";
    guideButton.classList.add("guide-button", "lg", "primary", "gradio-button", "svelte-cmf5ev");
    guideButton.style.marginTop = "10px";
    guideButton.addEventListener("click", function() {
        modelInfoPopUp(null, null, true);
        insertGuideMessage(guide_html);
    });

    const optionsText = document.createElement("span");
    optionsText.textContent = "Available options: {BASEMODEL} {NSFW} {AUTHOR} {MODELNAME} {MODELID} {VERSIONNAME} {VERSIONID}";

    // Append buttons to the container
    buttonContainer.appendChild(guideButton);
    buttonContainer.appendChild(plusButton);

    optionsDiv.appendChild(optionsText);

    subfolder.insertBefore(optionsDiv, subfolder.firstChild);
    subfolder.insertBefore(buttonContainer, subfolder.firstChild);
    subfolderDiv.appendChild(subfolder);
}

function insertGuideMessage(html_input) {
    const overlayContainer = document.querySelector(".civitai-overlay-inner");
    if (overlayContainer) {
        const guideHtml = document.createElement('div');
        guideHtml.innerHTML = html_input;
        while (guideHtml.firstChild) {
            overlayContainer.appendChild(guideHtml.firstChild);
        }
    }
}

// Runs all functions when the page is fully loaded
function onPageLoad() {
    updateSVGIcons();

    let subfolderDiv = document.querySelector("#settings_civitai_browser_plus > div > div");
    let downloadDiv = document.querySelector("#settings_civitai_browser_download > div > div");
    let settingsDiv = document.querySelector("#settings_civitai_browser > div > div");

    if (subfolderDiv || downloadDiv) {
        let div = subfolderDiv || downloadDiv;
        let subfolders = div.querySelectorAll("[id$='subfolder']");
        createAccordion(div, subfolders, "Default sub folders", 'default-sub-accordion');
        createAccordion(div, null, "Create sub folder entries", 'create-sub-accordion');
        createSubfolderButton();
    }

    if (subfolderDiv || settingsDiv) {
        let div = subfolderDiv || settingsDiv;
        let proxy = div.querySelectorAll("[id$='proxy']");
        createAccordion(div, proxy, "Proxy options", 'proxy-accordion');
    }

    let toggle4L = document.getElementById('toggle4L');
    let toggle4 = document.getElementById('toggle4');
    let hash_toggle_hover = document.querySelector('#skip_hash_toggle > label');
    let hash_toggle = document.querySelector('#skip_hash_toggle');

    if (toggle4L || toggle4) {
        let like_toggle = toggle4L || toggle4;
        let insertText = 'Requires an API Key\nConfigurable in CivitAI settings tab';
        createTooltip(like_toggle, like_toggle, insertText);
    }

    if (hash_toggle) {
        let insertText = 'This option generates unique hashes for models that were not downloaded with this extension.\nA hash is required for any of the options below to work, a model with no hash will be skipped.\nInitial hash generation is a one-time process per file.';
        createTooltip(hash_toggle, hash_toggle_hover, insertText);
    }

    addOnClickToButtons();
    createCivitAICardButtons();
    adjustFilterBoxAndButtons();
    setupClickOutsideListener();
    updateBackToTopVisibility([{isIntersecting: false}]);
}

onUiLoaded(onPageLoad);

function checkSettingsLoad() {
    const divElement = gradioApp().querySelector('#setting_custom_api_key');
    const infoElement = divElement?.querySelector('.info');
    if (!infoElement) {
        return;
    }
    clearInterval(settingsLoadInterval);
    createLink(infoElement);
}
let settingsLoadInterval = setInterval(checkSettingsLoad, 1000);