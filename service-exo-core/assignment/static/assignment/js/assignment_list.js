var Assignment = function(elem){
    this.elem = elem;
    var switchery = new Switchery(this.elem);
    this.counter = 0;
    this.initEvents();
};

Assignment.prototype.initEvents = function(){
    this.elem.onchange = _.bind(this.changePublic, this);
};

Assignment.prototype.changePublic = function(){
    var object_id = $(this.elem).data('id');
    var project_id = $(this.elem).data('project');
    this.counter = this.counter + 1;
    $.get(
          urlservice.resolve("project-assignment-change-status", project_id, object_id),
          _.bind(this.processStatusChanged, this)
    );
    $("body").addClass("waiting");
};

Assignment.prototype.processStatusChanged = function(response){
    toastr_manager.show_message('success', '', response.assignment_status);
    this.counter = this.counter - 1;
    if (this.counter === 0){
        $("body").removeClass("waiting");
    }
};

$(function(){
    var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
    elems.forEach(function(elem) {
      var assignment = new Assignment(elem);
    });
});
