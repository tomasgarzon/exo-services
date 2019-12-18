//Manager for PartnerForm
var PartnerForm = function(elem){
    this.$form = elem;
    this.init_wizard();
    this.init_widgets();
};

PartnerForm.prototype.init_wizard = function(){
    //Initialize wizard, based on django form.
    this.$form.steps({
        bodyTag: "fieldset",
        enableCancelButton: true,
        labels: {
            finish: 'Save'
        },
        onStepChanging: function (event, currentIndex, newIndex)
        {
            // Always allow going backward even if the current step contains invalid fields!
            if (currentIndex > newIndex)
            {
                return true;
            }

            var form = $(this);

            // Clean up if user went backward before
            if (currentIndex < newIndex)
            {
                // To remove error styles
                $(".body:eq(" + newIndex + ") label.error", form).remove();
                $(".body:eq(" + newIndex + ") .error", form).removeClass("error");
            }

            // Disable validation on fields that are disabled or hidden.
            form.validate().settings.ignore = ":disabled,:hidden";

            // Start validation; Prevent going forward if false
            return form.valid();
        },
        onFinishing: function (event, currentIndex)
        {
            var form = $(this);

            // Disable validation on fields that are disabled.
            // At this point it's recommended to do an overall check (mean ignoring only disabled fields)
            form.validate().settings.ignore = ":disabled,:hidden";

            // Start validation; Prevent form submission if false
            return form.valid();
        },
        onFinished: function (event, currentIndex)
        {
            var form = $(this);

            // Submit form input
            form.submit();
        },
        onCanceled: function(event, currentIndex){
            var form = $(this);
            location.href = form.data('url-cancel');
        },
        onInit: function(event, currentIndex){
            var form = $(this);
            var parent = form.find('.actions ul');
            var elem = form.find('.actions ul li a[href=#cancel]').parent();
            move_to_first(parent, elem);
        }
    }).validate({
                errorPlacement: function (error, element)
                {
                    element.before(error);
                },
                rules: {}
            });
};

PartnerForm.prototype.init_widgets = function(){
    //Init widget for checkbox and integer values
    var _self = this;
    this.$form.find('#id_profile_picture').change(function (){
        var filename = _self.$form.find('#id_profile_picture').val();
        _self.$form.find('#filename-logo').html(filename.split('\\').pop());
    });
    this.init_location();
};

PartnerForm.prototype.init_location = function(){
    var elem = document.getElementById('id_location');
    var autocomplete = new google.maps.places.Autocomplete(elem, {'types': ['(regions)']});
    autocomplete.setFields(['formatted_address', 'place_id']);

    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        document.getElementById("id_place_id").value = place.place_id;
    });
};


$(function(){
    var form = new PartnerForm($("#customer-form"));
});
