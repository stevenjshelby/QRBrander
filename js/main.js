$(document).ready( function() {

	$("#genBtn").click(function(e) {
		e.preventDefault();
		submitData();
	});

	function submitData() {
		var file = document.getElementById('logofile').files[0]; //Files[0] = 1st file
		var reader = new FileReader();

		reader.readAsDataURL(file);
		reader.onload = shipOff;
		//reader.onloadstart = ...
		//reader.onprogress = ...
		//reader.onabort = ...
		//reader.onerror = ...
		//reader.onloadend = ...
	}

	function shipOff(event) {
	    var result = event.target.result;
	    var fileName = document.getElementById('logofile').files[0].name; //Should be 'picture.jpg'
	    $.ajax({
	    	type: "POST",
	    	url: "server/qrgen.php",
	    	data: {
	    		filedata: result,
		    	filename: fileName,
		    	qrdata: $("#qrdata").val()
		   	},
		   	success: function(result) {
		   		var jsonresult = $.parseJSON(result);
		   		var brandedFile = jsonresult.serverBranded;

		   		$("#result-container").html("<img id='brandedImg' src='server/branded/" + brandedFile + "'>");
		   	}
	    });
	}

});