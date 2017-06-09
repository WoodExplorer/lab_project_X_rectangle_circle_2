var g_indent = '&nbsp;&nbsp;&nbsp;&nbsp;';

var repeat_string = function (s, cnt) 
// repeat a para@s para@cnt times
{
	var i = 0;
	var ret = '';
	if (cnt >= 0) {
		for (; i<cnt; i++) {
			ret += s;
		}
	} else {
		alert("Negative cnt: " + cnt);
	}
	return ret;
}

var handle_response_and_generate_user_list_html = function (resp, cur_level) 
// para@cur_level: Level for newly generated users.
//					Levels start from 0.
{		
	// turn response into json object
	var jsonObj = resp;
	var next_level = cur_level + 1;
	
	var user_list_html = "";
	$.each(jsonObj, function(index, content){ 
		//alert( "item #" + index + " its value is: " + content ); 	
		var cur_user_id = content.substr(0, content.indexOf('['));							
		var new_ele_id = '"level_' + cur_level + '_' + cur_user_id + '"';
		user_list_html += ('<div id=' + new_ele_id + 'class="my_ordinary_user" ' + 
								'onclick = my_request_for_user_group_info(' + new_ele_id + ',' + next_level + ',' + cur_user_id + ')' +
							'>' + 
							 repeat_string(g_indent, cur_level) + content + 
							'</div>');
	}); 
	return user_list_html;
}


var my_request_for_user_group_info = function (ele_id, cur_level, user_id) 
// fetch users recommended by user specified by para@user_id from server
{
	console.log('ele_id', ele_id);
	console.log('cur_level', cur_level);
	console.log('user_id', user_id);
	
	$.ajax({
			type: "POST",
			// ATTENTION: HARD-CODED URL !!!
			// 	This hard-coded url is introduced in the process of moving duplicate javascript into a dedicated file.
			// 
			// Also note that the leading '/' is indispensable.
			url: "/admin_generate_user_group",//"{{ url_for('admin_generate_user_group') }}",			
			data: JSON.stringify({ 'user_id': user_id }), 
			dataType: "json",
			contentType: 'application/json;charset=UTF-8',
			success: function(resp){
				//console.log(resp);
				
				// update web page: display user hierarchy
				var user_list_div = $('#' + ele_id);
				var user_list_html = handle_response_and_generate_user_list_html(resp, cur_level);
				user_list_div.after(user_list_html);						
			}
	});
		
	// CAREFUL! The following statement is indispensable: It prevents repeated fetching.
	$('#' + ele_id).attr('onclick', '');
}

