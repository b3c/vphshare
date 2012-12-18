/**
 * Created with PyCharm.
 * Date: 20/11/12
 * Time: 14.46
 * To change this template use File | Settings | File Templates.
 */

var SEARCH = false; // define if guidedsearchS1 search is a new search or the same.
/* START AJAX callback */

function resultsCallback( results ) {

    "use strict";
    var conceptUri;
    var dataset;
    var datasetLabel;
    var numMatch;
    var rdfLink;
    var conceptItem;
    var conceptItemBase = $( '#concept-base' ).clone();
    $( '.media-list' ).html( conceptItemBase );

    for ( conceptUri in results ) {
        if ( results.hasOwnProperty( conceptUri ) ) {

            conceptItem = conceptItemBase.clone();
            conceptItem.attr( 'id', 'concept-uri' );
            conceptItem.find( '.concept-label' ).text( conceptUri );
            dataset = results[conceptUri];
            for ( datasetLabel  in dataset ) {

                if ( dataset.hasOwnProperty( datasetLabel ) ) {

                    numMatch = dataset[datasetLabel][0];
                    rdfLink = dataset[datasetLabel][1];
                    conceptItem.find( '.dataset-item' ).show();
                    conceptItem.find( '.dataset-label' ).text( datasetLabel );
                    conceptItem.find( '.dataset-description' ).text( 'Match : ' + numMatch );
                    conceptItem.find( '.link-to-data' ).attr( 'href', rdfLink );

                }

            }
            if ( !datasetLabel ){
                conceptItem.find( '.concept-description' ).text('No results matching');
            }
            conceptItem.appendTo( '.media-list' );
            conceptItem.show();
        }
    }


}

function automaticSearchCallback( results ) {

    "use strict";
    resultsCallback( results );
    $( '#results' ).effect( 'slide', {direction: 'right'}, 500 );

}

function guidedSearchS2Callback( results ) {

    "use strict";
    resultsCallback( results );
    $( '#automatic-search-form' ).hide();
    $( '#query-submit' ).hide();
    $( '#back-to-query' ).fadeIn();
    $( '#search-content' ).toggle( 'slide', {direction: 'left'}, 400 );
    $( '#results' ).delay( 500 ).effect( 'slide', {direction: 'right'}, 500 );

}

/* END AJAX callback */

/* START AJAX call  */
function automaticSearchCall() {

    "use strict";
    var form;
    var url;
    var input;

    form = $( "#automatic-search-form" );
    input = form.find( 'input[name="free-text"]' ).val();
    url = '/automatic_search/';
    $( '#wait' ).fadeIn();

    $.ajax( {
        type: 'POST',
        url: url,
        data: {input: input},
        success: function( results ) {
            $( '#wait' ).fadeOut();
            automaticSearchCallback( results );
        },
        error: function( error ) {

            $( '#wait' ).fadeOut();

        }
    } );
}

function guidedSearchS1CallBack( results ) {

    "use strict";
    var maxMatches = results.max_matches;
    var numPages = results.num_pages;
    var numResultsTotal = results.num_results_total;
    var pagenum = parseInt( results.page_num, 10 );

    var item;
    var term = $( "#terms-list-base > .term" ).clone();
    var termList = $( "#terms-list-base" ).clone();

    $( "#term-list-block" ).children( '#terms-pagination' ).remove();

    var termsPagination = $( "#term-list-block" ).children( '#terms-pagination-base' ).clone().attr( 'id', 'terms-pagination' );


    $( "#term-list" ).remove();
    $( "#term-list-block" ).append( termList );
    termList.attr( 'id', 'term-list' );

    var termsResults = results[pagenum];

    for ( item in termsResults ) {

        var termName = termsResults[item][0];
        var conceptName = termsResults[item][1];
        var addTerm = term.clone();
        var id = conceptName + termName;

        if ( termName.length > 40 ) {

            addTerm.append( termName.substr( 0, 40 ) + "..." );

        } else {

            addTerm.append( termName );

        }

        var fieldset = $('<fieldset class="fieldsetTerm hide"></fieldset>');
        fieldset.append( '<input name="inputConceptUri" type="hidden" value="' + item + '" /> ' );
        fieldset.append( '<input name="inputTermName" type="hidden" value="' + termName + '" /> ' );
        fieldset.append( '<input name="inputConceptName" type="hidden" value="' + conceptName + '" /> ' );

        addTerm.append(fieldset);

        termList.append( addTerm );

        addTerm.show();
        addTerm.popover( {
            title: conceptName,
            content: termName,
            trigger: 'hover',
            placement: 'left',
            delay: { show: 500, hide: 100 }
        } );

        addTerm.draggable( {

            cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            containment: "document",
            helper: "clone",
            cursor: "move"

        } );


    }

    if ( numPages > 1 ) {

        for ( var i = 1; i <= numPages; i++ ) {

            var page = termsPagination.find( '#prev' ).clone();
            page.attr( 'id', 'pg' + i ).attr( 'page', i ).children( 'a' ).attr( "href", "#" ).text( i );

            if ( i === pagenum )
                page.attr( 'class', 'active' );

            if ( i === 1 ) {

                page.insertAfter( termsPagination.find( '#prev' ) );

            } else {

                page.insertAfter( termsPagination.find( '#pg' + (i - 1) ) );

            }

        }

        if ( pagenum === 1 )
            termsPagination.find( '#prev' ).addClass( 'disabled' ).removeClass( 'page' );

        if ( pagenum === numPages )
            termsPagination.find( '#next' ).addClass( 'disabled' ).removeClass( 'page' );

        termsPagination.show();
        termsPagination.appendTo( "#term-list-block" );

    }

    $( "#num-terms" ).text( numResultsTotal ).parent().show();

    termList.kendoTreeView( {

        select: noSelect

    } );

    SEARCH = true;
}

