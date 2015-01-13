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
                    var chart_div = $('#chart_div');
                    if (selected_user) {
                        loading.show();
                        chart_div.hide();

                        // data insert start

                        $.getJSON("/api/v1/presence_start_end/"+selected_user, function(result) {
                            $.each(result, function(index, value) {
                                value[1] = new Date (value[1][0], value[1][1], value[1][2], value[1][3], value[1][4], value[1][5]);
                                value[2] = new Date (value[2][0], value[2][1], value[2][2], value[2][3], value[2][4], value[2][5]);
                            });


                        // data insert end

                            var data = new google.visualization.DataTable();
                            data.addColumn('string', 'Weekday');
                            data.addColumn('datetime', 'Start time (h:m:s)');
                            data.addColumn('datetime', 'End time (h:m:s)');
                            data.addRows(result);
                            var options = {
                                hAxis: {title: 'Hours'}
                            };
                                var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                            formatter.format(data, 1);
                            formatter.format(data, 2);

                        chart_div.show();
                        loading.hide();
                            debugger;
                        var chart = new google.visualization.Timeline(chart_div[0]);
                        chart.draw(data, options);
                        });
                    }
                });
            });
        })(jQuery);