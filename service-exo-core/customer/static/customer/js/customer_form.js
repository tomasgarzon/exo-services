// Functions for Select2 for Organization
function formatRepo (repo) {
    return repo.name;
}

function formatRepoSelection (repo) {
  return repo.name;
}

//Manager for CustomerForm
var CustomerForm = function(elem){
    this.CH_ORGANIZATION = 'organization';
    this.$form = elem;
    this.init_wizard();
    this.init_widgets();
};

CustomerForm.prototype.init_wizard = function(){
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
        onStepChanged: function (event, currentIndex, priorIndex)
        {
            if (currentIndex === 1){
                $(this).find('#id_country2').select2({placeholder: 'Select a country'});
                $(this).find('#id_timezone').select2({placeholder: 'Select a timezone'});
            }
            if (currentIndex === 2){
                $(this).find('#id_industry').select2({placeholder: 'Select an industry'});
                $(this).find('#id_size').select2({placeholder: 'Select a size'});
            }
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

CustomerForm.prototype.init_widgets = function(){
    //Init widget for checkbox and integer values
    var _self = this;
    this.$source = this.$form.find('.i-checks');
    this.$source.iCheck(icheck_options.get_defaults());
    this.show_organization();
    this.$form.find('#id_partner').select2({placeholder: 'Select a partner'});
    this.$form.find('#id_profile_picture').change(function (){
        var filename = _self.$form.find('#id_profile_picture').val();
        _self.$form.find('#filename-logo').html(filename.split('\\').pop());
    });
    this.init_location();
};

CustomerForm.prototype.show_organization = function(){
    //Show organization select and generate select2
    var _self = this;
    this.$organization = this.$form.find("#id_organization");
    this.$organization.select2({placeholder: 'Organization name'});
    //When user select, load information from URL
    this.$organization.on('select2:select', function(event){
        var id = event.params.data.id;
        var url = urlservice.resolve('api-organization-detail', [id]);
        _self.load_from_organization(url);
        _self.$form.find("#id_organization_id").val(event.params.data.id);
    });
};

CustomerForm.prototype.hide_organization = function(){
    //Hide select for organization
    this.$organization = this.$form.find(".js-data-organization-ajax");
    this.$organization_container = this.$form.find('.js-organization-container');
    this.$organization.select2('destroy');
    this.$form.find("#id_organization_id").val("");
    this.$organization_container.addClass('hide');
    this.$organization.rules('remove', 'required'); //Remove rule
};

CustomerForm.prototype.load_from_organization = function(url){
    //Load json information from organization and put it into the current form
    var _self = this;
    var $form = this.$form;
    $.get(url, function(data){
        _.each(data, function(value, key){
            // temporal hack, country to country2
            if (key === 'country'){
                key = 'country2';
            }
            $form.find("[name=" + key + "]").val(value);
        });
        $form.find("#dev__exq").html(data.exq);
        if (data.exq < 1){ // Default value
            $form.find("#dev__exq").html("Pending");
        }
    });
};

CustomerForm.prototype.init_location = function(){
    var elem = document.getElementById('id_location');
    var autocomplete = new google.maps.places.Autocomplete(elem, {'types': ['(regions)']});
    autocomplete.setFields(['formatted_address', 'place_id']);

    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        document.getElementById("id_place_id").value = place.place_id;
    });
};

$(function(){
    var form = new CustomerForm($("#customer-form"));
});
