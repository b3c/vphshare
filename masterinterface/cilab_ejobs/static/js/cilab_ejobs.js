;(function($, doc, win) {
  "use strict";

  var name = 'EJob-plugin';

  function EJobPlugin(el, opts) {
    this.$el      = $(el);
    this.$el.data(name, this);
	this.ejob_id = this.$el.attr("id");
	this.ejob_state = parseInt(this.$el.attr("state"));

    this.defaults = {};

    var meta      = this.$el.data(name + '-opts');
    this.opts     = $.extend(this.defaults, opts, meta);

    this.init();
  }

  EJobPlugin.prototype.init = function() {
      var self = this;

      // this has to be the submit function when button pressed
      var el = this.$el.find(".cancel-button");
      if ((self.ejob_state >= 0) && (self.ejob_state <=1)) {

          el.click(function() {
              // console.log(["the id", self.ejob_id],self.getCookie('csrftoken'));

              $.ajax({
                  type:"POST",
                  url:"/ejobs/delete/",
                  dataType: "json",
                  data: {"job_id":self.ejob_id,},
                  success: function(data){
                      self.$el.find(".cancel-button").addClass("disabled");
                      // console.log(["deleted", data]);
                  },
                  fail: function(data){
                      // console.log(["fail", data]);
                  }
              });
          });

      } else {
          el.addClass("disabled");
      }

  };

  // using jQuery
  EJobPlugin.prototype.getCookie = function(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie != '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = jQuery.trim(cookies[i]);
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) == (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
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

