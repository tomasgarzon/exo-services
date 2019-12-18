var ProjectForm = function(){
    this.initWidgets();
    this.initLocation();
    this.initEvents();
};

ProjectForm.prototype.initWidgets = function(){
    $(".form_datetime").datetimepicker({
        format: 'yyyy-mm-dd hh:ii:ss',
        autoclose: true});
};

ProjectForm.prototype.initEvents = function(){
    $('#dev__launch').click(_.bind(this.openWaitingSprint, this));
};

ProjectForm.prototype.initLocation = function(){
    var elem = document.getElementById('id_location');
    var autocomplete = new google.maps.places.Autocomplete(elem, {'types': ['(cities)']});

    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        document.getElementById("id_place_id").value = place.place_id;
    });
};

ProjectForm.prototype.openWaitingSprint = function(event){
    event.preventDefault();
    var view = new window.View.ChangeStatusProjectFinish({
        project_id: $(event.target).data('project_id'),
        label: 'Start date',
        date: $(event.target).data('date'),
        status: settings.project.PROJECT_CH_STATUS_WAITING
    });
    this.show_modal(view, "Launch service", 'Launch');
};

ProjectForm.prototype.show_modal = function(view, title, ok_text){
    var modal = new Backbone.BootstrapModal({
        content: view,
        title: title,
        animate: true,
        okText: ok_text
    });
    modal.open();
};

$(function(){
    var project = new ProjectForm();
});
