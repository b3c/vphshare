


function defaultAjaxResponseHandler( responseText, statusText, xhr, jqform ) {
    alert(responseText);
    alert(jqform);
    var div = $(jqform).attr("rel");
    $(div).empty();
    $(responseText).appendTo( div );
}

$(document).ready(
    function(){

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