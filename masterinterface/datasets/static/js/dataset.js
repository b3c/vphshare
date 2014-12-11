
(function () {
    var global, $, QueryBuilder;
    global = this;
    $ = global.$;

    QueryBuilder = global.QueryBuilder = function (element, options) {
        this.inizialize(element);
    };

    QueryBuilder.prototype.inizialize = function (root) {
        var self = this;
        this.$columnsList
        root.find('.column').each(function(type,value) {
            $(value).draggable({
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
    };

    QueryBuilder.prototype.loadtables = function (table) {
        var self = this;
    };

    QueryBuilder.prototype.loadtables = function () {
        var self = this;
    };

    QueryBuilder.autoDiscover = function() {
        var queryBuilder = $( '#query-builder');
        new QueryBuilder(queryBuilder);

    };
}).call(this);