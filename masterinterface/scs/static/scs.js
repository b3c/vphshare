


function defaultAjaxResponseHandler( responseText, statusText, xhr, jqform ) {
    alert(responseText);
    alert(jqform);
    var div = $(jqform).attr("rel");
    $(div).empty();
    $(responseText).appendTo( div );
}

$(document).ready(
    function(){

        // highlight current section
        var thereIsASection = false;
        $('nav li[id!="navhome"] a').each(
            function(){
                if ( document.URL.match($(this).attr("href")) ){
                    $(this).parent().toggleClass("current-menu-item");
                    thereIsASection = true;
                }
            }
        );
        if (thereIsASection){ $("#navhome").removeClass("current-menu-item");}

        //create if not exist overlay div
        if ( $("#overlay").length == 0 ) {

            $(document.createElement("div"))
                .attr("id", "overlay")
                .addClass("overlay")
                .append(
                    $(document.createElement("div"))
                    .addClass("contentWrap")
                )
                .appendTo( $("body") );
        }

        //create if not exist login iframes
        $(".login").each(
            function(){
                var iframe_id = $(this).attr("id") + "iframe";
                var src = $(this).attr("href");
                $(this).attr("rel", "#"+iframe_id);
                $(document.createElement("iframe"))
                    .attr("id", iframe_id)
                    .addClass("overlay")
                    .attr("src", src)
                    .css("overflow-y","hidden")

                .appendTo( $("body") );

            }
        );
        if ( $("#loginiframe").length == 0 ) {


        }

        // set up overlay elements
        $(".popup[rel]").overlay({
            closeOnClick: true,
            closeOnEsc: true,

            onBeforeLoad: function() {
                // grab wrapper element inside content
                var wrap = this.getOverlay().find(".contentWrap");
                // load the page specified in the trigger
                wrap.load(this.getTrigger().attr("href"));
            },
            onClose: function(){
                location.replace('/');
            }
        });



        // set up default ajax form behaviour
        $('.ajax').submit(
            function(event){

                // stop form from submitting normally
                event.preventDefault();

                // submit parameters
                var url = $(this).attr( "action" );
                var method = $(this).attr("method") || "get"; // default method get
                var data = $(this).find(":input").serializeArray();

                // create response div
                var responseDiv = $(document.createElement("div"));
                // append responseDiv afterthe form
                $(this).after( responseDiv );

                $.ajax({
                        type: method,
                        url: url,
                        data: data,
                        context: $(responseDiv),
                        success: function(data){
                            $("#statusmessage").empty().text("Form submitted");
                            $(this).empty().html( data );
                        }
                    }
                );

            }
        );

    }
);


//ajax request//
function users_create_role(){

    if ( $("#users_create_roleLOADIMG").hasClass( "invisible" ) ){
        $("#users_create_roleLOADIMG").removeClass("invisible");
    }

    var form = $("#users_create_role");
    var data = form.serializeArray();
    var url = $( form ).attr( 'action' );

    $.ajax({
            type: 'POST',
            url : url,
            data: data,
            success: users_create_roleResponseHandler
        }
    );

}

function users_create_roleResponseHandler(responseText, statusText, xhr, jqform){
    // example of overriding the expires and speed options for one notification

    $("#users_create_roleLOADIMG").addClass("invisible");
    if (responseText == "TRUE"){
        $("#statusmessage").empty().text("Role Created");
        $('#statusmessage').fadeIn().delay(2000).fadeOut('slow');
    }else{
        $("#errormessage").empty().text("Some error occurred");
        $('#errormessage').fadeIn().delay(2000).fadeOut('slow');
    }

    loadRoleMap();
}

