openerp.product_image_resize = function(instance) {
	var _t = instance.web._t,
	   _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	
	instance.web.form.FieldBinaryImage = instance.web.form.FieldBinary.extend({
	    template: 'FieldBinaryImage',
	    placeholder: "/web/static/src/img/placeholder.png",
	    render_value: function() {
	        var self = this;
	        var url;
	        if (this.get('value') && !instance.web.form.is_bin_size(this.get('value'))) {
	            url = 'data:image/png;base64,' + this.get('value');
	        } else if (this.get('value')) {
	            var id = JSON.stringify(this.view.datarecord.id || null);
	            var field = this.name;
	            if (this.options.preview_image)
	                field = this.options.preview_image;
	            url = this.session.url('/web/binary/image', {
	                                        model: this.view.dataset.model,
	                                        id: id,
	                                        field: field,
	                                        t: (new Date().getTime()),
	            });
	        } else {
	            url = this.placeholder;
	        }
	        var $img = $(QWeb.render("FieldBinaryImage-img", { widget: this, url: url }));
	        this.$el.find('> img').remove();
	        this.$el.prepend($img);
	        $img.load(function() {
	        
			    var active_model = $.bbq.getState().model;
		    	if (active_model=='product.product'){
	            	$img.css("width", "" + 90 + "px");
	            	$img.css("height", "" + 90 + "px");
	            }
	        
	            if (! self.options.size)
	                return;
	            $img.css("max-width", "" + self.options.size[0] + "px");
	            $img.css("max-height", "" + self.options.size[1] + "px");
	            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
	            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
	        });
	        $img.on('error', function() {
	            $img.attr('src', self.placeholder);
	            instance.webclient.notification.warn(_t("Image"), _t("Could not display the selected image."));
	        });
	    },
	    on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
	        this.internal_set_value(file_base64);
	        this.binary_value = true;
	        this.render_value();
	        this.set_filename(name);
	    },
	    on_clear: function() {
	        this._super.apply(this, arguments);
	        this.render_value();
	        this.set_filename('');
	    },
	    set_value: function(value_){
	        var changed = value_ !== this.get_value();
	        this._super.apply(this, arguments);
	        // By default, on binary images read, the server returns the binary size
	        // This is possible that two images have the exact same size
	        // Therefore we trigger the change in case the image value hasn't changed
	        // So the image is re-rendered correctly
	        if (!changed){
	            this.trigger("change:value", this, {
	                oldValue: value_,
	                newValue: value_
	            });
	        }
	    }
	});
}
// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
