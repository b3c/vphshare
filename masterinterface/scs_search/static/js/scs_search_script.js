/**
 * Created with PyCharm.
 * Date: 20/11/12
 * Time: 14.46
 * To change this template use File | Settings | File Templates.
 */


function automaticSearchCall ( )
{
    var form = $( "#automaticSearchForm" );
    var input = form.find( 'input[name="freeText"]' ).val();
    var url = '/automatic_search/'

    $.ajax({
        type : 'POST',
        url : url,
        data : {input : input
            },
        success: function( results ) {
                alert(results[0]['concept_uri']);
            },
        error: function (error) {
            alert(error);
            }
        });
}