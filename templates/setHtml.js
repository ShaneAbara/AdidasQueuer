function setHTML (html) {
	document.body.insertAdjacentHTML('beforeEnd', html);
	var range = document.createRange();
	range.setStartAfter(document.body.lastChild);
	document.documentElement.innerHTML = '';
	var docFrag = range.createContextualFragment(html);
	document.body.appendChild(docFrag);
}

setHTML("{{ html }}")