
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
        this.$allButton.click(function(e){self.allFilter(e);});
        this.$institutionButton.click(function(e){self.institutionFilter(e);});
        this.$smartButton.click(function(e){self.smartFilter(e);});
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

    GroupsList.autoDiscover = function(options) {
        var groupslist = $( '.groups-list');
        new GroupsList(groupslist);

    };
}).call(this);


(function() {
    var global = this;
    var $ = global.$;
    var console = global.console || {log: function() {}};

    var CicuWidget = global.CicuWidget = function(element, options) {
        this.options = {
            modalButtonLabel : 'Upload image',
            changeButtonText : 'Change Image',
            sizeAlertMessage : 'Warning: the area selected is little, min size:',
            sizeErrorMessage : "Image don't have minimal size",
            modalSaveCropMessage: 'Set image',
            modalCloseCropMessage: 'Close',
            uploadingMessage : 'Uploading your image',
            fileUploadLabel : 'Select image from your computer',
            sizeWarning : 'True',
            ratioWidth :'800',
            ratioHeight :'600',
            onUpload: null,
            onComplete: null,
            onError: null,
            onRemove: null,
            onCrop: null
        };
        $.extend(this.options, options);
        this.$element = $(element);
        $('label[for='+this.$element.attr('id')+']:first').removeAttr('for');
        this.initialize();
    };

    CicuWidget.prototype.DjangoCicuError = function(message) {
        this.name = 'DjangoCicuError';
        this.message = message;
    };

    CicuWidget.prototype.showMessage = function(message){
        this.$warningSize.html(message+'<a class="close" data-dismiss="alert" href="#">&times;</a>').show();
    };

    CicuWidget.prototype.DjangoCicuError.prototype = new Error();
    CicuWidget.prototype.DjangoCicuError.prototype.constructor = CicuWidget.prototype.DjangoCicuError;

    CicuWidget.prototype.initialize = function() {
        var self = this;
        this.name = this.$element.attr('name');
        this.$modalButton = $('<a href="#uploadModal" role="button" class="btn upload-btn" data-toggle="modal">'+this.options['modalButtonLabel']+'</a>');
        this.$croppedImagePreview = $('<div class="cropped-imag-preview"><img src="'+this.$element.data('filename')+'"/></div>');
        this.$croppedImagePreview.append(this.$modalButton);
        this.$element.after(this.$croppedImagePreview);

        this.$modalWindow = $('<div id="uploadModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">' +
            '<div id="uploadModalBody" class="modal-body image-body-modal">' +
            '' +
            '</div>' +
            '<div class="modal-footer">' +
            '<button class="btn" data-dismiss="modal" aria-hidden="true">'+this.options.modalCloseCropMessage+'</button>' +
            '<button id="modal-set-image-button" class="btn btn-primary disabled">'+this.options.modalSaveCropMessage+'</button>' +
            '</div>' +
            '</div>');

        this.$element.after(this.$modalWindow);
        this.$uploadModalBody = $('#uploadModalBody');
        this.$warningSize = $('<div id="warning-size-message" class="alert alert-error hide"></div>');

        this.$uploadModalBody.before(this.$warningSize);
        // Create a hidden field to contain our uploaded file name
        this.$hiddenElement = $('<input type="hidden"/>')
            .attr('name', this.name)
            .val(this.$element.data('filename'));
        this.$element.attr('name', ''); // because we don't want to conflict with our hidden field
        this.$element.after(this.$hiddenElement);

        // Initialize preview area and action buttons
        this.$previewArea = $('<div class="ajax-upload-preview-area"></div>');
        this.$uploadModalBody.append(this.$previewArea);

        // Listen for when a file is selected, and perform upload
        this.$element.on('change', function() {
            self.upload();
        });
        this.$uploadButton = $('<div class="fileupload fileupload-new" data-provides="fileupload"><span class="btn btn-file">' +
            '<span id="file-upload-label" class="fileupload-new" data-loading-text="Uploading your image...">'+this.options.fileUploadLabel+'</span></span>'+
            '</div>');
        this.$uploadModalBody.append(this.$uploadButton);
        this.$fileUploadLabel = $('#file-upload-label');
        $( '.btn-file' ).append(this.$element);
        this.$modalSetImageButton = $('#modal-set-image-button');
        this.$modalSetImageButton.on( 'click' , function(){
            if (!$(this).hasClass('disabled')){
                self.setCrop();
            }
            return false;
        });
    };
    CicuWidget.prototype.setCrop = function() {
        var self = this;

        $.ajax(this.$element.data('crop-url'), {
            iframe : true,
            data : {cropping : this.$cropping.val(),
                id : this.$hiddenElement.data('imageId')},
            type: 'POST',
            dataType: 'json',
            success: function(data) { self.cropDone(data); },
            error: function(data) { self.cropFail(data); }
        });

    };

    CicuWidget.prototype.cropDone = function(data) {
        // This handles errors as well because iframe transport does not
        // distinguish between 200 response and other errors
        if(data.errors) {
            if(this.options.onError) {
                this.options.onError.call(this, data);
            } else {
                console.log('Crop failed:');
                console.log(data);
            }
        } else {
            this.$hiddenElement.val(data.id);
            this.$croppedImagePreview.children('img:first').attr('src',data.path);
            this.$modalWindow.modal('hide');
        }
        if(this.options.onCrop) {
            var result = this.options.onUpload.call(this);
            if(result === false)
                return;
        }
    };

    CicuWidget.prototype.cropFail = function(xhr) {
        if(this.options.onError) {
            this.options.onError.call(this);
        } else {
            console.log('Crop failed:');
            console.log(xhr);
            this.showMessage('Crop failed!');
        }
    };

    CicuWidget.prototype.upload = function() {
        var self = this;
        if(!this.$element.val()) return;
        this.$fileUploadLabel.button('loading');
        this.$fileUploadLabel.addClass('disabled');
        if(this.options.onUpload) {
            var result = this.options.onUpload.call(this);
            if(result === false) return;
        }
        this.$element.attr('name', 'file');
        $.ajax(this.$element.data('upload-url'), {
            iframe: true,
            files: this.$element,
            processData: false,
            type: 'POST',
            dataType: 'json',
            success: function(data) { self.uploadDone(data); },
            error: function(data) { self.uploadFail(data); }
        });
    };

    CicuWidget.prototype.uploadDone = function(data) {
        // This handles errors as well because iframe transport does not
        // distinguish between 200 response and other errors
        this.$fileUploadLabel.removeClass('disabled');
        this.$fileUploadLabel.button('reset');
        if(data.errors) {
            if(this.options.onError) {
                this.options.onError.call(this, data);
            } else {
                console.log('Upload failed:');
                console.log(data);
            }
        } else {
            if ((data.width < this.options.ratioWidth || data.height < this.options.ratioHeight) && this.options.sizeWarning == 'True' ){

                this.showMessage(this.options.sizeErrorMessage+this.options.ratioWidth+"x"+this.options.ratioHeight);


                if (this.options.sizeWarning == "True"){
                    this.$fileUploadLabel.text(this.options.fileUploadLabel);
                    this.$hiddenElement.data('imageId','');
                    this.$hiddenElement.data('imagePath','');
                }

            }else{
                this.$orgWidth = data.width;
                this.$orgHeight = data.height;
                this.$hiddenElement.data('imageId',data.id);
                this.$hiddenElement.data('imagePath',data.path);
                this.$fileUploadLabel.text(this.options.changeButtonText);
                this.$modalSetImageButton.removeClass('disabled');
            }
            var tmp = this.$element;
            this.$element = this.$element.clone(true).val('');
            tmp.replaceWith(this.$element);
            this.displaySelection();
            if(this.options.onComplete) this.options.onComplete.call(this, data.path);

        }
    };

    CicuWidget.prototype.uploadFail = function(xhr) {
        if(this.options.onError) {
            this.options.onError.call(this);
        } else {
            console.log('Upload failed:');
            console.log(xhr);
            this.showMessage('Upload failed');
        }
    };

    CicuWidget.prototype.displaySelection = function() {
        var filename = this.$hiddenElement.data('imagePath');

        if(filename !== '') {
            this.$previewArea.empty();
            this.$previewArea.append(this.generateFilePreview(filename));
            image_cropping.init(this);
            this.$cropping = $('#id_cropping' );
            this.$uploadModalBody.removeClass( 'image-body-modal' );
            this.$previewArea.show();

        } else {
            this.$uploadModalBody.addClass( 'image-body-modal' );
            this.$previewArea.slideUp();
            this.$element.show();
        }
    };

    CicuWidget.prototype.generateFilePreview = function(filename) {
        // Returns the html output for displaying the given uploaded filename to the user.
        var output = '', width = this.$orgWidth , height = this.$orgHeight;
        var $self = this;
        $.each(['jpg', 'jpeg', 'png', 'gif'], function(i, ext) {
            if(filename.toLowerCase().slice(-ext.length) == ext) {
                var crop_input = '<input data-size-warning="'+$self.options.sizeWarning+'"  data-width="'+$self.options.ratioWidth+'" data-height="'+$self.options.ratioHeight+'"  data-allow-fullsize="false" name="cropping" maxlength="255" value="300,100,600,600" class="image-ratio" data-image-field="image_field" id="id_cropping" data-adapt-rotation="false" type="text" data-my-name="cropping" style="display: none;" />';
                output += '<input data-org-width="'+width+'" data-org-height="'+height+'" data-field-name="image_field" class="crop-thumb hide" src="'+filename+'"  data-thumbnail-url="'+filename+'" />' + crop_input;
                return false;
            }
        });
        output += '';
        return output;
    };

    CicuWidget.autoDiscover = function(options) {
        var cicuOptions = $( '#cicu-options');
        options =  cicuOptions.data();
        cicuOptions.remove();
        $('input[type="file"].ajax-upload').each(function(index, element) {
            new CicuWidget(element, options);
        });
    };
}).call(this);
