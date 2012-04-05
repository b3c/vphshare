$(document).ready(function() {
	pm.bind("resizeEvent", function(data) {
		if($('#cloudmanagerframe')) {
			$('#cloudmanagerframe').css('height', data['size'] + 'px');
		}
		
		if($('#datamanagerframe')) {
			$('#datamanagerframe').css('height', data['size'] + 'px');
		}
	});
});