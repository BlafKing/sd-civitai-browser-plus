"use strict";

// Selects a model by pressing on card
function select_model(model_name) {
    var civitaiDiv = document.getElementById('civitai_preview_html');
	let model_dropdown = gradioApp().querySelector('#eventtext1 textarea');
	if (model_dropdown && model_name) {
		let randomNumber = Math.floor(Math.random() * 1000);
		let paddedNumber = String(randomNumber).padStart(3, '0');
		model_dropdown.value = model_name + "." + paddedNumber;
		updateInput(model_dropdown);
        observer.unobserve(civitaiDiv);
        observer.observe(civitaiDiv);
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
            if (onclickAttr && onclickAttr.includes(`select_model('${modelName}')`)) {
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
function createAccordion() {
    var containerDiv = document.querySelector("#settings_civitai_browser_plus > div > div");
    var subfolders = containerDiv.querySelectorAll("[id$='subfolder']");
    if (containerDiv == null || subfolders.length == 0) {
        return;
    }
    var accordionContainer = document.createElement('div'); 
    accordionContainer.id = 'settings-accordion';
    var toggleButton = document.createElement('button');
    toggleButton.id = 'accordionToggle';
    toggleButton.innerHTML = 'Default sub folders<div style="transition: transform 0.15s; transform: rotate(90deg)">▼</div>';
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

// Runs all functions when the page is fully loaded
function onPageLoad() {
    const divElement = document.getElementById('setting_custom_api_key');
    var civitaiDiv = document.getElementById('civitai_preview_html');
    const infoElement = divElement?.querySelector('.info');
    if (!infoElement) {
        return;
    }

    observer.observe(civitaiDiv);
    clearInterval(intervalID);
    updateSVGIcons();
    adjustFilterBoxAndButtons();
    createTooltipOnHover();
    changeTabTitle();
    setupClickOutsideListener();
    createLink(infoElement);
    updateBackToTopVisibility([{isIntersecting: false}]);
    createAccordion();
}

// Checks every second if the page is fully loaded
let intervalID = setInterval(onPageLoad, 1000);