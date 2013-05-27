$(document).ready(function() {
	pm.bind("resizeEvent", function(data) {
		if($('#cloudmanagerframe')) {
			$('#cloudmanagerframe').css('height', data['size'] + 'px');
		}

		if($('#datamanagerframe')) {
			$('#datamanagerframe').css('height', data['size'] + 'px');
		}

		if($('#policymanagerframe')) {
			$('#policymanagerframe').css('height', data['size'] + 'px');
		}
	});

	$('.has_left_tooltip').tooltip({placement: 'left'});
	$('.has_right_tooltip').tooltip({placement: 'right'});
});