function guidedSearchS1Call() {

    "use strict";
    var form = $( "#automatic-search-form" ),
        input = form.find( 'input[name="free-text"]' ).val(),
        url = '/guided_search_s1/',
        numMaxHits = $( '#num-max-hits' ).val(),
        pageNum = $( '#page-num' ).val();

    if ( SEARCH === false ) {

        $( '#page-num' ).val( 1 );
        pageNum = 1;

    }

    $( '#wait-terms' ).fadeIn();
    $.ajax( {
        type: 'POST',
        url: url,
        data: {input: input, nummaxhits: numMaxHits, pagenum: pageNum},
        success: function( results ) {

            $( '#wait-terms' ).fadeOut();
            guidedSearchS1CallBack( results );

        },
        error: function( error ) {

            $( '#wait-terms' ).fadeOut();

        }
    } );
}

function guidedSearchS2Call() {

    "use strict";
    var url = '/guided_search_s2/';
    var conceptUriList = [];
    $( '#wait' ).fadeIn();

    $( "form#query-form :input[name=inputConceptUri]" ).each( function() {
        var input = $( this ).val();
        conceptUriList.push( input );
    } );

    $.ajax( {
        type: 'POST',
        url: url,
        data: {concept_uri_list: conceptUriList.join( "," )
        },
        success: function( results ) {

            $( '#wait' ).fadeOut();
            guidedSearchS2Callback( results );

        },
        error: function( error ) {

            $( '#wait' ).fadeOut();

        }
    } );
}

function guidedSearchComplexQueryCall() {

    "use strict";
    var groupsList = [];
    var groupsQuery = [];
    var url = '/guided_search_complex_query/';

    $( '#wait' ).fadeIn();

    $( '.group' ).each( function() {
        groupsList.push( this.id );
    } );

    for ( var i = 0; i < (groupsList.length - 1); i++ ) {

        var conceptUriList = [];
        var id_group = groupsList[ i ];


        $( "ul#" + id_group ).each( function() {

            $(this).find('.fieldsetTerm').each( function() {

                var singleTerm = [];

                var conceptUri = $(this).find("input[name=inputConceptUri]").val()
                var termName =  $(this).find("input[name=inputTermName]").val()
                var conceptName =  $(this).find("input[name=inputConceptName]").val()


                if ( $( "#" + id_group + ' > .exclude' ).children().hasClass( 'active' ) ) {
                    singleTerm.push( ['NOT ' + conceptUri, termName, conceptName ] );
                    groupsQuery.push ( singleTerm );
                }
                else {
                    singleTerm.push( conceptUri );
                    singleTerm.push( termName );
                    singleTerm.push( conceptName );
                    conceptUriList.push( singleTerm );
                }

            });
        });

        if ( conceptUriList.length !== 0 ) {
            groupsQuery.push( conceptUriList );
        }

    }

    // multidimensional array with JSON
    var stringJSON = JSON.stringify( groupsQuery );

    $.ajax( {
        type: 'POST',
        url: url,
        data: { groups_query: stringJSON },
        success: function( results ) {

            $( '#wait' ).fadeOut();
            guidedSearchS2Callback( results );

        },
        error: function( error ) {

            $( '#wait' ).fadeOut();

        }
    } );

}

/* END AJAX call  */

