var ExOConsultant = function(){
    this.initViews();
    this.initEvents();
};

ExOConsultant.prototype.initViews = function(sprint_id) {
    this.ConsultantModalView = this.initConsultantModalView();

};

ExOConsultant.prototype.initConsultantModalView = function(){
    var _this = this;

    var ConsultantModalView = Backbone.BootstrapContentModalForm.extend({
        template: templates.project_assign_consultant,
        initialize: function(options){
            options = $.extend({}, options);
            this.project = options.project;
            this.consultant = {};
            this.roles = options.roles;
        },
        render: function(){
            var _self = this;
            this.$el.html(this.template({
                roles: this.roles
            }));
            this.$el.find('#id_role.select2').select2();
            this.$el.find('#id_consultant.select2').select2(init_consultant_select2());
            this.$el.find('#id_consultant').on('select2:selecting', function (e) {
                _self.consultant = e.params.args.data;
            });
        },
        save: function(){
            var name = this.consultant.name;
            var email = this.consultant.email;
            var id = this.consultant.id;
            var rol = this.$el.find("#id_role").val();
            var rol_description = this.$el.find('#id_role option:selected').text();
            var url = urlservice.resolve('exo-consultant-project-list', this.project);
            var data = {
                exo_role: parseInt(rol),
                consultant: id
            };
            $.post(
                url,
                data,
                _.bind(this.successSave, this)
            );
        },
        successSave: function(response){
            location.href = ".";
        }
    });

    return ConsultantModalView;
};

ExOConsultant.prototype.initEvents = function(){
    $('.dev__assign_exo_consultant').click(_.bind(this.triggerAddModal, this));
    $('.dev__delete_role').click(_.bind(this.triggerRemoveModal, this));
};

ExOConsultant.prototype.triggerAddModal = function(event){
    var elem = $(event.currentTarget);
    this.project = elem.data('project');
    if (this.roles){
        this.showModal();
    }else {
        this.getRoles(this.project);
    }
};

ExOConsultant.prototype.getRoles = function(project){
    $.get("/api/project/backoffice/"+project+"/customize-roles/", _.bind(this.onRestResponse, this));
};

ExOConsultant.prototype.onRestResponse = function(response){
    this.roles = response;
    this.showModal();
};

ExOConsultant.prototype.showModal = function(){
    var view = new this.ConsultantModalView({
        project: this.project,
        roles: this.roles});
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: "Assign ExO Consultant",
        animate: true,
        okText: 'Save'
    });
    modal.open();
};

ExOConsultant.prototype.triggerRemoveModal = function(event){
    var elem = $(event.currentTarget);
    this.url = elem.data('url');
    var role = elem.data('role');
    alert_manager.show_message({
        title: "",
        text: "Are you sure to remove this ExO Consultant as " + role + "?",
        type: "warning",
        confirmButtonText: 'Yes, remove'
    }, _.bind(this.confirmRemove, this));
};

ExOConsultant.prototype.confirmRemove = function(){
    $.ajax({
        type: 'delete',
        url: this.url,
        success: function(){location.href=".";}
    });
};

$(function(){
    var form = new ExOConsultant();
});
