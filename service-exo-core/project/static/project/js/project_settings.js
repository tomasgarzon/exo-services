var ProjectForm = function(){
    this.initWidgets();
    this.initEvents();
    this.initObserverView();
};

ProjectForm.prototype.initWidgets = function(){
    $('.ichecks').iCheck(icheck_options.get_defaults());
    $('#id_bulk_actions').select2();

};

ProjectForm.prototype.initEvents = function(){
    $('#dev__add_observer').click(_.bind(this.openAddObserver, this));
    $('#dev__add_staff').click(_.bind(this.openAddStaff, this));
    $('#dev__add_ticket_manager').click(_.bind(this.openAddTicketManager, this));
    $('#dev__apply_bulk').click(_.bind(this.processBulkActions, this));
    $('.dev__remove').click(_.bind(this.triggerRemoveModal, this));
    $('#id_template_assignments').change(_.bind(this.triggerTemplateAssignmentsChange, this));
};

ProjectForm.prototype.initObserverView = function(){
    var _this = this;

    this.UserModalView = Backbone.BootstrapContentModalForm.extend({
        template: templates.team_create_add_member,
        initialize: function(options){
            options = $.extend({}, options);
            this.project = options.project;
            this.exo_role = options.exo_role;
        },
        render: function(){
            var _self = this;
            this.$el.html(this.template());
        },
        save: function(){
            var name = this.$el.find('#id_member_name').val();
            var email = this.$el.find('#id_email').val();
            var url = urlservice.resolve('user-roles', this.project);
            var data = {
                name: name,
                email: email,
                exo_role: this.exo_role
            };

            $.ajax({
                method: 'POST',
                data: data,
                url: url,
                success: _.bind(this.successSave, this),
                error: _.bind(this.errorSave, this)
            });
        },
        successSave: function(response){
            location.href = ".";
        },
        errorSave: function(response, data){      
            try {
                var message = response.responseJSON.email[0];
            } catch (e) {
                var message = 'Error';
            }

            toastr_manager.show_message('error', '', message);
        }
    });

    return this.UserModalView;
};

ProjectForm.prototype._openModalForm = function(project, exo_role, title, okText){
    var view = new this.UserModalView({
        project: project,
        exo_role: exo_role});
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: title,
        animate: true,
        okText: okText
    });
    modal.open();
};

ProjectForm.prototype.openAddObserver = function(event){
    this._openModalForm(
        $(event.currentTarget).data('project'),
        'SOB',
        "Add new observer",
        "Add");
};

ProjectForm.prototype.openAddTicketManager = function(event){
    this._openModalForm(
        $(event.currentTarget).data('project'),
        'SDM',
        "Add new Delivery Manager",
        "Add");
};

ProjectForm.prototype.openAddStaff = function(event){
    this._openModalForm(
        $(event.currentTarget).data('project'),
        'SOT',
        "Add new ExO Works Staff",
        "Add");
};

ProjectForm.prototype.processBulkActions = function(event){
    event.preventDefault();
    var action = $('#id_bulk_actions').val();
    $("[name=observer]:checked").each(function(index, elem){
        var $elem = $(elem);
        if (action === 'send_invitation'){
            var invitation_id = $elem.val();
            $.ajax({
                type: 'put',
                url: urlservice.resolve('resend-invitation', invitation_id),
                success: function(){
                    toastr_manager.show_message(
                        'success', '',
                        'Invitation sent successfully');
                }
            });
        }
    });
};

ProjectForm.prototype.triggerRemoveModal = function(event){
    event.preventDefault();
    var elem = $(event.currentTarget);
    var user_project_id = elem.data('pk');
    var project_id = elem.data('project');
    var role_name = elem.data('role');
    this.url = urlservice.resolve('user-roles-detail', project_id, user_project_id);
    alert_manager.show_message({
        title: "",
        text: "Are you sure to remove this " + role_name + "?",
        type: "warning",
        confirmButtonText: 'Yes, remove'
    }, _.bind(this.confirmRemove, this));
};

ProjectForm.prototype.confirmRemove = function(){
    $.ajax({
        type: 'delete',
        url: this.url,
        success: function(){location.href=".";}
    });
};

ProjectForm.prototype.triggerTemplateAssignmentsChange = function(event) {
    if (!event.target.value) {
        alert('Assignments will be removed after saving Settings information');
    } else {
        var option_selected = $(event.target).find('option:selected').text();
        alert('Assignments will be populated with: ' + option_selected);
    }
}

$(function(){
    var project = new ProjectForm();
});
