;(function($, doc, win) {
  "use strict";

  var name = 'EJob-plugin';

  function EJobPlugin(el, opts) {
    this.$el      = $(el);
    this.$el.data(name, this);
	this.ejob_id = this.$el.attr("id");

    this.defaults = {};

    var meta      = this.$el.data(name + '-opts');
    this.opts     = $.extend(this.defaults, opts, meta);

    this.init();
  }

  EJobPlugin.prototype.init = function() {
	  var self = this;

      // this has to be the submit function when button pressed
      this.$el.find(".cancel-button").click(function() {
          system.log(["the id", self.ejob_id])
      });

  };

  EJobPlugin.prototype.destroy = function() {
    this.$el.off('.' + name);
    this.$el.find('*').off('.' + name);
    this.$el.removeData(name);
    this.$el = null;
  };

  $.fn.EJobPlugin = function(opts) {
    return this.each(function() {
      new EJobPlugin(this, opts);
    });
  };

  $(doc).on('dom_loaded ajax_loaded', function(e, nodes) {
    var $nodes = $(nodes);
    var $elements = $nodes.find('.' + name);
    $elements = $elements.add($nodes.filter('.' + name));

    $elements.EJobPlugin();
  });

})(jQuery, document, window);

