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
    var imgKeyframes = `width: ${width}em !important; height: ${height}em !important;`;
    
    var fontSize = (width / 8) * 100;
    var textKeyframes = `font-size: ${fontSize}% !important;`;

    addOrUpdateRule(styleSheet, '.civmodelcard img', imgKeyframes);
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

function filterByBaseModel(selectedBaseModels) {
    if (!selectedBaseModels || selectedBaseModels.length === 0) {
        document.querySelectorAll('.civmodelcard').forEach(card => {
            card.style.opacity = '1';
        });
        return;
    }

    if (!Array.isArray(selectedBaseModels)) {
        selectedBaseModels = [selectedBaseModels];
    }

    document.querySelectorAll('.civmodelcard').forEach(card => {
        const cardBaseModel = card.getAttribute('base-model');
        let shouldDisplay = false;

        for (let i = 0; i < selectedBaseModels.length; i++) {
            if (cardBaseModel === selectedBaseModels[i]) {
                shouldDisplay = true;
                break;
            }

            if (selectedBaseModels[i] === "SD 2.0" && (cardBaseModel === "SD 2.0" || cardBaseModel === "SD 2.0 768")) {
                shouldDisplay = true;
                break;
            }

            if (selectedBaseModels[i] === "SD 2.1" && ["SD 2.1", "SD 2.1 768", "SD 2.1 Unclip"].includes(cardBaseModel)) {
                shouldDisplay = true;
                break;
            }
        }

        card.style.opacity = shouldDisplay ? '1' : '0.1';
    });
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
            if (refreshButton) {
                refreshButton.click();
            }

            e.preventDefault();
        }
    }
});
