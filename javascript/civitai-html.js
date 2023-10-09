"use strict";

function select_model(model_name) {
	let model_dropdown = gradioApp().querySelector('#eventtext1 textarea');
	if (model_dropdown && model_name) {
		let randomNumber = Math.floor(Math.random() * 1000);
		let paddedNumber = String(randomNumber).padStart(3, '0');
		model_dropdown.value = model_name + "." + paddedNumber;
		updateInput(model_dropdown)
	}
}

function updateCardSize(width, height) {
    var styleSheet = document.styleSheets[0];
    var dimensionsKeyframes = `width: ${width}em !important; height: ${height}em !important;`;
    
    var fontSize = (width / 8) * 100;
    var textKeyframes = `font-size: ${fontSize}% !important;`;

    addOrUpdateRule(styleSheet, '.civmodelcard img', dimensionsKeyframes);
    addOrUpdateRule(styleSheet, '.civmodelcard .video-bg', dimensionsKeyframes);
    addOrUpdateRule(styleSheet, '.civmodelcard figcaption', textKeyframes);
}

function toggleNSFWContent(hideAndBlur) {
    const sheet = document.styleSheets[0];

    if (!hideAndBlur) {
        addOrUpdateRule(sheet, '.civcardnsfw', 'display: none;');
        addOrUpdateRule(sheet, '.civnsfw img', 'filter: blur(10px);');
    }
    else {
        addOrUpdateRule(sheet, '.civcardnsfw', 'display: block;');
        addOrUpdateRule(sheet, '.civnsfw img', 'filter: none;');
    }

    const dateSections = document.querySelectorAll('.date-section');
    dateSections.forEach((section) => {
        const cards = section.querySelectorAll('.civmodelcard');
        const nsfwCards = section.querySelectorAll('.civmodelcard.civcardnsfw');

        if (!hideAndBlur && cards.length === nsfwCards.length) {
            section.style.display = 'none';
        } else {
            section.style.display = 'block';
        }
    });
}

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

document.addEventListener('keydown', function(e) {
    var handled = false;

    // Check for the combination of "Enter" key along with Ctrl, Alt, or Meta (Cmd on Mac)
    if (e.key !== undefined) {
        if ((e.key == "Enter" && (e.metaKey || e.ctrlKey || e.altKey))) handled = true;
    } else if (e.keyCode !== undefined) {
        if ((e.keyCode == 13 && (e.metaKey || e.ctrlKey || e.altKey))) handled = true;
    }

    if (handled) {
        // Check if the extension's tab is the currently active tab
        var currentTabContent = get_uiCurrentTabContent();
        if (currentTabContent && currentTabContent.id === "tab_civitai_interface") {

            // Find the refresh button within the current tab content and click it
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
    if (!element) {
        return;
    }

    const childDiv = element.querySelector("div:nth-child(3)");
    if (!childDiv) {
        return;
    }

    if (window.innerWidth >= 1250) {
        childDiv.style.marginLeft = "0px";  // Reset margin-left when width is >= 1250
        element.style.justifyContent = "center";
    } else if (window.innerWidth < 1250 && window.innerWidth > 915) {
        const marginLeftValue = 1250 - window.innerWidth;
        childDiv.style.marginLeft = `${marginLeftValue}px`;
        element.style.justifyContent = "center";
    } else if (window.innerWidth <= 915) {
        childDiv.style.marginLeft = "0px";  // Reset margin-left when width is <= 915
        element.style.justifyContent = "flex-start";
    }

    // Reference to the buttons and divs
    const pageBtn1 = document.querySelector("#pageBtn1");
    const pageBtn2 = document.querySelector("#pageBtn2");
    const pageBox = document.querySelector("#pageBox");
    const pageBoxMobile = document.querySelector("#pageBoxMobile");
    
    // Move the buttons based solely on viewport width
    if (window.innerWidth < 500) {
        childDiv.style.width = "300px";
        // Move the buttons to pageBoxMobile
        if (pageBoxMobile) {
            if (pageBtn1) {
                pageBoxMobile.appendChild(pageBtn1);
            }
            if (pageBtn2) {
                pageBoxMobile.appendChild(pageBtn2);
            }
        }
    } else {
        childDiv.style.width = "375px";
        // Move the buttons back to pageBox
        if (pageBox) {
            // Ensure pageBtn1 is the first child
            if (pageBtn1) {
                pageBox.insertBefore(pageBtn1, pageBox.firstChild);
            }
            // Append pageBtn2 to ensure it's the last child
            if (pageBtn2) {
                pageBox.appendChild(pageBtn2);
            }
        }
    }
}

// Calls the function above whenever the window is resized
window.addEventListener("resize", adjustFilterBoxAndButtons);

// Function to trigger refresh button with extra checks for page slider
function pressRefresh() {
    setTimeout(() => {
        // Check if the user is currently typing in the specified input
        const input = document.querySelector("#pageSlider > div:nth-child(2) > div > input");
        if (document.activeElement === input) {
            // Attach an event listener to detect the 'Enter' key press
            input.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.keyCode === 13) {
                    // If 'Enter' key is detected, blur the input to make it inactive
                    input.blur();
                }
            });

            // Attach an event listener to detect if the input gets blurred
            input.addEventListener('blur', function() {
                return; // If input is blurred (either by user or programmatically), return from the function
            });

            return; // Exit the function if the user is typing
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
    }, 200); // Delay of 200 milliseconds
}

// Update SVG Icons based on dark theme or light theme
function updateSVGIcons() {
    // Check if body has class "dark" and set appropriate SVG Icons
    const isDark = document.body.classList.contains('dark');
    const filterIconUrl = isDark ? "https://svgur.com/i/y93.svg" : "https://svgur.com/i/yBY.svg";
    const searchIconUrl = isDark ? "https://svgur.com/i/y9S.svg" : "https://svgur.com/i/y8H.svg";

    const element = document.querySelector("#filterBox") || document.querySelector("#filterBoxL");
    const childDiv = element.querySelector("div:nth-child(3)");

    if (childDiv) {
        const boxShadowValue = isDark ? 'box-shadow: #ffffff 0px 0px 2px 0px; display: none;' : 'box-shadow: #000000 0px 0px 2px 0px; display: none;';
        childDiv.style.cssText = boxShadowValue;
    }

    // Update filter SVG
    const style = document.createElement('style');
    style.innerHTML = `
        #filterBox > div:nth-child(2) > span:nth-child(2)::before, 
        #filterBoxL > div:nth-child(2) > span:nth-child(2)::before {
            background: url('${filterIconUrl}') no-repeat center center;
            background-size: contain;
        }
    `;
    document.head.appendChild(style);

    // Update search SVG
    const refreshBtn = document.querySelector("#refreshBtn");
    const refreshBtnL = document.querySelector("#refreshBtnL");
    let targetSearchElement;

    if (refreshBtn && refreshBtn.firstChild) {
        targetSearchElement = refreshBtn.firstChild;
    } else if (refreshBtnL && refreshBtnL.firstChild) {
        targetSearchElement = refreshBtnL.firstChild;
    }
    if (targetSearchElement) {
        targetSearchElement.src = searchIconUrl;
    }
}

function onPageLoad() {
    // The tab element which exists if page is done loading
    const targetButton = document.querySelector("#tab_civitai_interface");

    // If the target tab doesn't exist yet, retry after 1 second
    if (!targetButton) {
        return;
    }

    // If the tab is found, clear the interval
    clearInterval(intervalID);

    updateSVGIcons();
    adjustFilterBoxAndButtons();
}

// Start the observer on page load and retry every second until successful
let intervalID = setInterval(onPageLoad, 1000);