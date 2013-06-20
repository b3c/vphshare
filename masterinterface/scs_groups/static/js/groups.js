
(function() {
    var global = this;
    var $ = global.$;
    var console = global.console || {log:function() {}};

    var GroupItem = global.GroupItem = function(element, options) {
        return 0;
    };


    var GroupsList = global.GroupsList = function(element, options) {
        this.$destinationList = element;
        this.$groups = element.clone().hide();
        this.inizialize();
    };

    GroupsList.prototype.inizialize = function(){
        var self = this;
        this.$allButton = $('#all-filter');
        this.$institutionButton = $('#institution-filter');
        this.$smartButton = $('#smart-filter');
        this.$studiesButton = $('#studies-filter');

        this.$allButton.click(function(e){self.allFilter(e);});
        this.$institutionButton.click(function(e){self.institutionFilter(e);});
        this.$smartButton.click(function(e){self.smartFilter(e);});
        this.$studiesButton.click(function(e){self.studiesFilter(e);});
        $('a[data-toggle="tab"]').on('shown',self.hideTab3);

    };

    GroupsList.prototype.hideTab3 = function(e){
        if (e.target.hash == '#lB'){
            $('.main-item-tab3').show();
        }else{
            $('.main-item-tab3').hide();
        }

        $(".nano").nanoScroller({ alwaysVisible: true });

    };

    GroupsList.prototype.allFilter = function(e){
        var self = this;
        this.$destinationList.quicksand(
            self.$groups.find('li'),
            { duration: 1000 }
        );
        e.preventDefault();
    };

    GroupsList.prototype.institutionFilter = function(e){
        var self = this;
        this.$destinationList.quicksand(
            self.$groups.find('.group-institution'),
            { duration: 1000 }
        );
        e.preventDefault();
    };

    GroupsList.prototype.smartFilter = function(e){
        var self = this;
        this.$destinationList.quicksand(
            self.$groups.find('.group-smart'),
            { duration: 1000 }
        );
        e.preventDefault();
    };

    GroupsList.prototype.studiesFilter = function(e){
        var self = this;
        this.$destinationList.quicksand(
            self.$groups.find('.group-study'),
            { duration: 1000 }
        );
        e.preventDefault();
    };

    GroupsList.autoDiscover = function(options) {
        var groupslist = $( '.groups-list');
        new GroupsList(groupslist);

    };
}).call(this);
