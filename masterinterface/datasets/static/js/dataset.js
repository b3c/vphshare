
(function () {
    var global, $, QueryBuilder;
    global = this;
    $ = global.$;

    QueryBuilder = global.QueryBuilder = function (element, options) {
        this.inizialize(element);
    };

    QueryBuilder.prototype.inizialize = function (root) {
        var self = this;
        this.$columnsList = {};
        this.$dropArea = {"select":[], "where":[]};
        this.$root = root;
        this.$globalID = root.data('globalid');
        this.$queryid = root.data('queryid');
        $('#query_button').click(function(){
           $('#query_button').button('loading');
           self.submit_query();
        });
        $('#saveas-query').click(function(){
            self.saveAsQuery();
        });
        $('#save-query').click(function(){
            self.saveQuery();
        });

        $(".query-list").each(function(type,value){
            var list = $(value);
            list.bind('close', function () {
                var local = $(this);
                var id = list.data('queryid');
                var name = list.data('name');
                if (confirm('Are you sure you want to delete '+name+' query?')) {
                    $.ajax({
                        type:"POST",
                        url:"/delete_the_query/",
                        dataType: "json",
                        data: {"globalID":self.$globalID, "q":id, "name":name },
                        success: function(data){
                            if (data['deleted'])
                             return true;
                        },
                        fail: function(data){
                            alert("Some errors occurs, retry");
                        }
                    });
                    return true;
                } else {
                  return false;
                }
            })
        });

        root.find("input,select,textarea").not("[type=submit]").jqBootstrapValidation();
        root.find(".input-date").each(function(type,value) {
            $(value).datetimepicker({clearBtn: false,
                autoclose: true,
                format: 'dd/mm/yyyy hh:ii'})
        });

        root.find(".input-datetime").each(function(type,value) {
            $(value).datetimepicker({minView: 2,
            autoclose: true,
            clearBtn: false,
            startView: 2,
            format: 'dd/mm/yyyy'})
        });

        root.find(".input-time").each(function(type,value) {
            $(value).datetimepicker({minView: 0,
                format: 'hh:ii',
                clearBtn: false,
                maxView: 1,
                autoclose: true,
                startView: 1});
            }
        );

        root.find('.column').each(function(type,value) {
            var column = $(value);
            self.$columnsList[column.attr('id')] = {
                name: column.data('name'),
                type: column.data('type'),
                tablename: column.data('tablename')
            };
            column.draggable({
                revert: "invalid",
                revertDuration: 200,
                zIndex: 2500,
                cursor: "move",
                helper: "clone",
                appendTo: "body",
                cursorAt: { top: 17, left: 15 },
                start: function (event, ui) {
                },
                drag: function (event, ui) {
                }
            })
        });

        root.find('.condition:not(.new-condition)').droppable({
              activeClass: "new-condition-active",
              hoverClass: "condition-hover",
              drop: function (event, ui){
                  self.drop_new_single_operation(event, ui, $(this));
              }
        });

        root.find('.new-condition').droppable({
              activeClass: "new-condition-active",
              hoverClass: "condition-hover",
              drop: function (event, ui){
                  self.drop_new_condition(event, ui, $(this));
              }
        });

        root.find('.new-select').droppable({
              activeClass: "new-condition-active",
              hoverClass: "condition-hover",
              drop: function (event, ui){
                  self.drop_new_select(event, ui, $(this));
              }
        });

        root.find('.close').tooltip();
        root.find('.connector').click(
            self.changeConnector
        );
        self.loadtables();
        if (this.$queryid != ""){
            $('#query_button').button('loading');
            self.submit_query();
        }
        root.find('select').change(function(){
            var value=$( this ).val();
            if ($.inArray(value, ['=--EMPTY', 'NOT=--EMPTY'])>-1){
                $(this).next().hide();
                $(this).next().val('1');
            }else{
                if ($(this).next()=='none') $(this).next().val('');
                $(this).next().show();
            }
        });
    };

    QueryBuilder.prototype.changeConnector = function (){
        var self = $(this);
        if (self.hasClass("and")){
            self.removeClass("and").addClass("or");
        }else{
            self.removeClass("or").addClass("and");
        }
    };

    QueryBuilder.drop_new_operation = function (target, operation) {
        if ( target.find('.connector').length ) {
            target.children('.connector').before(operation);
        }else{
            target.append(operation);
        }
    };

    QueryBuilder.prototype.drop_new_single_operation = function (event, ui, target) {
        var self = this;
        var columnObj = $(ui.draggable).clone();
        var name = columnObj.data('name');
        var type = columnObj.data('type');
        var id = columnObj.attr('id');
        var tablename = columnObj.data('tablename');
        var operations = "";
        var input = "";
        var valuetype = "";
        if ($.inArray(type, ['smallint', 'int', 'bigint']) > -1){
            operations = ich.numeric_options()[0].outerHTML;
            valuetype = "numeric";
            input = ich.integer_value({'name':name})[0].outerHTML
        }else if ($.inArray(type, ['double', 'float']) > -1){
            operations = ich.numeric_options()[0].outerHTML;
            valuetype = "numeric";
            input = ich.float_value({'name':name})[0].outerHTML
        }else if ($.inArray(type, ['date', 'time', 'dateTime']) > -1){
            valuetype = type.toLowerCase();
            operations = ich.numeric_options()[0].outerHTML;
            input = ich.datetime_value({'name':name})[0].outerHTML
        }else{
            operations = ich.string_options()[0].outerHTML;
            input = ich.text_value({'name':name})[0].outerHTML;
            valuetype = "string";
        }

        var operation = ich.inside_condition({
                           "left_node": columnObj.html(),
                            "operations": operations,
                            "input": input
        });
        operation.find('select').change(function(){
            var value=$( this ).val();
            if ($.inArray(value, ['=--EMPTY', 'NOT=--EMPTY'])>-1){
                $(this).next().hide();
                $(this).next().val('1');
            }else{
                if ($(this).next()=='none') $(this).next().val('');
                $(this).next().show();
            }
        });
        if (type == "date"){
            operation.find('.date').datetimepicker({clearBtn: false,
            autoclose: true,
            format: 'dd/mm/yyyy hh:ii'});
        }else if (type == "dateTime"){
            operation.find('.date').datetimepicker({minView: 2,
            autoclose: true,
            clearBtn: false,
            startView: 2,
            format: 'dd/mm/yyyy'});
        }else if (type == "time"){
            operation.find('.date').datetimepicker({minView: 0,
            format: 'hh:ii',
            clearBtn: false,
            maxView: 1,
            autoclose: true,
            startView: 1});
        }

        operation.find("input,select,textarea").jqBootstrapValidation();

        operation.data({
           "name": name,
           "type": type,
           "id": id,
           "tablename": tablename,
            "valuetype": valuetype
        });

        QueryBuilder.drop_new_operation(target,operation);
        operation.find('.connector').click(
            self.changeConnector
        );
        $('.close').tooltip();
    };

    QueryBuilder.prototype.drop_new_condition = function (event, ui, root) {
        var self = this;
        var columnObj = $(ui.draggable).clone();
        var new_condition = $(ich.condition());
        self.drop_new_single_operation(event,ui,new_condition);
        root.before(new_condition);
        new_condition.droppable({
              activeClass: "new-condition-active",
              hoverClass: "condition-hover",
              drop: function (event, ui){
                  self.drop_new_single_operation(event, ui, new_condition);
              }
        });
        new_condition.children('.connector').click(
            self.changeConnector
        );
        $('.close').tooltip();
    };

    QueryBuilder.prototype.drop_new_select = function (event, ui, root) {
        var self = this;

        var columnObj = $(ui.draggable).clone();

        var name = columnObj.data('name');
        var type = columnObj.data('type');
        var id = columnObj.attr('id');
        var tablename = columnObj.data('tablename');
        if (root.parent().find('.'+id).length){
            columnObj.remove();
            $("#select-message-error").text("This column is already in the select statement!").fadeIn().delay(5000).slideUp();
            return false;
        }
        var new_select = $(ich.select({"id":id, "name":name}));

        new_select.data({
           "name": name,
           "type": type,
           "id": id,
           "tablename": tablename
        });
        root.before(new_select);
        new_select.find('.close').tooltip();
    };

    QueryBuilder.prototype.validation = function () {
        var self = this;
        var errors = self.$root.find("input,select,textarea").jqBootstrapValidation("collectErrors");
        for (key in errors){
            if (errors[key].length){
                $("#where-message-error").text(key+" assignment error. Please check if the inserted value is missing or a wrong type value.").fadeIn().delay(5000).slideUp();
                $('#myTab a:last').tab('show');
                $('input[name='+key+']').focus();
                return false;
            }
        }
        return true;
    };

    QueryBuilder.prototype.generateQuery = function(){
        var self = this;
        $('#myTab a:last').tab('show');
        self.$dropArea = {"select":[], "where":[]};
        if (self.validation()){

            self.$root.find('#where > .condition:not(.new-condition)').each(function(type, value){
                var dropArea = $(value);

                if( dropArea.find('.inside-condition').length > 0 ){
                    //it is a group of conditions
                    //{"group":[Cond_Obj, Cond_Obj2 ...], "connector":[]}
                    var connector = "";
                    if (dropArea.children('.connector:visible').length > 0)
                        connector = $(dropArea.children('.connector:visible')[0]).hasClass('and') ? 'and' : 'or';

                    var condition = {"group":[] , "connector":connector};

                    dropArea.find('.inside-condition').each(function(){
                        var insideCondition = $(this);
                        condition['group'].push({
                            "name": insideCondition.data("name"),
                            "type": insideCondition.data("type"),
                            "tablename": insideCondition.data("tablename"),
                            "operator" : insideCondition.find('.operator:first').val(),
                            "value": insideCondition.find('input:first').val(),
                            "valueType": insideCondition.data("valuetype"),
                            "connector": insideCondition.children('.connector:visible').length > 0 ? $(insideCondition.children('.connector:visible')[0]).hasClass('and') ? "and" : "or" : ""
                        });
                    });
                    self.$dropArea['where'].push(condition)
                }
            });

            self.$root.find('#select-columns > .select:not(.new-select)').each(function(type, value){
                var select = $(value);
                var selectCondition;
                if( select.find('.condition-form').length > 0 ){
                    selectCondition = {
                            "name": select.data("name"),
                            "type": select.data("type"),
                            "tablename": select.data("tablename"),
                            "displayAs": select.find('input:first').val()
                    };
                    self.$dropArea['select'].push(selectCondition)
                }

            });
            return true;
        }else{
            return false;
        }
    };

    QueryBuilder.prototype.submit_query= function () {
        var self = this;
        if (self.validation()){
            self.generateQuery();
            //Send query to server and retriave the results.
            $.ajax({
                type:"POST",
                url:"/get_results/",
                dataType: "json",
                data: {"globalID":self.$globalID, "query":JSON.stringify(self.$dropArea) },
                success: function(data){
                    self.getReults(data);
                },
                fail: function(data){
                    alert("Some errors occurs, retry");
                }
            })
        }
    };

    QueryBuilder.prototype.getReults = function (results) {
        var self = this;
        var header = [];
        for (column in results['header']){
            header.push({"title":results['header'][column]});
        }
        var table = $('<table cellpadding="0" cellspacing="0" border="0" class="display cell-border" id="dataset-results-table"></table>');
        $("#query-results > .span12").empty();
        table.appendTo("#query-results > .span12");
        $("#query-results").show();
        $("#hr-query-results").show();
        table.dataTable({
                /*"data": dataSet,*/
                "data": results['results'],
                "columns": header,
                "paging": true,
                "ordering": true,
                "info": true,
                "search": true,
                "scrollX": true,
                "dom": 'T<"clear">lfrtip',
                "tableTools": {
                    "sSwfPath": "/static/swf/copy_csv_xls_pdf.swf"
                },
                language: {
                    search: "<i class='icon-search'></i>",
                    paginate: {
                        previous: "«",
                        next: "»"
                    }
                }
        });
        $('#query_button').button('reset');
    };
    QueryBuilder.prototype.saveQuery = function () {
        var self = this;
        $("#save-query").button('loading');
        if (!self.generateQuery()) {
            $("#save-query").button('reset');
            $('#save-query-modal').modal('toggle');
            return false;
        }
        if ( $("#save-query-input").val() == "") {
            $("#save-query").button('reset');
            return false;
        }
        var name = $("#save-query-input").val();
        $.ajax({
                type:"POST",
                url:"/edit_the_query/",
                dataType: "json",
                data: {"globalID":self.$globalID, "query":JSON.stringify(self.$dropArea), "name":name , "q":self.$queryid},
                success: function(data){
                    if (data['saved'])
                    window.location.replace("/query_builder/"+self.$globalID+"/?q="+data['id']);
                },
                fail: function(data){
                    alert("Some errors occurs, retry");
                }
            });
    };

    QueryBuilder.prototype.saveAsQuery = function () {
        var self = this;
        $("#saveas-query").button('loading');
        if (!self.generateQuery()) {
            $("#saveas-query").button('reset');
            $('#saveas-query-modal').modal('toggle');
            return false;
        }
        if ( $("#saveas-query-input").val() == "") {
            $("#saveas-query").button('reset');
            return false;
        }
        var name = $("#saveas-query-input").val();
        $.ajax({
                type:"POST",
                url:"/save_the_query/",
                dataType: "json",
                data: {"globalID":self.$globalID, "query":JSON.stringify(self.$dropArea), "name":name },
                success: function(data){
                    if (data['saved'])
                    window.location.replace("/query_builder/"+self.$globalID+"/?q="+data['id']);
                },
                fail: function(data){
                    alert("Some errors occurs, retry");
                }
            });
    };

    QueryBuilder.prototype.loadtables = function () {
        var self = this;
        self.$root.find('.dataset-table').each(function () {
            $(this).dataTable({

                "dom": "<'row-fluid'<'span12'f>r>" + "<'row-fluid'<'span12'p>>" + "<'row-fluid'<'span12't>>",
                /*"data": dataSet,*/
                "columns": [
                    { "title": "" }
                ],
                "paging": true,
                "ordering": false,
                "info": false,
                "search": true,
                "scrollX": true,
                language: {
                    search: "<i class='icon-search'></i>",
                    paginate: {
                        previous: "«",
                        next: "»"
                    }
                }
            });
          });
    };

    QueryBuilder.autoDiscover = function() {
        var queryBuilder = $( '#query-builder');
        new QueryBuilder(queryBuilder);

    };
}).call(this);