function loadRoleMap(){

    if ( $("#users_update_role_mapLOADIMG").hasClass( "invisible" ) ){
        $("#users_update_role_mapLOADIMG").removeClass("invisible");
        $("#usersList").addClass("invisible");
    }

    var form = $("#users_update_role_map");
    var csrfmiddlewaretoken = $( form ).find( 'input[name="csrfmiddlewaretoken"]' ).val();
    var url = $( form ).attr( 'action' );

    $.ajax({
            type: 'GET',
            url : url,
            data: {csrfmiddlewaretoken: csrfmiddlewaretoken},
            success: loadRoleMapResponseHandler
        }
    );

}
function loadRoleMapResponseHandler(responseText, statusText, xhr, jqform){

    var div = $("#usersList");
    $(div).empty();
    $(responseText).appendTo( div );
    $("#users_update_role_mapLOADIMG").addClass("invisible");
    $(div).removeClass("invisible");

}

function users_update_role_map(){

    if ( $("#users_update_role_mapLOADIMG").hasClass( "invisible" ) ){
        $("#users_update_role_mapLOADIMG").removeClass("invisible");
        $("#usersList").addClass("invisible");
    }

    var form = $("#users_update_role_map");
    //var data = form.serializeArray();
    var csrfmiddlewaretoken = form.find( 'input[name="csrfmiddlewaretoken"]' ).val();
    var data = form.find('input:checkbox').map(function() {
        return { name: this.name, value: this.checked ? this.value : "false" };
    });
    var url = $( form ).attr( 'action' );

    data.push({ name: 'csrfmiddlewaretoken', value: csrfmiddlewaretoken });
    $.ajax({
            type: 'POST',
            url : url,
            data: data,
            success: users_update_role_mapResponseHandler
        }
    );

}
function users_update_role_mapResponseHandler(responseText, statusText, xhr, jqform){

    if (responseText == "TRUE"){
        $("#statusmessage").empty().text("Role update complete");
        $('#statusmessage').fadeIn().delay(2000).fadeOut('slow');
    }else{
        $("#errormessage").empty().text("Some error occurred");
        $('#errormessage').fadeIn().delay(2000).fadeOut('slow');
    }
    loadRoleMap();

}

function users_access_search(mail){


    if ( $("#users_access_searchLOADIMG").hasClass( "invisible" ) ){
        $("#users_access_searchLOADIMG").removeClass("invisible");
        //$("#usersList").addClass("invisible");
    }

    var form = $("#users_access_search");
    var data = form.serializeArray();
    var url = $( form ).attr( 'action' );

    if (typeof mail !== 'undefined'){
        data['email']=mail;
    }
    $.ajax({
            type: 'POST',
            url : url,
            data: data,
            success: users_access_searchResponseHandler
        }
    );

}
function users_access_searchResponseHandler(responseText, statusText, xhr, jqform){
    if (responseText == 'FALSE') {
        $("#errormessage").empty().text("No user find");
        $('#errormessage').fadeIn().delay(2000).fadeOut('slow');

    }else{
        var list = $(".tableuserlits");
        $(responseText).appendTo( list);
    }
    //var div = $("#usersList");
    $("#users_access_searchLOADIMG").addClass("invisible");
    $("#users_update_role_mapLOADIMG").addClass("invisible");
    //$(div).removeClass("invisible");

}


function users_remove_role(action, role){

    if ( $("#users_create_roleLOADIMG").hasClass( "invisible" ) ){
        $("#users_create_roleLOADIMG").removeClass("invisible");
    }

    var form = $("#users_remove_role");
    var csrfmiddlewaretoken = form.find( 'input[name="csrfmiddlewaretoken"]' ).val();
    var data = form.serializeArray();
    var url = action

    $.ajax({
            type: 'POST',
            url : url,
            data: {csrfmiddlewaretoken:csrfmiddlewaretoken,
                    role_name:role},
            success: users_remove_roleResponseHandler
        }
    );

}

function users_remove_roleResponseHandler(responseText, statusText, xhr, jqform){
    // example of overriding the expires and speed options for one notification

    $("#users_create_roleLOADIMG").addClass("invisible");
    if (responseText == "TRUE"){
        $("#statusmessage").empty().text("Role Deleted");
        $('#statusmessage').fadeIn().delay(2000).fadeOut('slow');
    }else{
        $("#errormessage").empty().text("Some error occurred");
        $('#errormessage').fadeIn().delay(2000).fadeOut('slow');
    }

    loadRoleMap();
}