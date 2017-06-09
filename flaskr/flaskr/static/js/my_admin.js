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


////////////////////////////////////////////////////// used for providing_help and receiving_help

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
var my_generate_html_with_operation_confirm = function (tgbz_item_id, jsonObj) {
	var info_list = '';
	$.each(jsonObj, function(index, content){ 
		//console.log( "item #" + index + " its value is: " + content ); 	
		
		info_list += ('<tr>' + 
							'<td>' + content.id + '</td>' +
							'<td>' + content.user + '</td>' +
							'<td>' + content.user_nc + '</td>' +
							'<td>' + content.jb + '</td>' +
							'<td>' + content.date + '</td>' +
							'<td>' + '<a href="#modal2" onclick="my_confirm_match(' + tgbz_item_id + ',' + content.id + ')">' + '确认匹配' + '</a>' + '</td>' +
					'</tr>');
	}); 
	console.log('info_list', info_list);
	return info_list;
}

var my_post_and_generate_html_function_generator = function (target_url, posted_data, html_generator, target_container_id) {
	return function () {
		$.post(
			target_url,
			posted_data,     
			function (jsonObj, textStatus){        
				console.log(jsonObj);   
				var info_list = html_generator(jsonObj);
				$('#' + target_container_id).html(info_list);			// Careful! Do not put wrong id here!
			}, 
			"json"
		);
	};
}


//var my_query_by_account = function () {
//	$.post(
//		'{{ url_for("admin_providing_help_query") }}', 	// Careful! Do not put wrong url here!
//		{ account: $('#account').val() },     
//		function (jsonObj, textStatus){        
//			console.log(jsonObj);   
//			var info_list = my_generate_html(jsonObj);
//			$('#query_result').html(info_list);			// Careful! Do not put wrong id here!
//		}, 
//		"json"
//	);
//}
//
//var my_fetch_unmatched = function () {
//	$.post(
//		'{{ url_for("admin_providing_help_unmatched_items") }}',  // Careful! Do not put wrong url here!
//		{ },     
//		function (jsonObj, textStatus){        
//			console.log(jsonObj);   
//			var info_list = my_generate_html_with_operation_query_candidates(jsonObj);
//			$('#unmatched_items').html(info_list);			 	// Careful! Do not put wrong id here!
//		}, 
//		"json"
//	);
//}
//
//var my_fetch_matched = function () {
//	$.post(
//		'{{ url_for("admin_providing_help_matched_items") }}', 	// Careful! Do not put wrong url here!
//		{ },     
//		function (jsonObj, textStatus){        
//			console.log(jsonObj);   
//			var info_list = my_generate_html(jsonObj);
//			$('#matched_items').html(info_list);			 	// Careful! Do not put wrong id here!
//		}, 
//		"json"
//	);
//}


var my_trying_to_match_generator = function (target_url, html_generator, target_container_id) {
	return function(tgbz_item_id, jb) {
		$.post(
			target_url,
			{ tgbz_item_id: tgbz_item_id, jb: jb },     
			function (jsonObj, textStatus){        
				console.log(jsonObj);   
				var info_list = html_generator(tgbz_item_id, jsonObj);
				$('#' + target_container_id).html(info_list);			// Careful! Do not put wrong id here!
			}, 
			"json"
		);
	};
}
//var my_trying_to_match = function (tgbz_item_id, jb) {
//	console.log('tgbz_item_id', tgbz_item_id);
//	
//	$.post(
//		'{{ url_for("admin_providing_help_unmatched_items_with_specifi_jb") }}', 	// Careful! Do not put wrong url here!
//		{ tgbz_item_id: tgbz_item_id, jb: jb },     
//		function (jsonObj, textStatus){        
//			console.log(jsonObj);   
//			var info_list = my_generate_html_with_operation_confirm(tgbz_item_id, jsonObj);
//			$('#modal2Table').html(info_list);			// Careful! Do not put wrong id here!
//		}, 
//		"json"
//	);
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
//	$.post(
//		'{{ url_for("admin_providing_help_match_tgbz_to_jsbz") }}', 	// Careful! Do not put wrong url here!
//		{ tgbz_item_id: tgbz_item_id, jsbz_item_id: jsbz_item_id },     
//		function (jsonObj, textStatus){        
//			console.log(jsonObj);   
//			//alert('match completed');
//			top.location = "{{ url_for('admin_providing_help') }}";
//		}, 
//		"json"
//	);
//}


