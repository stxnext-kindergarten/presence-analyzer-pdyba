(function($) {
            $(document).ready(function(){
                var loading = $('#loading');
                $.getJSON("/api/v1/users", function(result) {
                    var dropdown = $("#user_id");
                    $.each(result, function(item) {
                        dropdown.append($("<option />").val(this.user_id).text(this.name));
                    });
                    dropdown.show();
                    loading.hide();
                });
                $('#user_id').change(function(){
                    var selected_user = $("#user_id").val();
                    var user_details = $('#user_detail');
                    if(selected_user) {
                        loading.show();
                        $.getJSON("/api/v1/user/"+selected_user, function(result) {
                            user_details.text(result.name);
                            user_details.append($("<img />").attr('src', result.image_url));
                        });
                    }
                });
            });
        })(jQuery);