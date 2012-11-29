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

function guidedSearchS1Call ( )
{
    var form = $( "#automaticSearchForm" );
    var input = form.find( 'input[name="freeText"]' ).val();
    var url = '/guided_search_s1/'

    $.ajax({
        type : 'POST',
        url : url,
        data : {input : input
        },
        success: function( results ) {
            alert(results[0]);
        },
        error: function (error) {
            alert(error);
        }
    });
}

/* END AJAX call  */


/* START jquery ready in search page */
$(function() {

    var $term = $( '.term'), $groups = [], $new_group = $( '#new-group' );

    $groups[0] = $( '#group0' ) ;

    /* START graphic wrap */
    /*$( '#guidedSearchCheckBox' ).popover( {
        trigger : "click",
        title : 'Guide Search',
        content : 'enable this form to guide search.',
        delay: { show: 100, hide: 50 }
    } );*/

    $( '#termsList' ).kendoTreeView( {

        select: noSelect

    } );

    $( '.group' ).kendoTreeView( {

        select: noSelect

    } );
    /* END graphic wrap */

    /* START event wrap */

    /** START drang & drop events */
    $term.draggable( {

        cancel: "a.ui-icon", // clicking an icon won't initiate dragging
        revert: "invalid", // when not dropped, the item will revert back to its initial position
        containment: "document",
        helper: "clone",
        cursor: "move"

    } );

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

    $( '#searchButton' ).bind( "click", function(){ automaticSearchCall(); } );

    $( '#guidedSearchCheckBox' ).click( function(){

        $( '#searchButton' ).unbind('click');

        if ( $( '#guidedSearchCheckBox' ).attr( 'checked' ) ) {

            $( '#searchButton' ).bind( "click", function(){ guidedSearchS1Call(); } );
            $( '#searchContent' ).fadeIn();
            $( '#freeText' ).attr( 'placeholder', 'Search Terms' )

        }else{

            $( '#searchButton' ).bind( "click", function(){ automaticSearchCall(); } );
            $( '#searchContent' ).fadeOut();
            $( '#freeText' ).attr( 'placeholder', 'Search Dataset' )

        }

    } );

    $('#querySubmit').click( function(){

        $( '#search' ).toggle( 'slide', {direction:'left'}, 400 );
        $( '#results' ).delay(500).effect( 'slide', {direction:'right'}, 500 );

    } );

    $( '#backToQuery' ).click( function(){

        $('#results').toggle( 'slide', {direction:'rigth'}, 400);
        $('#search').delay(500).effect( 'slide', {direction:'left'}, 500 );

    } );

    $( '.delete-link' ).click(function( e ) {

        var parent = $( this ).parents( '.group' );

        e.preventDefault();
        if ( parent.children( '.term' ).length == 1 && parent.attr( 'id' ) != 'group0' ){

            $( this ).parents( '.k-treeview' ).fadeOut( 400, function(){ $( this ).parents( '.k-treeview' ).remove() } );
            return;

        }

        $( this ).closest( '.k-item' ).remove();

        if ( parent.attr( 'id' ) == 'group0' &&  parent.children( '.term' ).length == 0  )

            parent.children( '#help' ).fadeIn();

    });
    /** END click events */
    /* END events wrap */


    /* START callback from animations  */
    function noSelect(e){

        var item = e.node;

        item.children( '.k-state-selected' ).removeClass( 'k-state-selected' );
        item.children( 'k-state-focused' ).removeClass( 'k-state-focused' );

    }

    function newGroup( $item , $dropTarget  ) {

        var $item_cloned = $item.clone().hide();
        var $group = $dropTarget.clone();
        var n_group = $groups.length;


        $group.attr( 'id', "group"+n_group );
        $group.find( '#help' ).hide();
        $group.insertAfter( $groups[n_group-1].parent() );
        $group.hide();
        $groups[n_group] = $group;
        $group.kendoTreeView( {

            select: noSelect

        } ).fadeIn();
        $groups[n_group].droppable( {

            accept: ".term",
            activeClass: "drop-in",
            drop: function( event, ui ) {

                dropTerm( ui.draggable ,$( this ) );

            }

        } );

        $item_cloned.children().children().append( "<a class='delete-link' href='#'></a>" );
        $item_cloned.appendTo($group).delay( 200 ).fadeIn( 200 );

    }

    function dropTerm( $item , $dropTarget  ) {

        var $item_cloned = $item.clone().hide();
        $item_cloned.children().children().append( "<a class='delete-link' href='#'></a>" );
        $dropTarget.find( '#help' ).fadeOut( 200 );
        $item_cloned.appendTo( $dropTarget ).delay( 200 ).fadeIn( 200 );

    }
    /* END callback from animations  */

});

/* END jquery ready in search page */
