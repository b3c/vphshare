jQuery(document).ready(function() {
	$('#fileupload').fileupload({
		start: function(e, data) {
			jQuery('#progress').removeClass('fade');
		},
		done: function(e, data) {
			jQuery('#progress').addClass('fade');
			window.location = window.location.pathname;
		},
		progressall: function(e, data) {
			var progress = parseInt(data.loaded / data.total * 100, 10);
			jQuery('#progress .bar').css('width', progress + '%');
		}
	});
});