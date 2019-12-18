//Manager for TeamForm
var TeamForm = function(elem){
    this.$form = elem;
    this.project_id = elem.data('project');
    this.object_id = elem.data('object');
    this.init_wizard();
    this.init_team(this.project_id, this.object_id);
};

TeamForm.prototype.init_wizard = function(){
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
            // Suppress (skip) "Warning" step if the user is old enough and wants to the previous step.
            $('.select2.step' + currentIndex).select2({placeholder: "Select a consultant"});
        },
        onFinishing: function (event, currentIndex)
        {
            var form = $(this);

            // Disable validation on fields that are disabled.
            // At this point it's recommended to do an overall check (mean ignoring only disabled fields)
            form.validate().settings.ignore = ":disabled";

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

            $('.select2.step' + currentIndex).select2({minimumResultsForSearch: Infinity});
        }
    }).validate({
                errorPlacement: function (error, element)
                {
                    element.before(error);
                },
                rules: {
                    'name': 'required',
                    'stream': 'required',
                    'coach': 'required'
                }
            });
};

TeamForm.prototype.init_views = function(){
    // MODALS View for add member and project
    var MemberModalView = Backbone.BootstrapContentModalForm.extend({
        template: templates.team_create_add_member,
        events: {
            'ok': 'submit'
        },
        initialize: function(options){
            this.team = options.team;
        },
        my_validation: function(){
            var name = this.$el.find('#id_member_name').val();
            var email = this.$el.find('#id_email').val();

            if (!name.length) {
                var validator = this.$el.validate();
                validator.showErrors({
                  "member_name": "Name cannot be empty"
                });
                this.set_valid(false);
                return false;
            }

            if (!email.length || !validateEmail(email)) {
                var validator = this.$el.validate();
                validator.showErrors({
                  "email": "You must provide a valid email"
                });
                this.set_valid(false);
                return false;
            }

            if (this.team.exists_member(name, email)){
                var validator = this.$el.validate();
                validator.showErrors({
                  "email": "There is other member with the same email"
                });
                this.set_valid(false);
                return false;
            }
            this.set_valid(true);
            return true;
        },
        submit: function(event){
            event.preventDefault();
            if(this.my_validation()){
                this.save();
            }
        },
        save: function(){
            var name = this.$el.find('#id_member_name').val();
            var email = this.$el.find('#id_email').val();
            this.team.add_member(name, email);
            return true;
        }
    });

    var ExOProjectModalView = Backbone.BootstrapContentModalForm.extend({
        template: templates.team_create_add_project,
        initialize: function(options){
            this.team = options.team;
        },
        save: function(){
            var name = this.$el.find('#id_project_name').val();
            var description = this.$el.find('#id_description').val();
            this.team.add_exo_project(name, description);
        }
    });
    //Generic Views for list and add member and project
    var TeamListView = Backbone.View.extend({
        events: {
            'click #add-item': 'openModal',
            'click .delete': 'delete_item'
        },
        initialize: function(options){
            this.team = options.team;
            this.collection = options.collection;
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
        },
        openModal: function() {
            var view = new this.ModalView({team: this.team});
            var modal = new Backbone.BootstrapModal({
                content: view,
                title: this.title_modal,
                animate: true,
                okText: 'Add'
            });
            modal.open();
        },
        render: function(){
            var container = this.$el.find('table tbody');
            container.empty();
            var pos = 0;
            this.collection.each(function(value){
                var html = this.render_item(value, pos);
                container.append(html);
                pos = pos + 1;
            }, this);
            return this.$el;
        },
        delete_item: function(event){
            var position = $(event.currentTarget).data('pk');
            var user = this.collection.findWhere({position: position});
            this._current_position = position;
            alert_manager.show_message({
                title: "",
                text: "Are you sure to remove " + user.get('short_name') + " from team?",
                type: "warning",
            }, _.bind(this.remove_user_confirm, this));
        },
        remove_user_confirm: function(){
            var position = this._current_position;
            this.team.remove_from_collection(this.collection, position);
        }
    });
    //View for members list
    var MembersView = TeamListView.extend({
        el: '#team-members',
        title_modal: 'Add new member',
        template_table: templates.team_create_member_list,
        ModalView: MemberModalView,
        render_item: function(value, pos){
            var html = this.template_table({
                name: value.get('short_name'),
                email: value.get('email'),
                position: pos,
                pk: value.get('position')
            });
            return html;
        }
    });
    //View for project list
    var ProjectsView = TeamListView.extend({
        el: '#exo-projects',
        title_modal: 'Add new project',
        template_table: templates.team_create_exo_project_list,
        ModalView: ExOProjectModalView,
        render_item: function(value, pos){
            var html = this.template_table({
                name: value.get('name'),
                description: value.get('description'),
                position: pos,
                pk: value.get('position')
            });
            return html;
        }
    });

    return {MembersView: MembersView, ProjectsView: ProjectsView};
};

TeamForm.prototype.init_team = function(project_id, object_id){
    var views = this.init_views();
    var TeamView = Backbone.View.extend({
        el: "#form",
        events:{
            'submit': 'save'
        },
        initialize: function(options){
            if (options.object_id){
                this.team = new Backbone.models.Team({project_id: options.project_id, id: options.object_id});
                this.team.fetch();
            }
            else{
                this.team = new Backbone.models.Team({project_id: options.project_id});
            }
        },
        save: function(event){
            var _self = this;
            event.preventDefault();
            this.team.set('name', this.$el.find('#id_name').val());
            this.team.set('stream', this.$el.find('#id_stream').val());
            this.team.set('coach', this.$el.find('#id_coach').val());
            this.team.set('zoom_id', this.$el.find('#id_zoom_id').val());
            this.team.set('exq_survey', this.$el.find('#id_exq_survey').val());
            this.team.save([],{
                silent: true,
                success: function(model){
                    location.href = _self.$el.data('url-success');
                }
            });
        },
        render: function(){
            this.$el.find('.select2.step0').select2();
            this.members_view = new views.MembersView({
                team: this.team,
                collection: this.team.get('team_members')});
            this.members_view.render();
            this.projects_view = new views.ProjectsView({
                team: this.team,
                collection: this.team.get('exo_projects')
            });
            this.projects_view.render();
        }
    });

    this.team_view = new TeamView({project_id: project_id, object_id: object_id});
    this.team_view.render();
};

$(function(){
    var form = new TeamForm($("#form"));
});

function validateEmail(email) {
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}
