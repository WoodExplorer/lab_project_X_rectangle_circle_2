
////////////////////////////////////////////////////// used for providing_help and receiving_help   <START>

var my_generate_html = function (jsonObj) {
    var info_list = '';
    $.each(jsonObj, function(index, content){ 
        //console.log( "item #" + index + " its value is: " + content );    
        
        info_list += ('<tr>' + 
                            '<td>' + content.id + '</td>' +
                            '<td>' + content.user + '</td>' +
                            '<td>' + content.user_nc + '</td>' +
                            '<td>' + content.jb + '</td>' +
                            '<td>' + content.date + '</td>' +
                    '</tr>');
    }); 
    console.log('info_list', info_list);
    return info_list;
}
var my_generate_html_with_operation_query_candidates = function (jsonObj) {
    var info_list = '';
    $.each(jsonObj, function(index, content){ 
        //console.log( "item #" + index + " its value is: " + content );    
        
        info_list += ('<tr>' + 
                            '<td>' + content.id + '</td>' +
                            '<td>' + content.user + '</td>' +
                            '<td>' + content.user_nc + '</td>' +
                            '<td>' + content.jb + '</td>' +
                            '<td>' + content.date + '</td>' +
                            '<td>' + '<a href="#modal2" onclick="my_trying_to_match(' + content.id + ',' + content.jb + ')">' + '手动匹配' + '</a>' + '</td>' +
                    '</tr>');
    }); 
    console.log('info_list', info_list);
    return info_list;
}
var my_generate_html_with_operation_confirm_generator = function (request_type) {
    if ('receiving_help' != request_type && 'providing_help' != request_type) {
        alert('Unknown request_type:' + request_type + '. Pleasee contact administrator.');
        return;
    }
    return function(item_id, jsonObj) {
                var info_list = '';
                $.each(jsonObj, function(index, content){ 
                    //console.log( "item #" + index + " its value is: " + content );    
                    info_list += ('<tr>' + 
                                        '<td>' + content.id + '</td>' +
                                        '<td>' + content.user + '</td>' +
                                        '<td>' + content.user_nc + '</td>' +
                                        '<td>' + content.jb + '</td>' +
                                        '<td>' + content.date + '</td>' +
                                        '<td>' + '<a href="#modal2" onclick="my_confirm_match(' + 
                                                                                            (
                                                                                                'providing_help' == request_type? 
                                                                                                    ('' + item_id + ',' + content.id):
                                                                                                    ('' + content.id + ',' + item_id)
                                                                                            ) + 
                                                                                            ')">' + '确认匹配' + '</a>' + '</td>' +
                                '</tr>');
                }); 
                console.log('info_list', info_list);
                return info_list;
    };
    
}

var my_post_and_generate_html_function_generator = function (target_url, posted_data_generator, html_generator, target_container_id) {
    return function () {
        $.post(
            target_url,
            posted_data_generator(),     
            function (jsonObj, textStatus){        
                console.log(jsonObj);   
                var info_list = html_generator(jsonObj);
                $('#' + target_container_id).html(info_list);           // Careful! Do not put wrong id here!
            }, 
            "json"
        );
    };
}


//var my_query_by_account = function () {
//  $.post(
//      '{{ url_for("admin_providing_help_query") }}',  // Careful! Do not put wrong url here!
//      { account: $('#account').val() },     
//      function (jsonObj, textStatus){        
//          console.log(jsonObj);   
//          var info_list = my_generate_html(jsonObj);
//          $('#query_result').html(info_list);         // Careful! Do not put wrong id here!
//      }, 
//      "json"
//  );
//}
//
//var my_fetch_unmatched = function () {
//  $.post(
//      '{{ url_for("admin_providing_help_unmatched_items") }}',  // Careful! Do not put wrong url here!
//      { },     
//      function (jsonObj, textStatus){        
//          console.log(jsonObj);   
//          var info_list = my_generate_html_with_operation_query_candidates(jsonObj);
//          $('#unmatched_items').html(info_list);              // Careful! Do not put wrong id here!
//      }, 
//      "json"
//  );
//}
//
//var my_fetch_matched = function () {
//  $.post(
//      '{{ url_for("admin_providing_help_matched_items") }}',  // Careful! Do not put wrong url here!
//      { },     
//      function (jsonObj, textStatus){        
//          console.log(jsonObj);   
//          var info_list = my_generate_html(jsonObj);
//          $('#matched_items').html(info_list);                // Careful! Do not put wrong id here!
//      }, 
//      "json"
//  );
//}


var my_trying_to_match_generator = function (target_url, html_generator, target_container_id) {
    return function(tgbz_item_id, jb) {
        $.post(
            target_url,
            { tgbz_item_id: tgbz_item_id, jb: jb },     
            function (jsonObj, textStatus){        
                console.log(jsonObj);   
                var info_list = html_generator(tgbz_item_id, jsonObj);
                $('#' + target_container_id).html(info_list);           // Careful! Do not put wrong id here!
            }, 
            "json"
        );
    };
}
//var my_trying_to_match = function (tgbz_item_id, jb) {
//  console.log('tgbz_item_id', tgbz_item_id);
//  
//  $.post(
//      '{{ url_for("admin_providing_help_unmatched_items_with_specifi_jb") }}',    // Careful! Do not put wrong url here!
//      { tgbz_item_id: tgbz_item_id, jb: jb },     
//      function (jsonObj, textStatus){        
//          console.log(jsonObj);   
//          var info_list = my_generate_html_with_operation_confirm(tgbz_item_id, jsonObj);
//          $('#modal2Table').html(info_list);          // Careful! Do not put wrong id here!
//      }, 
//      "json"
//  );
//}

var my_confirm_match_generator = function (target_url, redirect_url) {
    return function (tgbz_item_id, jsbz_item_id) {
        $.post(
            target_url,
            { tgbz_item_id: tgbz_item_id, jsbz_item_id: jsbz_item_id },     
            function (jsonObj, textStatus){        
                console.log(jsonObj);   
                //alert('match completed');
                top.location = redirect_url;
            }, 
            "json"
        );
    };
}
//var my_confirm_match = function (tgbz_item_id, jsbz_item_id) {
//  $.post(
//      '{{ url_for("admin_providing_help_match_tgbz_to_jsbz") }}',     // Careful! Do not put wrong url here!
//      { tgbz_item_id: tgbz_item_id, jsbz_item_id: jsbz_item_id },     
//      function (jsonObj, textStatus){        
//          console.log(jsonObj);   
//          //alert('match completed');
//          top.location = "{{ url_for('admin_providing_help') }}";
//      }, 
//      "json"
//  );
//}

////////////////////////////////////////////////////// used for providing_help and receiving_help   <END>
