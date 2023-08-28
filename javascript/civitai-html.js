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

    styleSheet.insertRule(`.civmodelcard img { ${imgKeyframes} }`, styleSheet.cssRules.length);
    styleSheet.insertRule(`.civmodelcard figcaption { ${textKeyframes} }`, styleSheet.cssRules.length);
}
