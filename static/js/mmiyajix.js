function get_editable(draft){
	var targetDoc;
	var iframe = "editable_frame"; // インラインフレームのID属性を指定する。
	var input = "editable_frame_input"; // インラインフレームのID属性を指定する。
	//IE
	if (document.all) {
		targetDoc = document.frames(iframe).document;
	//その他
	} else {
		targetDoc = document.getElementById(iframe).contentDocument;
	}
	// alert(targetDoc.body.innerHTML);
	document.getElementById(input).value = targetDoc.body.innerHTML;
	return true;
}
function start_editable(id,tree_contents,save_addr){
	if($("#"+id).is(".editable")){
		$("#"+id).attr("contenteditable","False");
		$("#"+id).removeClass("editable");
		$("#"+tree_contents+" h3 img").attr("src","/static/img/edit.png");
		var data = {content:$("#"+id).html()};
		post_data(save_addr,data);
	}else{
		$("#"+id).attr("contenteditable","True");
		$("#"+id).addClass("editable");
		$("#"+tree_contents+" h3 img").attr("src","/static/img/editor/accept.png");	
		mode_edit(id);
	}
}
function mode_edit(id){
}
function setfunc(iframe,comm,ui,value){
	var targetDoc;
	var targetFrame;
	// var iframe = id; // インラインフレームのID属性を指定する。
	//IE
	if (document.all) {
		targetFrame = document.frames(iframe);
		targetDoc = targetFrame.document;
	//その他
	}else{
		targetFrame = document.getElementById(iframe);
		targetDoc = targetFrame.contentDocument;
	}
	// // alert(targetDoc.body.innerHTML);
	// switch(comm){
	// 	case "h1":
	// 		targetDoc.execCommand("FormatBlock",false,"h1");
	// 		break;
	// 	case "h2":
	// 		targetDoc.execCommand("FormatBlock",false,"h2");
	// 		break;
	// 	case "h3":
	// 		targetDoc.execCommand("FormatBlock",false,"h3");
	// 		break;
	// 	default:
	// 		targetDoc.execCommand(comm,false,null);
	// 		break;
	// }
	targetDoc.execCommand(comm,ui,value);
	targetFrame.focus();
	// alert(comm+value);
}
function sethtml(iframe,comm,ui,value){
	var targetDoc;
	var targetFrame;
	// var iframe = id; // インラインフレームのID属性を指定する。
	//IE
	if (document.all) {
		targetFrame = document.frames(iframe);
		targetDoc = targetFrame.document;
	//その他
	}else{
		targetFrame = document.getElementById(iframe);
		targetDoc = targetFrame.contentDocument;
	}
	// // alert(targetDoc.body.innerHTML);
	// switch(comm){
	// 	case "h1":
	// 		targetDoc.execCommand("FormatBlock",false,"h1");
	// 		break;
	// 	case "h2":
	// 		targetDoc.execCommand("FormatBlock",false,"h2");
	// 		break;
	// 	case "h3":
	// 		targetDoc.execCommand("FormatBlock",false,"h3");
	// 		break;
	// 	default:
	// 		targetDoc.execCommand(comm,false,null);
	// 		break;
	// }
	// targetFrame.insertHTML(value);
	targetDoc.body.innerHTML='<table><tr><td>baka</td></tr></table>';
	targetFrame.focus();
	// alert(comm+value);
}

// function executeCommand(comm,flag,target){
// 	
// }
function post_data(addr,data){
	alert(data["content"]);
	$.ajax({
		type: "POST",
		url: addr,
		data: data,
		success: function(){
		},
		complete: function(){
		},
	 });
}
function setdraft(){
	document.getElementById("draft").value = "True";
}
