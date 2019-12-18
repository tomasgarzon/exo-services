$(function(){
	var data = {
        autofocus: false,
        savable: false
    }
    $('textarea.dev__markdown').markdown(data);  

    $("input[name=start], input[name=end]").datetimepicker({
        format: 'yyyy-mm-dd hh:ii:ss',
        autoclose: true});
});
