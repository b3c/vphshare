
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
        this.$query = [];
        this.$root = root;
        $('#query_button').click(function(){
           self.submit_query();
        });
        root.find("input,select,textarea").not("[type=submit]").jqBootstrapValidation();

        root.find('.column').each(function(type,value) {
            var column = $(value);
            self.$columnsList[column.attr('id')] = {
                name: column.data('name'),
                type: column.data('type')
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
        var operations = "";
        var input = "";
        if ($.inArray(type, ['smallint', 'int', 'bigint']) > -1){
            operations = ich.numeric_options()[0].outerHTML;
            input = ich.integer_value({'name':name})[0].outerHTML
        }else if ($.inArray(type, ['double', 'float']) > -1){
            operations = ich.numeric_options()[0].outerHTML;
            input = ich.float_value({'name':name})[0].outerHTML
        }else if ($.inArray(type, ['date', 'time', 'dateTime']) > -1){
            operations = ich.numeric_options()[0].outerHTML;
            input = ich.datetime_value({'name':name})[0].outerHTML
        }else{
            operations = ich.string_options()[0].outerHTML;
            input = ich.text_value({'name':name})[0].outerHTML
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
                $(this).next().val('none');
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
           "id": id
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
        if (root.parent().find('.'+id).length){
            columnObj.remove();
            $("#select-message-error").text("This column is already in the select statement!").fadeIn().delay(5000).slideUp();
            return false;
        }
        var new_select = $(ich.select({"id":id, "name":name}));

        new_select.data({
           "name": name,
           "type": type,
           "id": id
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

    QueryBuilder.prototype.submit_query= function () {
        var self = this;
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
                            "operator" : insideCondition.find('.operator:first').val(),
                            "value": insideCondition.find('input:first').val(),
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
                            "displayAs": select.find('input:first').val()
                    };
                    self.$dropArea['select'].push(selectCondition)
                }

            });
        }
    };

    QueryBuilder.prototype.loadtables = function () {
        var self = this;
    };

    QueryBuilder.autoDiscover = function() {
        var queryBuilder = $( '#query-builder');
        new QueryBuilder(queryBuilder);

    };
}).call(this);