/* START jquery ready in SEARCH page */
$( function() {

    "use strict";
    var groups = [];                   //groups array content block
    var newGroup = $( '#new-group' );  //is "IN AND TERMS" group that call new group event

    /** START define new event 'remove' **/

    /** define remove event**/
    var ev = new $.Event( 'remove' ),
        orig = $.fn.remove;
    $.fn.remove = function() {
        $( this ).trigger( ev );
        return orig.apply( this, arguments );
    };
    /** END define new event 'remove' **/

    /* START graphic wrap */
    groups[0] = $( '#group0' ); //load first group (IN OR TERMS)

    $( ".exclude" ).tooltip( {title: "Exclude"} );

    $( "#slider-range-min" ).slider( {
        range: "min",
        value: 20,
        min: 20,
        max: 100,
        slide: function( event, ui ) {

            $( "#num-max-hits" ).val( ui.value );
            $( "#max-terms" ).html( ui.value );

        },
        stop: function( event, ui ) {

            $( "#num-max-hits" ).val( ui.value );
            $( "#max-terms" ).html( ui.value );
            if ( $( '#page-num' ).val() > Math.ceil( ($( "#num-max-hits" ).val() / 20) ) ) {
                $( '#page-num' ).val( Math.ceil( ($( "#num-max-hits" ).val() / 20) ) );
            }
            if ( SEARCH ) {
                guidedSearchS1Call();
            }

        }
    } );

    $( "#amount" ).val( "$" + $( "#slider-range-min" ).slider( "value" ) );

    $( '#guided-search-check-box' ).removeAttr( 'checked' );

    $( '.group' ).kendoTreeView( {

        select: noSelect

    } );
    /* END graphic wrap */

    /* START event wrap */

    /** START drang & drop events */
    groups[0].droppable( {

        accept: ".term",
        activeClass: "drop-in",
        drop: function( event, ui ) {

            dropTerm( ui.draggable, $( this ) );

        }

    } );

    newGroup.droppable( {

        accept: ".term",
        activeClass: "drop-in",
        drop: function( event, ui ) {

            createNewGroup( ui.draggable, $( this ) );

        }

    } );
    /** END drang & drop events */

    /* END events wrap */


    /* START callback from animations  */

    /* Create new group when term is dropped in AND group*/
    function createNewGroup( item, dropTarget ) {

        var group = dropTarget.clone();
        var nGroup = groups.length;
        var itemCloned;

        if ( item.parents( '.group' ).length > 0 ) {

            groupCheckContent( item.parents( '.group' ), 2 );
            itemCloned = item;

        } else {

            itemCloned = item.clone().hide();
            itemCloned.children().children().append( '<a class="delete-link" href="#"></a>' );
            itemCloned.attr( 'id', item.attr( 'data-uid' ) );

        }

        groups[nGroup] = group;
        group.attr( 'id', "group" + nGroup );
        group.find( '.help' ).hide();
        group.find( '#and' ).show();
        group.find( '.exclude' ).tooltip( {title: "Exclude"} ).delay( 300 ).fadeIn( 200 );
        group.insertBefore( dropTarget.parents( '.k-treeview' ) );
        group.hide();
        group.kendoTreeView( {

            select: noSelect

        } ).fadeIn();
        group.droppable( {

            accept: ".term",
            activeClass: "drop-in",
            drop: function( event, ui ) {

                dropTerm( ui.draggable, $( this ) );

            }

        } );

        itemCloned.appendTo( group ).delay( 200 ).fadeIn( 200 );
        itemCloned.draggable( {

            cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            containment: "document",
            helper: "clone",
            cursor: "move"

        } );

    }

    /* Create new group when term is dropped in OR group*/
    function dropTerm( item, dropTarget ) {

        var itemCloned;

        //if term dropped is not present in group , it can be dropped
        if ( (dropTarget.find( '#' + item.attr( 'data-uid' ) ).length === 0 )) {

            //if term came from other groups or from term-list search results
            if ( item.parents( '.group' ).length > 0 ) {

                groupCheckContent( item.parents( '.group' ), 2 );
                itemCloned = item;


            } else {

                itemCloned = item.clone().hide();
                itemCloned.children().children().append( "<a class='delete-link' href='#'></a>" );
                itemCloned.attr( 'id', item.attr( 'data-uid' ) );

            }

            dropTarget.find( '.help' ).fadeOut( 200 );
            dropTarget.find( '.exclude' ).delay( 300 ).fadeIn( 200 );

            itemCloned.appendTo( dropTarget ).delay( 200 ).fadeIn( 200 );

            itemCloned.draggable( {

                cancel: "a.ui-icon", // clicking an icon won't initiate dragging
                revert: "invalid", // when not dropped, the item will revert back to its initial position
                containment: "document",
                helper: "clone",
                cursor: "move"

            } );
        }
    }

    //verify if group have to be delete (no more terms inside it)
    function groupCheckContent( parent, minLength ) {

        if ( parent.children( '.term' ).length === minLength && parent.attr( 'id' ) !== 'group0' ) {

            parent.parents( '.k-treeview' ).fadeOut( 400, function() {
                $( this ).parents( '.k-treeview' ).remove();
            } );
            parent.parents( '.k-treeview' ).remove();

        }else if ( parent.attr( 'id' ) === 'group0' && parent.children( '.term' ).length === minLength ) {

            //if group is group0 return to intial view.
            parent.children( '.help' ).delay( 400 ).fadeIn( 200 );
            parent.children( '.exclude' ).fadeOut();

        }
    }

    /* END callback from animations  */

    /* START click event */

    $( '#free-text' ).change( function() {
        SEARCH = false;
    } );

    $( '#query-submit' ).bind( "click", function() {
        //guidedSearchS2Call();
        guidedSearchComplexQueryCall()

    } );
    //$( '#query-submit' ).bind( "click", function(){ guidedSearchComplexQueryCall( ); } );

    $( '#search-button' ).bind( "click", function() {
        automaticSearchCall();
    } );
    $( '#automatic-search-form' ).bind(
        "submit",
        function() {
            if ( $( '#guided-search-check-box' ).attr( 'checked' ) ) {
                guidedSearchS1Call();
            } else {
                automaticSearchCall();
            }
            return false;
        }
    );

    /** reset of guidedSearch S1 area**/
    $( '#guided-search-check-box' ).click( function() {

        $( '#search-button' ).unbind( 'click' );

        if ( $( '#guided-search-check-box' ).attr( 'checked' ) ) {

            $( '#results' ).hide();
            $( '#query-submit' ).fadeIn();
            $( '#search-content' ).fadeIn();
            $( '#search-button' ).bind( "click", function() {
                guidedSearchS1Call();
            } );
            $( '#free-text' ).attr( 'placeholder', 'Search Terms' );


            /*** START Reset Term List ***/
            var term = $( "#terms-list-base > .term" ).clone();
            var termList = $( "#terms-list-base" ).clone();
            $( "#term-list" ).remove();
            $( "#term-list-block" ).append( termList );
            termList.attr( 'id', 'term-list' );
            $( "#num-max-hits" ).val( 20 );
            $( "#max-terms" ).text( 20 );
            $( "#num-terms" ).text( '' ).parent().hide();
            $( "#page-num" ).val( 1 );
            $( "#slider-range-min" ).slider( 'value', '20' );
            $( "#termsPagination" ).remove();

            $( '.group > .term' ).bind( 'remove', function( e ) {

                var parent = $( this ).parents( '.group' );

                e.preventDefault();

                groupCheckContent( parent, 1 );

            } );

            $( '.group > .term' ).remove();
            SEARCH = false;
            /*** END Reset Term List ***/

        } else {

            $( '#search-button' ).bind( "click", function() {
                automaticSearchCall();
            } );
            $( '#search-content' ).fadeOut();
            $( '#free-text' ).attr( 'placeholder', 'Search Dataset' );
            $( '#query-submit' ).fadeOut();

        }

    } );

    $( '#back-to-query' ).click( function() {

        $( '#back-to-query' ).hide();
        $( '#automatic-search-form' ).show();
        $( '#query-submit' ).show();
        $( '#results' ).toggle( 'slide', {direction: 'rigth'}, 400 );
        $( '#search-content' ).delay( 500 ).effect( 'slide', {direction: 'left'}, 500 );

    } );

    /** event to delete term from group **/
    $( document ).on( 'click', '.delete-link', function( e ) {

        var parent = $( this ).parents( '.group' );

        e.preventDefault();

        groupCheckContent( parent, 1 );
        $( this ).closest( '.k-item' ).remove();


    } );

    /** event to change page of terms-list **/
    $( document ).on( 'click', '.page', function( e ) {

        var page = $( this );
        var id = page.attr( 'id' );
        var newpage = 1;

        if ( id === 'prev' && !page.hasClass( 'disabled' ) ) {

            newpage = parseInt( $( '#page-num' ).val(), 10 ) - 1;


        } else if ( id === 'next' && !page.hasClass( 'disabled' ) ) {

            newpage = parseInt( $( '#page-num' ).val(), 10 ) + 1;

        } else {

            newpage = page.attr( 'page' );

        }

        $( '#page-num' ).val( newpage );
        e.preventDefault();

        guidedSearchS1Call();


    } );
    /* END click event */
} );

/*
noSelect hide the selection event
from term in kendo treeview ***MAYBE SOME BUG HERE***
*/
function noSelect( e ) {

    "use strict";
    var item = e.node;
    item.children( '.k-state-selected' ).removeClass( 'k-state-selected' );
    item.children( '.k-state-focused' ).removeClass( 'k-state-focused' );

}
/* END jquery ready in search page */
