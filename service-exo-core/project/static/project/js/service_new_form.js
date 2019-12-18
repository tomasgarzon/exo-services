$(function(){
    var view = new NewServicePopup($('a#add_service'));
});


var NewServicePopup = function(button){
    this.button_tag = button;
    this.__init__();
};

NewServicePopup.prototype.__init__ = function(){
    this.button_tag.on('click', _.bind(this.open_modal, this));
};

NewServicePopup.prototype.open_modal = function(){

    this.view = new ServiceViewForm();
    this.modal = new Backbone.BootstrapModal({
        content: this.view,
        title: 'Add new project',
        animate: true,
        okText: 'Save'
    });

    this.modal.open();

};

var ServiceViewForm = Backbone.BootstrapContentModalForm.extend({
    template: templates.new_service_form,
    initialize: function(options){
        var options = $.extend({}, options);
    },
    render: function(){
        this.$el.html(this.template({
            can_add_automated: $("#project-list-detail").data("automated")
        }));
        this.$el.find('select#partner').select2();
        this.$el.find('select#id_type_project,select#id_step_unit').select2();
        this.$el.find('#id_type_project').on("select2:select", _.bind(this.onChangeTypeProject, this));
        this.$el.find('#id_has_partner').select2();
        this.$el.find('#id_has_partner').on("select2:select", _.bind(this.onChangeHasPartner, this));
        this.$el.find('#partner').on("select2:select", _.bind(this.onChangePartner, this));
    },
    save: function(){
        data = {
            'name': this.$el.find('input#id_name').val(),
            'type_project': this.$el.find('#id_type_project').val(),
            'duration': this.$el.find('#id_duration').val(),
            'lapse': this.$el.find('#id_step_unit').val(),
            'partner': this.$el.find('select#partner').val(),
            'customer': this.$el.find('select#customer').val()
        };
        $.ajax({
            url: urlservice.resolve('create-service'),
            data: data,
            method: 'post',
            success: _.bind(this.success, this),
            error: _.bind(this.errors, this)
        });
    },
    onChangeTypeProject: function(event){
        var value = this.$el.find('#id_type_project').val();
        switch(value){
            case 'sprint':
                this.$el.find('#id_duration').val(10);
                this.$el.find('#id_step_unit').val('W').trigger("change");
                break;
            case 'sprintautomated':
                this.$el.find('#id_duration').val(14);
                this.$el.find('#id_step_unit').val('P').trigger("change");
                this.$el.find('#id_has_partner').val("no").trigger("change").trigger("select2:select");
                break;
            case 'workshop':
                this.$el.find('#id_duration').val(3);
                this.$el.find('#id_step_unit').val('D').trigger("change");
                break;
            case 'fastracksprint':
                this.$el.find('#id_duration').val(0);
                this.$el.find('#id_step_unit').val('N').trigger("change");
        }
    },
    onChangeHasPartner: function(event){
        var value = this.$el.find('#id_has_partner').val();
        this.$el.find('select#customer').val("").trigger('change');
        if (value === 'yes'){
            this.$el.find('select#partner').select2(init_partners_select2());
            this.$el.find('select#partner').attr('required', 'required');
            this.$el.find("#dev__partner").removeClass('hide');
            this.$el.find("#dev__customer").addClass('hide');
        } else {
            this.$el.find('select#partner').select2('destroy');
            this.$el.find('select#partner').val("").trigger('change');
            this.$el.find("#dev__partner").addClass('hide');
            this.$el.find('select#partner').removeAttr('required');
            this.$el.find("#dev__customer").removeClass('hide');
            this.$el.find('select#customer').select2(init_customers_select2());
        }
    },
    onChangePartner: function(event){
        var value = this.$el.find('#partner').val();
        this.$el.find('select#customer').val("").trigger('change');
        this.$el.find('select#customer').select2(init_customers_select2(value));
        this.$el.find("#dev__customer").removeClass('hide');
    },
    success: function(data){
        location.href = '/project/' + data.id + '/';
    },
    errors: function(){

    }
});
