$(function(){
    var view = new ProjectList('.list-detail');
});


var ProjectList = function(dom_object){
    this.$el = $(dom_object);
    this.__init__();
};

ProjectList.prototype.__init__ = function(options){
    this.init_events();
};

ProjectList.prototype.init_events = function(){
    // Finish Sprint Event
    $('div[data-role="list-detail"]').on('click',
                '.dev__finish_sprint',
                _.bind(this.openFinishSprint, this)
    );
    $('div[data-role="list-detail"]').on('click',
                '.dev__start_sprint',
                _.bind(this.openStartSprint, this)
    );
    $('div[data-role="list-detail"]').on('click',
                '.dev__launch_sprint',
                _.bind(this.openWaitingSprint, this)
    );

};

ProjectList.prototype.openFinishSprint = function(event){
    var view = new window.View.ChangeStatusProjectFinish({
        project_id: $(event.target).data('project_id'),
        label: 'End date',
        date: $(event.target).data('date'),
        badges: true,
        status: settings.project.PROJECT_CH_STATUS_FINISHED
    });
    this.show_modal(view, "Finish Service", 'Finish');
};

ProjectList.prototype.openStartSprint = function(event){
    var view = new window.View.ChangeStatusProjectFinish({
        project_id: $(event.target).data('project_id'),
        label: 'Start date',
        date: $(event.target).data('date'),
        status: settings.project.PROJECT_CH_STATUS_STARTED
    });
    this.show_modal(view, "Start Service", 'Start');
};

ProjectList.prototype.openWaitingSprint = function(event){
    event.preventDefault();
    var view = new window.View.ChangeStatusProjectFinish({
        project_id: $(event.target).data('project_id'),
        label: 'Start date',
        date: $(event.target).data('date'),
        status: settings.project.PROJECT_CH_STATUS_WAITING
    });
    this.show_modal(view, "Launch service", 'Launch');
};

ProjectList.prototype.show_modal = function(view, title, ok_text){
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: title,
        animate: true,
        okText: ok_text
    });
    modal.open();
};
