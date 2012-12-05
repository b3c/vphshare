/**
 * Created with PyCharm.
 * Date: 20/11/12
 * Time: 14.46
 * To change this template use File | Settings | File Templates.
 */


/* START AJAX callback */
function resultsCallback( results ){
    var concept_uri;
    var dataset;
    var dataset_label;
    var num_match;
    var rdf_link;
    var $concept_item_base = $( '#concept-base').clone();
    $( '.media-list').html($concept_item_base);

    for ( concept_uri in results ) {

        var $concept_item = $concept_item_base.clone();
        $concept_item.attr('id','concept_uri');
        $concept_item.find('.concept-label').text(concept_uri);

        dataset = results[concept_uri]
        for ( dataset_label  in dataset ){

            num_match = dataset[dataset_label][0];
            rdf_link = dataset[dataset_label][1];
            $concept_item.find('.dataset-item').show();
            $concept_item.find('.dataset-label').text(dataset_label);
            $concept_item.find('.dataset-description').text('Match : '+num_match);
            $concept_item.find('.link-to-data').attr('href',rdf_link);

        }

        $concept_item.appendTo('.media-list');
        $concept_item.show();
    }



}

function automaticSearchCallback( results ) {

    resultsCallback( results );
    $( '#results' ).effect( 'slide', {direction:'right'}, 500 );

}

function guidedSearchS2Callback( results ) {

    resultsCallback( results );
    $( '#automaticSearchForm').hide();
    $( '#querySubmit').hide();
    $( '#backToQuery').fadeIn();
    $( '#searchContent' ).toggle( 'slide', {direction:'left'}, 400 );
    $( '#results' ).delay(500).effect( 'slide', {direction:'right'}, 500 );

}

/* END AJAX callback */

/* START AJAX call  */
function automaticSearchCall ( )
{
    var form = $( "#automaticSearchForm" );
    var input = form.find( 'input[name="freeText"]' ).val();
    var url = '/automatic_search/'
    $( '#wait' ).fadeIn();

    $.ajax({
        type : 'POST',
        url : url,
        data : {input : input
        },
        success: function( results ) {
            $( '#wait').fadeOut();
            automaticSearchCallback(results);
        },
        error: function (error) {

            $( '#wait' ).fadeOut();

        }
    });
}

function guidedSearchS1CallBack( results )
{
    var max_matches = results['max_matches'];
    var num_pages = results['num_pages'];
    var num_results_total = results['num_results_total'];
    var elem;
    var concept;
    var $term = $("#termsListBase > .term").clone();
    var $termList = $("#termsListBase").clone();

    $("#termList").remove();
    $("#termListBlock").append($termList);
    $termList.attr('id','termList');


    $("#termsList").append($term);

    for (  elem in results )
    {
        if (elem != 'num_pages' && elem != 'max_matches' && elem != 'num_results_total' )
        {

            for ( concept in results[elem] )
            {
                var term_name = results[elem][concept][0];
                var concept_name = results[elem][concept][1];
                var concept_uri = concept;
                var $addTerm = $term.clone();
                var id = concept_name + term_name;

                if (term_name.length > 50){

                    $addTerm.append(term_name.substr(0,50)+"...");

                }else{

                    $addTerm.append(term_name);

                }

                $addTerm.append('<input name="inputConceptUri" type="hidden" value="' + concept_uri + '" /> ');

                $termList.append($addTerm);

                $addTerm.show();
                $addTerm.popover({
                    title : concept_name,
                    content: term_name,
                    trigger : 'hover',
                    placement : 'right',
                    delay : { show: 500, hide: 100 }
                });

                $addTerm.draggable( {

                    cancel: "a.ui-icon", // clicking an icon won't initiate dragging
                    revert: "invalid", // when not dropped, the item will revert back to its initial position
                    containment: "document",
                    helper: "clone",
                    cursor: "move"

                } );


            }

            $termList.kendoTreeView( {

                select:  noSelect

            } );
        }
    }

}

function guidedSearchS1Call ( )
{
    var form = $( "#automaticSearchForm" );
    var input = form.find( 'input[name="freeText"]' ).val();
    var url = '/guided_search_s1/'
    $( '#wait' ).fadeIn();

    $.ajax({
        type : 'POST',
        url : url,
        data : {input : input
        },
        success:function ( results ) {

            $( '#wait' ).fadeOut();
            guidedSearchS1CallBack( results )

        },
        error: function ( error ) {

            $( '#wait' ).fadeOut();

        }
    });
}

function guidedSearchS2Call ( )
{
    var url = '/guided_search_s2/'
    var concept_uri_list = [];
    $( '#wait').fadeIn();

    $("form#queryForm :input").each(function(){
        var input = $(this).val();
        concept_uri_list.push(input);
    });


    $.ajax({
        type : 'POST',
        url : url,
        data : {concept_uri_list : concept_uri_list.join(",")
        },
        success: function( results ) {

            $( '#wait').fadeOut();
            guidedSearchS2Callback(results);

        },
        error: function (error) {

            $( '#wait').fadeOut();

        }
    });
}
/* END AJAX call  */


