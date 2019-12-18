//Manager for SprintForm
var SprintForm = function(elem){
    this.$form = elem;

    this.excluded_roles = {'name': 'Head Coach'};
    this.init_wizard();
    this.init_views(this.$form.data('object'));
    this.init_widgets();
};

SprintForm.prototype.init_widgets = function(){
    $('.select2#id_customer').select2({placeholder:'Select a customer'});
    $('.select2#id_project_manager').select2(
        _.extend(
            init_consultant_select2(),
            {placeholder: "Select an ExO Consultant"})
    );
    $('#id_start').datepicker(datepicker.options);
};

SprintForm.prototype.init_wizard = function(){
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
        }
    }).validate(
        {
        errorPlacement: function (error, element)
            {
                element.before(error);
            },
        rules: {
        }
    });
};

SprintForm.prototype.init_views = function(sprint_id) {
    var ConsultantModalView = this.init_ConsultantModalView();
    var ExoConsultantView = this.init_ExoConsultantView(ConsultantModalView);

    var MembersModalView = this.init_MembersModalView();
    var CustomerMemberView = this.init_CustomerMemberView(MembersModalView);

    var SprintView = this.init_sprintView(ExoConsultantView,
                                          CustomerMemberView);

    if (sprint_id !== undefined){
        this.sprint_view = new SprintView({sprint_id: sprint_id});
    } else {
        this.sprint_view = new SprintView();
        this.sprint_view.render();
    }
};

SprintForm.prototype.init_ConsultantModalView = function(){
    var _this = this;

    var ConsultantModalView = Backbone.BootstrapContentModalForm.extend({
        template: templates.sprint_assign_consultant,
        initialize: function(options){
            var options = $.extend({}, options);
            this.sprint = options.sprint;
            this.consultant = {};
            this.roles = _(options.roles.reject(_this.excluded_roles));
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
            this.sprint.add_consultant(name, email, parseInt(rol), rol_description, id, undefined, this.consultant.thumbnail);
        }
    });

    return ConsultantModalView;
};

SprintForm.prototype.init_ExoConsultantView = function(ConsultantModalView){

    var _this = this;

    var ExoConsultantView = Backbone.View.extend({
        el: '#consultants',
        template_table: templates.sprint_list_exoconsultant,
        events:{
            'click #add-new': 'openModal',
            'click .delete': 'delete_item'
        },
        initialize: function(options){
            var options = $.extend({}, options);
            this.sprint_form = _this;
            this.sprint = options.sprint;
            this.collection = options.collection;
            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);

            this.$el.find('#id_project_manager').on(
                'select2:selecting',
                _.bind(this.change_head_coach, this));

            this.roles = new window.Collection.Role();
            this.roles.fetched = false;
        },
        change_head_coach: function(e){
            var id = e.params.args.data.id;
            var name = e.params.args.data.name;
            var email = e.params.args.data.email;
            var role = this.roles.get_manager();
            this.sprint.change_head_coach(id, name, email, role);
        },
        openModal: function() {
            var view = new ConsultantModalView({
                sprint: this.sprint,
                roles: this.roles});
            var modal = new Backbone.BootstrapModal({
                content: view,
                title: "Assign ExO Consultant",
                animate: true,
                okText: 'Save'
            });
            modal.open();
        },
        render: function(){
            if (!this.roles.fetched){
                this.roles.fetch({
                    data: {'id': 1},
                    success: _.bind(this.readyForRender, this)
                });
            }
            else{
                this.readyForRender();
            }
            return this.$el;
        },
        readyForRender: function(){
            this.roles.fetched = true;
            var container = this.$el.find('table tbody');
            container.empty();
            var pos = 0;
            var managers = 0;
            var rendered = {};
            this.collection.each(function(value){
                if(!rendered.hasOwnProperty(value.get('email'))){
                    rendered[value.get('email')] = null;
                    if(this.sprint_form.excluded_roles.name != value.get('role_description')){
                        var html = this.render_item(value, pos);
                        container.append(html);
                        pos = pos + 1;
                    }
                    var role = this.roles.findWhere({id: value.get('role')});
                    if (role.get('code') === settings.relation.CONSULTANT_CH_MANAGER){
                        managers = managers+1;
                    }
                }
            }, this);
            this.sprint.set('managers', managers);
        },
        render_item: function(value, pos){
            var consultors = this.collection.filter({'email': value.get('email')});
            var consultor_data = {
                'name': value.get('name'),
                'email': value.get('email'),
                'url_profile': value.get('url_profile'),
                'thumbnail': value.get('thumbnail'),
                'roles': []
            };
            _.each(consultors, function(consultor, index){
                var new_role = {
                    'role_display': consultor.get_role_display(),
                    'position': consultor.get('position'),
                    'can_delete': consultor.can_delete()
                };
                consultor_data['roles'].push(new_role);
            });
            var html = this.template_table({'value': consultor_data});
            return html;
        },
        delete_item: function(event){
            var _self = this;
            var position = $(event.currentTarget).data('pk');
            var consultant = this.sprint.get('consultants_roles').findWhere({position: position});
            this._current_consultant = consultant;
            alert_manager.show_message({
                title: "",
                text: "Are you sure to remove " + consultant.get('name') + " as " + consultant.get_role_display() +"?",
                type: "warning",
            }, _.bind(this.remove_consultant_confirm, this));
        },
        remove_consultant_confirm: function(inputValue) {
            if (inputValue===true){
                this.sprint.remove_consultant(this._current_consultant.get('position'));
            }
        }
    });

    return ExoConsultantView;
};

