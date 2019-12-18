var AssignmentForm = function(form){
    this.form = form;
    this.initEvents();
    var value = this.form.find('#id_type').val();
    this.customizeGenericObject(value);
};

AssignmentForm.prototype.initEvents = function(){
    var _self = this;
    this.form.find('#id_type').change(_.bind(this.onTypeChange, this));
    this.generic_values = [];
    this.form.find('#id_generic_obj option').each(function(index, elem){
        var value = [elem.value, elem.label, elem.selected];
        _self.generic_values.push(value);
    });
};

AssignmentForm.prototype.onTypeChange = function(event){
    var value = $(event.currentTarget).val();
    this.customizeGenericObject(value);
};

AssignmentForm.prototype.customizeOptions = function(contenttype){
    this.form.find('#id_generic_obj option').remove();
    _.each(this.generic_values, function(value, index){
        if (value[0].startsWith('type:' + contenttype)){
            this.form.find('#id_generic_obj').append("<option value='" + value[0] + "'>" + value[1] + "</option>" );
            if (value[2]){
                this.form.find('#id_generic_obj option[value="' + value[0] + '"]').attr('selected', 'selected');
            }
        }
    }, this);
};

AssignmentForm.prototype.customizeGenericObject = function(value){
    if ((value === 'N') || (value === 'Q') || (value === 'B')){
        if (this.form.find('#id_generic_obj').data('select2')){
            this.form.find('#id_generic_obj').select2('destroy');
            this.form.find('#id_generic_obj').hide();
            this.form.find('#id_generic_obj').parent().hide();
            this.form.find('#id_generic_obj').removeProp('required');
            this.form.find('#id_generic_obj').parent().removeClass('required');
        }
        this.customizeOptions('');
    } else if (value === 'E'){
        this.customizeOptions('evaluation_evaluation');
        this.form.find('#id_generic_obj').prop('required');
        this.form.find('#id_generic_obj').select2({placeholder: 'Select Evaluation form'});
        this.form.find('#id_generic_obj').data('select2').$container.show();
        this.form.find('#id_generic_obj').data('select2').$container.parent().show();
        this.form.find('#id_generic_obj').data('select2').$container.parent().find('label').html("Select Evaluation form");
        this.form.find('#id_generic_obj').data('select2').$container.parent().addClass('required');
    }
};


$(function(){
    $('#form .select2').select2();
    var form = new AssignmentForm($('#form'));
    $('textarea#id_content, textarea#id_tips').markdown({
        autofocus:false,
        savable:false});
});
