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
            console.error('Unknown suffix', suffix);
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
function createTooltipOnHover() {
    const toggle4L = document.getElementById('toggle4L');
    const toggle4 = document.getElementById('toggle4');

    if (toggle4L || toggle4) {
        const targetElement = toggle4L || toggle4;

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = 'Requires an API Key\nConfigurable in CivitAI settings tab';
        tooltip.style.cssText = 'display: none; text-align: center; white-space: pre;';

        targetElement.addEventListener('mouseover', () => {
            tooltip.style.display = 'block';
        });

        targetElement.addEventListener('mouseout', () => {
            tooltip.style.display = 'none';
        });

        targetElement.appendChild(tooltip);
    }
}

// Changes the Tab title
function changeTabTitle() {
    const tabElement = document.getElementById('rc-tabs-0-tab-tab_civitai_interface');
    if (tabElement) {
        tabElement.textContent = 'CivitAI Browser+';
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

    const existingText = "(You can create your own API key in your CivitAI account settings, Requires UI reload)";
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

    const hasMatchingButtonName = validButtonNames.some(buttonName =>
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

                    const metaDataButton = buttonRow.querySelector('.metadata-button.card-button')

                    const newDiv = document.createElement('div');
                    newDiv.classList.add('goto-civitbrowser', 'card-button');
                    newDiv.addEventListener('click', function (event) {
                        event.stopPropagation();
                        sendModelToBrowser(modelName, content_type);
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
                    }
                    svgIcon.setAttribute('viewBox', '75 0 500 500');
                    svgIcon.setAttribute('fill', 'white');

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

function sendModelToBrowser(modelName, content_type) {
    const tabNav = document.querySelector('.tab-nav');
    const buttons = tabNav.querySelectorAll('button');
    for (const button of buttons) {
        if (button.textContent.includes('Civitai')) {
            button.click();
            
            const firstButton = document.querySelector('#tab_civitai_interface > div > div > div > button');
            if (firstButton) {
                firstButton.click();
            }
        }
    }
    select_model(modelName, null, true, content_type);
}

var selectedModels = [];
function multi_model_select(modelName, isChecked) {
    if (arguments.length === 0) {
        selectedModels = [];
        return;
    }
    if (isChecked) {
        if (!selectedModels.includes(modelName)) {
            selectedModels.push(modelName);
        }
    } else {
        var index = selectedModels.indexOf(modelName);
        if (index > -1) {
            selectedModels.splice(index, 1);
        }
    }
    const output = gradioApp().querySelector('#selected_list textarea');
    output.value = JSON.stringify(selectedModels);
    updateInput(output);
}

// Clicks the first item in the browser cards list
function clickFirstFigureInColumn() {
    const columnDiv = document.querySelector('.column.civmodellist');
    if (columnDiv) {
        const firstFigure = columnDiv.querySelector('figure');
        if (firstFigure) {
            firstFigure.click();
        }
    }
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

function selectAllModels() {
    const checkboxes = Array.from(document.querySelectorAll('.model-checkbox'));
    const allChecked = checkboxes.every(checkbox => checkbox.checked);
    const allUnchecked = checkboxes.every(checkbox => !checkbox.checked);

    if (allChecked || allUnchecked) {
        checkboxes.forEach(clickCheckbox);
    } else {
        checkboxes.filter(checkbox => !checkbox.checked).forEach(clickCheckbox);
    }

    function clickCheckbox(checkbox) {
        const clickEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true
        });
        checkbox.dispatchEvent(clickEvent);
    }
}

function deselectAllModels() {
    setTimeout(() => {
        const checkboxes = Array.from(document.querySelectorAll('.model-checkbox'));
        checkboxes.filter(checkbox => checkbox.checked).forEach(uncheckCheckbox);
        function uncheckCheckbox(checkbox) {
            const clickEvent = new MouseEvent('click', {
                view: window,
                bubbles: true,
                cancelable: true
            });
            checkbox.dispatchEvent(clickEvent);
        }
    }, 1000);
}

// Runs all functions when the page is fully loaded
function onPageLoad() {
    const divElement = document.getElementById('setting_custom_api_key');
    var civitaiDiv = document.getElementById('civitai_preview_html');
    const infoElement = divElement?.querySelector('.info');
    if (!infoElement) {
        return;
    }

    var subfolderDiv = document.querySelector("#settings_civitai_browser_plus > div > div");
    var subfolders = subfolderDiv.querySelectorAll("[id$='subfolder']");

    createAccordion(subfolderDiv, subfolders, "Default sub folders");

    var upscalerDiv = document.querySelector("#settings_civitai_browser_plus > div > div > #settings-accordion > div");
    var upscalers = upscalerDiv.querySelectorAll("[id$='upscale_subfolder']");

    createAccordion(upscalerDiv, upscalers, "Upscalers");

    observer.observe(civitaiDiv);
    clearInterval(intervalID);
    updateSVGIcons();
    adjustFilterBoxAndButtons();
    createTooltipOnHover();
    changeTabTitle();
    setupClickOutsideListener();
    createLink(infoElement);
    updateBackToTopVisibility([{isIntersecting: false}]);
}

// Checks every second if the page is fully loaded
let intervalID = setInterval(onPageLoad, 1000);