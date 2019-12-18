var NetworkMemberActionView = function(){
    this.channelName = 'network';
    this.channel = Backbone.Radio.channel(this.channelName);
    this.init_disable();
    this.init_delete();
    this.init_reactivate();
    this.channel.on('disable-consultant', _.bind(this.manageDisable, this));
};


NetworkMemberActionView.prototype.init_disable = function(){
    var _self = this;
    $('div[data-role="list-detail"]').on('click', '.dev__disable_consultant', function(event){
        alert_manager.show_message({
                title: "",
                text: "Are you sure to disable this ExO Consultant?",
                type: "warning",
                confirmButtonText: 'Yes, disable'
            }, _.bind(_self.confirmDisable, this));
    });
};

NetworkMemberActionView.prototype.confirmDisable = function(){
    var url = $(this).data('url');
    location.href = url;
};

NetworkMemberActionView.prototype.init_delete = function(){
    var _self = this;
    $('div[data-role="list-detail"]').on('click', '.dev__delete_consultant', function(event){
        var elem = this;
        alert_manager.show_message({
                title: "",
                text: "Are you sure to delete this ExO Consultant?",
                type: "warning",
                confirmButtonText: 'Yes, delete'
            }, function(){
              _self.confirmDelete(elem);
            });
    });
};

NetworkMemberActionView.prototype.confirmDelete = function(elem){
    var url = $(elem).data('url');
    $.get(
        url,
        _.bind(this.processDelete, this)
    );
};

NetworkMemberActionView.prototype.processDelete = function(data){
    if (data.status === 'deleted'){
        location.href = data.url;
    } else{
        var _self = this;
        swal.close();
        setTimeout(function(){
            _self.channel.trigger('disable-consultant', data);
        }, 500);

    }
};

NetworkMemberActionView.prototype.manageDisable = function(data){
    var new_url = data.url;
    alert_manager.show_message({
        title: "",
        text: "This ExO Consultant can't be deleted because important information is related, Do you want to disable it?",
        type: "warning",
        confirmButtonText: 'Yes, disable'
    }, function(){
        location.href = new_url;
    });
};

NetworkMemberActionView.prototype.init_reactivate = function(){
    var _self = this;
    $('div[data-role="list-detail"]').on('click', '.dev__reactivate_consultant', function(event){
        var elem = this;
        var date = $(elem).data('date');
        alert_manager.show_message({
                title: "Activate old member",
                text: "This consultant was disabled on " + date +". Do you really want to add it again to the Network? All the related information will be restored.",
                type: "warning",
                confirmButtonText: 'Yes, activate'
            }, function(){
              _self.confirmReactivate(elem);
            });
    });
};

NetworkMemberActionView.prototype.confirmReactivate = function(elem){
    var url = $(elem).data('url');
    $.get(
        url,
        _.bind(this.processReactivate, this)
    );
};

NetworkMemberActionView.prototype.processReactivate = function(){
    location.href = ".";
};


$(function(){
    var view = new NetworkMemberActionView();
});
