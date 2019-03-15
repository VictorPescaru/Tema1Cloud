window.addEventListener("load", function () {

	var form = document.forms.namedItem("search");
	addListener(form);
	
	function addListener(form) {
		form.addEventListener("submit", function (event) {
			event.preventDefault();		
			var json = toJSONString(this); 
			sendData(json);
			
		}, false);
	}

	function sendData(data) {
		var XHR = new XMLHttpRequest();
			
		XHR.addEventListener("load", function(event) {
			window.open("").document.write(XHR.responseText);

		});

		XHR.addEventListener("error", function(event) {
			alert('Oops! Something went wrong.');
		});

		
		XHR.open("POST", "/search");
		XHR.setRequestHeader("Content-Type", "application/json");
		console.log(data);
		XHR.send(data);
	}

	function toJSONString( form ) {
		var obj = {};
		var elements = form.querySelectorAll( "input, select, textarea" );
		for( var i = 0; i < elements.length; ++i ) {
			var element = elements[i];
			var name = element.name;
			var value = element.value;

			if( name && value) {
				obj[ name ] = value;
			}
		
		}

		return JSON.stringify( obj );
	}
	

})
