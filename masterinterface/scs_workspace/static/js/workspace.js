;(function($, doc, win) {
    "use strict";

    var name = 'custominput-plugin';

    function CustomInputPlugin(el, opts) {
        this.$el      = $(el);
        this.$el.data(name, this);

        this.defaults = {"CustomValueFromInput": "",
                        "WorkflowOutFolderPath": "VPHSHARE_RUN_OUTPUT_FOLDER",
                        "elem_prefix": "CustomInput"};

        var meta      = this.$el.data(name + '-opts');
        this.opts     = $.extend(this.defaults, opts, meta);

        this.init();
    }

    CustomInputPlugin.prototype.init = function() {
        var self = this;

        this.$el.change(function() {
            var changed = $(this).val();
            var customId = $(this).attr(name+'-val')
            var str_id = '#'+ self.opts.elem_prefix +'-'+ customId;

            if (changed in self.opts) {

                if (self.opts[changed] != "") {
                    $(str_id).val(self.opts[changed]);
                } else {
                    $(str_id).val("");
                }

                $(str_id).removeClass("hidden");
            } else {
                $(str_id).addClass("hidden");
                $(str_id).val("");
            }
        });

    };

    CustomInputPlugin.prototype.destroy = function() {
        this.$el.off('.' + name);
        this.$el.find('*').off('.' + name);
        this.$el.removeData(name);
        this.$el = null;
    };

    $.fn.CustomInputPlugin = function(opts) {
        return this.each(function() {
            new CustomInputPlugin(this, opts);
        });
    };

    $(doc).on('dom_loaded ajax_loaded', function(e, nodes) {
        var $nodes = $(nodes);
        var $elements = $nodes.find('.' + name);
        $elements = $elements.add($nodes.filter('.' + name));

        $elements.CustomInputPlugin();
    });

})(jQuery, document, window);

