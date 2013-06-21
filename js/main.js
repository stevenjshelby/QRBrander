$(document).ready( function() {
        var validupload = false;

	$("#genBtn").click(function(e) {
		e.preventDefault();
		submitData();
	});

	function submitData() {
                if (validupload == true) {
                    if ($("#qrdata").val() == "") {
 			alert("Please submit data to encode!");
  		    }
		    else {
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
                }
                else {
		    alert("You have not uploaded a valid file.");
                }
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
        
        var file = document.getElementById('logofile');

        file.onchange = function(e){
            var ext = this.value.match(/\.([^\.]+)$/)[1];
            switch(ext)
            {
                case 'png':
                    //only allow png
                    validupload = true;
                    break;
                default:
                    alert('Sorry. Only PNG is allowed.');
                    validupload = false;
                                 
            }
        };

});