/* START jquery ready in search page */
$(function () {

    var $term = $( '.term'), $groups = [], $new_group = $( '#new-group' );

    $groups[0] = $( '#group0' ) ;

    /* START graphic wrap */
    /*$( '#guidedSearchCheckBox' ).popover( {
        trigger : "click",
        title : 'Guide Search',
        content : 'enable this form to guide search.',
        delay: { show: 100, hide: 50 }
    } );*/

    $( '#guidedSearchCheckBox').removeAttr('checked');

    $( '.group' ).kendoTreeView( {

        select: noSelect

    } );
    /* END graphic wrap */

    /* START event wrap */

    /** START drang & drop events */


    $groups[0].droppable( {

        accept: ".term",
        activeClass: "drop-in",
        drop: function( event, ui ) {

            dropTerm( ui.draggable ,$(this) );

        }

    } );

    $new_group.droppable( {

        accept: ".term",
        activeClass: "drop-in",
        drop: function( event, ui ) {

            newGroup( ui.draggable ,$(this) );

        }

    } );
    /** END drang & drop events */

    /** START click events */

    $( '#querySubmit' ).bind( "click", function(){ guidedSearchS2Call( ); } );

    $( '#searchButton' ).bind( "click", function(){ automaticSearchCall(); } );

    $( '#guidedSearchCheckBox' ).click( function(){

        $( '#searchButton' ).unbind('click');

        if ( $( '#guidedSearchCheckBox' ).attr( 'checked' ) ) {

            $( '#results').hide();
            $( '#querySubmit').fadeIn();
            $( '#searchButton' ).bind( "click", function(){ guidedSearchS1Call(); } );
            $( '#searchContent' ).fadeIn();
            $( '#freeText' ).attr( 'placeholder', 'Search Terms' );
            $( "div[id=exclude]" ).fadeOut( 200 ) ;

            /*** START Reset Term List ***/
            var $term = $("#termsListBase > .term").clone();
            var $termList = $("#termsListBase").clone();
            $("#termList").remove();
            $("#termListBlock").append($termList);
            $termList.attr('id','termList');
            $("#termsList").append($term);
            /*** END Reset Term List ***/




        }else{

            $( '#searchButton' ).bind( "click", function(){ automaticSearchCall(); } );
            $( '#searchContent' ).fadeOut();
            $( '#freeText' ).attr( 'placeholder', 'Search Dataset' );
            $( '#querySubmit').fadeOut();

        }

    } );

    $( '#backToQuery' ).click( function(){

        $( '#backToQuery' ).hide();
        $( '#automaticSearchForm' ).show();
        $( '#querySubmit').show();
        $('#results').toggle( 'slide', {direction:'rigth'}, 400);
        $('#searchContent').delay(500).effect( 'slide', {direction:'left'}, 500 );

    } );

    /** END click events */
    /* END events wrap */


    /* START callback from animations  */


    function newGroup( $item , $dropTarget  ) {

        var $group = $dropTarget.clone();
        var n_group = $groups.length;

        if ($item.parents('.group').length > 0){

            groupCheckContent($item.parents( '.group' ), 2);
            var $item_cloned = $item;

        }else{

            var $item_cloned = $item.clone().hide();
            $item_cloned.children().children().append( "<a class='delete-link' href='#'></a>" );
            $item_cloned.attr('id',$item.attr('data-uid'));

        }

        $groups[n_group] = $group
        $group.attr( 'id', "group"+n_group );
        $group.find( '#help' ).hide();
        $group.find( '#exclude').delay( 300 ).fadeIn( 200 );
        $group.insertBefore( $dropTarget.parents( '.k-treeview'));
        $group.hide();
        $group.kendoTreeView( {

            select: noSelect

        } ).fadeIn();
        $group.droppable( {

            accept: ".term",
            activeClass: "drop-in",
            drop: function( event, ui ) {

                dropTerm( ui.draggable ,$( this ) );

            }

        } );

        $item_cloned.appendTo($group).delay( 200 ).fadeIn( 200 );
        $item_cloned.draggable( {

            cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            containment: "document",
            helper: "clone",
            cursor: "move"

        } );

    }

    function dropTerm( $item , $dropTarget  ) {

        if ( $dropTarget.find( '#'+$item.attr( 'data-uid' ) ).length > 0 )
            return ;

        if ($item.parents('.group').length > 0){

            groupCheckContent($item.parents( '.group' ), 2);
            var $item_cloned = $item;


        }else{

            var $item_cloned = $item.clone().hide();
            $item_cloned.children().children().append( "<a class='delete-link' href='#'></a>" );
            $item_cloned.attr('id',$item.attr('data-uid'));

        }

        $dropTarget.find( '#help' ).fadeOut( 200 );
        $dropTarget.find( '#exclude').delay( 300 ).fadeIn( 200 );


        $item_cloned.appendTo( $dropTarget ).delay( 200 ).fadeIn( 200 );


        $item_cloned.draggable( {

            cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            containment: "document",
            helper: "clone",
            cursor: "move"

        } );


    }

    function groupCheckContent( parent , minLength ){

        if(typeof(minLength)==='undefined') minLength = 1;

        if ( parent.children( '.term' ).length == minLength && parent.attr( 'id' ) != 'group0' ){

            parent.parents( '.k-treeview' ).fadeOut( 400, function(){ $( this ).parents( '.k-treeview' ).remove(); } );
            parent.parents( '.k-treeview' ).remove();
            return;

        }


        if ( parent.attr( 'id' ) == 'group0' &&  parent.children( '.term' ).length == minLength  ){

            parent.children( '#help' ).delay(400).fadeIn(200);
            parent.children( '#exclude').fadeOut();

        }
    }

    /* END callback from animations  */
    $( document ).on('click', '.delete-link', function( e ) {

        var parent = $( this ).parents( '.group' );

        e.preventDefault();

        groupCheckContent(parent);
        $( this ).closest( '.k-item' ).remove();



    });
});

function noSelect(e){

    var item = e.node;
    item.children('.k-state-selected' ).removeClass( 'k-state-selected' );
    item.children( '.k-state-focused' ).removeClass( 'k-state-focused' );

}
/* END jquery ready in search page */
