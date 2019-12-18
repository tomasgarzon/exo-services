var ProjectValidation = function(){
    this.init();
}

ProjectValidation.prototype.init = function(){
    $('.dev__fix_validation').click(_.bind(this.fix, this));
}

ProjectValidation.prototype.fix = function(event){
    var data = $(event.currentTarget).data('post');
    var canfix = $(event.currentTarget).data('canfix');
    if ((data.toLowerCase() == 'true') && (canfix.toLowerCase() == 'true')){
        event.preventDefault();
        var project_id = $(event.currentTarget).data('project');
        var url = urlservice.resolve('forum-request-deploy', project_id);
        $.ajax({
            url: url,
            method: 'post',
            success: function(result){
                toastr_manager.show_message(
                    'success',
                    result.message,
                    ''
                );
            },
            error: function(event){
                toastr_manager.show_message(
                    'error',
                    'An error ocurred, please contact support',
                    ''
                );
            }
        });
    }
}

$(function(){
    var validation = new ProjectValidation();
});
