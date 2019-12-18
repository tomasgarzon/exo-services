var InvitationPreviewForm = function($form){
    this.$form = $form;
    this.init_events();
};

InvitationPreviewForm.prototype.init_events = function(){
    var _self = this;
    this.$form.on('click', '.dev__preview_invitation', function(event){
        event.preventDefault();
        var validation_type = $(event.currentTarget).data('type');
        var name = _self.$form.find($('#id_name')).val();
        var custom_text = _self.$form.find($('#id_custom_text')).val();
        _self.get_preview(validation_type, name, custom_text);
    });
    this.$form.find('#id_email').blur(function(){
        var email = $(this).val();
        _self.validateEmail(email);
    });
};

InvitationPreviewForm.prototype.get_preview = function(validation_type, name, custom_text){
    var data = {
        'name': name,
        'validation_type': validation_type,
        'custom_text': custom_text
    };
    $.ajax({
        method: 'GET',
        data: data,
        url: urlservice.resolve('preview-invitation'),
        success: _.bind(this.show_preview, this)
    });
};

InvitationPreviewForm.prototype.show_preview = function(data){
    var view = new window.View.PreviewInvitation({data: data});
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: "Preview of invitation email",
        animate: true,
        okText: 'Close',
        allowCancel: false
    });
    modal.open();
};

InvitationPreviewForm.prototype.validateEmail = function(email){
    var variables = {'email': email};
    var operationName = 'ValidateEmailStatus';
    var query = 'query ValidateEmailStatus($email: String){\n' +
        'allConsultants(user_Email: $email){\n' +
            'edges { \n' +
                'node {\n' +
                    'status\n' +
                    'id\n' +
                    'modified\n' +
                '}\n' +
            '}\n' +
        '}\n' +
    '}';
    var data = {};
    data.variables = JSON.stringify(variables);
    data.query = query;
    data.operationName = operationName;
    $.post("/graphql/", data, _.bind(this.onGraphqlResponse, this));
};

InvitationPreviewForm.prototype.onGraphqlResponse = function(response, status){
    if (response.data.allConsultants.edges.length > 0){
        var node = response.data.allConsultants.edges[0].node;
        if (node.status === 'D') { //If consultant is disabled
            this.showReactiveConsultant(node);
        }
    }

};

InvitationPreviewForm.prototype.showReactiveConsultant = function(consultant){
    var modified = moment(consultant.modified);
    var date = modified.format("MMM D, YYYY");
    alert_manager.show_message({
        title: "Activate old member",
        text: "This consultant was disabled on " + date +". Do you really want to add it again to the Network? All the related information will be restored.",
        type: "warning",
        confirmButtonText: 'Yes, activate'
    }, function(){
        var url = urlservice.resolve('reactive-consultant', consultant.id);
        $.get(url, function(){
            location.href = "/network/list/";
        });
    });
};


$(function(){
    var preview = new InvitationPreviewForm($('#consultant_form'));
});