SprintForm.prototype.init_MembersModalView = function(){
    var _this = this;

    var MemberModalView = Backbone.BootstrapContentModalForm.extend({
        template: templates.team_create_add_member,
        events: {
            'ok': 'submit'
        },
        initialize: function(options){
            option = _.extend({}, options);
            this.sprint_form = _this;
            this.sprint = options.sprint;
        },
        my_validation: function(){
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
            this.sprint.add_member(name, email);
            return true;
        }
    });

    return MemberModalView;
};

SprintForm.prototype.init_CustomerMemberView = function(MemberModalView){

    var CustomerMemberView = Backbone.View.extend({
        el: '#members',
        template_table: templates.customer_member_list,
        events:{
            'click #add-new': 'openModal',
            'click .delete': 'delete_item'
        },
        initialize: function(options){
            var options = $.extend({}, options);
            this.sprint = options.sprint;
            this.collection = options.collection;

            this.listenTo(this.collection, 'add', this.render);
            this.listenTo(this.collection, 'remove', this.render);
            this.render();
        },
        openModal: function() {
            var view = new MemberModalView({sprint: this.sprint});
            var modal = new Backbone.BootstrapModal({
                content: view,
                title: "Add customer member",
                animate: true,
                okText: 'Save'
            });
            modal.open();
        },
        render: function(){
            this.readyForRender();
            return this.$el;
        },
        readyForRender: function(){
            var container = this.$el.find('table tbody');
            container.empty();
            var _self = this;
            var pos = 1;
            this.collection.each(function(value){
                var html = _self.render_item(value);
                container.append(html);
                pos += 1;
            });
        },
        render_item: function(value){
            var html = this.template_table({value: value});
            return html;
        },
        delete_item: function(event){
            var _self = this;
            var id = $(event.currentTarget).data('pk');
            var member = this.sprint.get('users_roles').findWhere({position: id});
            this._current_member = member;
            alert_manager.show_message({
                title: "",
                text: "Are you sure to remove " + member.get('short_name') + "?",
                type: "warning",
            }, _.bind(this.remove_member_confirm, this));
        },
        remove_member_confirm: function(inputValue) {
            if (inputValue===true){
                this.sprint.remove_member(this._current_member.get('position'));
            }
        }
    });

    return CustomerMemberView;
};


SprintForm.prototype.init_sprintView = function(ExoConsultantView,
                                                CustomerMemberView){
    var SprintView = Backbone.View.extend({
        el: "#form",
        events:{
            'submit': 'save'
        },
        initialize: function(options){
            var options = $.extend({}, options);
            this.sprint = null;

            if (options.hasOwnProperty('sprint_id')){
                this.sprint = new Backbone.models.Sprint({id: options.sprint_id});
                this.sprint.fetch({success: _.bind(this.render, this)});
            }
            else{
                this.sprint = new Backbone.models.Sprint();
            }
            this.listenTo(this.sprint, 'change:managers', this.render_managers);
        },
        save: function(event){
            var _self = this;
            event.preventDefault();
            var data = {
                'name': this.$el.find('#id_name').val(),
                'customer': this.$el.find('#id_customer').val(),
                'start': this.$el.find('#id_start').val(),
                'goals': this.$el.find('#id_goals').val(),
                'challenges': this.$el.find('#id_challenges').val(),
            };
            this.sprint.save(data,{
                silent: true,
                parse: false,
                success: function(model){
                    location.href = _self.$el.data('url-success');
                }
            });
        },
        render: function(){
            this.consultant_views = new ExoConsultantView({
                sprint: this.sprint,
                collection: this.sprint.get('consultants_roles')
            });
            this.consultant_views.render();

            this.members_view = new CustomerMemberView({
                sprint: this.sprint,
                collection: this.sprint.get('users_roles')
            });
            this.members_view.render();
        },
        render_managers: function(){
            this.$el.find('#id_managers').val(this.sprint.get('managers'));
        }
    });

    return SprintView;
};

$(function(){
    var form = new SprintForm($("#form"));
});
