// var targetDoc;
// var iframe = "editable_frame"; // インラインフレームのID属性を指定する。
// //IE
// if (document.all) {
// 	targetDoc = document.frames(iframe).document;
// //その他
// } else {
// 	targetDoc = document.getElementById(iframe).contentDocument;
// }
// // ドキュメントを編集可能にする
// targetDoc.designMode = "On";

jQuery.fn.set_pos = function(xx,yy){
	this.css("position","absolute");
	this.css("top", yy + "px");
	this.css("left", xx + "px");
	this.css("z-index","1000");
	return this;
}
jQuery.fn.set_center = function(){
	var wx = $(window).width();
	var wy = $(window).height();
	this.css("position","absolute");
	// this.css("margin","10px auto");
	this.css("top", wx/2+100 + "px");
	this.css("left", wy/2+100 + "px");
	this.css("z-index","1000");
	return this;
}
function hide_curtain(){
	$("#curtain").remove();
}
function create_curtain(){
	var frame_tmp = "<div class='curtain' id='curtain'></div>";
	var windows = $("#wrapper");
	windows.append(frame_tmp);
	// $('.curtain').click(function(){
	// 	hide_curtain();
	// });
}
function create_frame(frame_id){
	create_curtain();
	var frame_tmp = "";
	var windows;
	$.ajax({
		type: "get",
		url: "/tmp/inner_img.html",
		success: function(text){
			frame_tmp = "<div class='movable'><a class='hide_button' href='#' onclick='hide_curtain()'>×</a>"+text+"</div>";
			windows = $("#curtain");
			windows.append(frame_tmp);
		}
	});
	// var frames = $("#"+frame_id);
	// frames.css("width", "400px");
	// frames.css("hight", "300px");
	// var pos = getElemPos(document.getElementById(window_id));
	// frames.set_pos(pos.x,pos.y+50);
	// frames.set_center();
	// alert(pos.x+":"+pos.y);
}
function set_img(id){
	var url = $("#"+id+"_url").val();
	var alt = $("#"+id+"_alt").val();
	setfunc('editable_frame','inserthtml',false,'<br /> <div class=\'content_center content_dot\'><table class=\'table_img\'><tr><td><a href=\''+url+'\' target=\'_blank\' ><img src=\''+url+'\' alt=\''+alt+'\' /></a></td></tr><tr><td>'+alt+'</td></tr></table></div><br />');
	hide_curtain();
}

function getElemPos(elem){
var elemPos = new Object();
elemPos.x = 0;
elemPos.y = 0;
while(elem){
elemPos.x += elem.offsetLeft;
elemPos.y += elem.offsetTop;
elem = elem.offsetParent;
}
if (navigator.userAgent.indexOf('Mac') != -1 && typeof document.body.leftMargin != "undefined") {
elemPos.x += document.body.leftMargin;
elemPos.y += document.body.topMargin;
}
return elemPos;
}
