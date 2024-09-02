/* *******************************************************
 * filename : functions.js
 * description : 전체적으로 사용되는 JS
 * date : 2022-07-15
******************************************************** */


// function footeradjust(){
// 	var nFinalHeight = Math.max( document.body.scrollHeight, document.body.offsetHeight, 
// 		document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );
// 	// $('#footer').css('top',nFinalHeight);
// 	$('#footer').css('bottom','unset');	
// }

/* ************************
  * 브라우저를 체크할때 사용하는 함수
  * return browser(브라우저name)
  ************************ */
function detectBrowser () {
	var agent = navigator.userAgent.toLowerCase(); 
	var browser; 
	
	if ( (agent.indexOf('msie') > -1) || (agent.indexOf('trident') > -1) || (agent.indexOf('edge') > -1) ) { 
		browser = 'ie'
	}else if(agent.indexOf('firefox') > -1) { 
		browser = 'firefox' 
	}else if(agent.indexOf('opr') > -1) { 
		browser = 'opera' 
	}else if(agent.indexOf('chrome') > -1) { 
		browser = 'chrome' 
	}else if(agent.indexOf('safari') > -1) { 
		browser = 'safari'
	}

	return browser;
}

 /* ************************
  * IE 버전을 체크할때 사용하는 함수
  * return : IE 아닐때 false / IE 일때 9,10,11,"edge"
  ************************ */
function ieVersionCheck () {
	var word; 
	var version = "N/A"; 
	var agent = navigator.userAgent.toLowerCase(); 
	var name = navigator.appName; 

	// IE old version ( IE 10 or Lower ) 
	if ( name == "Microsoft Internet Explorer" ) word = "msie "; 
	else { 
		// IE 11 
		if ( agent.search("trident") > -1 ) word = "trident/.*rv:"; 
		// Microsoft Edge  
		else if ( agent.search("edge/") > -1 ) word = "edge/"; 
	} 
	var reg = new RegExp( word + "([0-9]{1,})(\\.{0,}[0-9]{0,1})" ); 
	if (  reg.exec( agent ) != null  ) version = RegExp.$1 + RegExp.$2; 
	
	if ( version !="NaN" && version < 12 ) {
		return parseInt (version)
	}else if ( word === "edge/" ) {
		return	 false;
	}else {
		return false;
	}
}

 /* ************************
  * OS 체크 함수
  * android/ios 체크할때 사용
  ************************ */
function detectOS(){
    var agent = navigator.userAgent.toLowerCase(); 
	var osCheck; 

    if ( agent.indexOf('android') > -1) {
        return "android";
    } else if ( agent.indexOf("iphone") > -1|| agent.indexOf("ipad") > -1|| agent.indexOf("ipod") > -1 || agent.indexOf("macintosh") > -1 ) {
        return "ios";
    } else {
        return "other";
    }

	return osCheck;
}

 /* ************************
  * 모바일 체크 함수
  * return : 모바일 true / PC false
  * Ipad Safari userAgent 변경으로 인해 if문 추가 (2020-07-17)
  ************************ */
function isMobile(){
	var UserAgent = navigator.userAgent;
	if (UserAgent.match(/iPhone|iPad|iPad|Android|Windows CE|BlackBerry|Symbian|Windows Phone|webOS|Opera Mini|Opera Mobi|POLARIS|IEMobile|lgtelecom|nokia|SonyEricsson/i) != null || UserAgent.match(/LG|SAMSUNG|Samsung/) != null)
	{
		return true;
	}else{
		// Ipad Safari Browser
		if ( detectIpad() ) {
			return true;
		}else {
			return false;
		} 
	}
}
function detectIpad() {
	var userAgent = navigator.userAgent || navigator.vendor || window.opera;
	// Lying iOS13 iPad
	if (userAgent.match(/Macintosh/i) !== null) {
		// need to distinguish between Macbook and iPad
		var canvas = document.createElement("canvas");
		if (canvas !== null) {
			var context = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
			if (context) {
				var info = context.getExtension("WEBGL_debug_renderer_info");
				if (info) {
					var renderer = context.getParameter(info.UNMASKED_RENDERER_WEBGL);
					if (renderer.indexOf("Apple") !== -1)
					return true;
				}
			}
		}
	}
	return false;
}

/* ************************
  * window 팝업 오픈 함수
  * @param src : "팝업 페이지 주소"
  * @param title : "팝업 페이지 타이틀"
  * @param option : "width=너비, height=높이, left=x축 위치, top=y축 위치, resizable=리사이즈 여부, scrollbars=스크롤바 여부, status=상태 표시줄 여부"
  ************************ */
function winPopupOpen(src,title,option){
	window.open(src,title,option);
}

 /* ************************
  * 브라우저의 가로값, 세로값 측정 함수
  * return 가로값/세로값
  ************************ */
/* 임의의 영역을 만들어 스크롤바 크기 측정 */ 
function getScrollBarWidth(){
	if($(document).height() > $(window).height()){
		$('body').append('<div id="fakescrollbar" style="width:50px;height:50px;overflow:hidden;position:absolute;top:-200px;left:-200px;"></div>');
		fakeScrollBar = $('#fakescrollbar');
		fakeScrollBar.append('<div style="height:100px;">&nbsp;</div>');
		var w1 = fakeScrollBar.find('div').innerWidth();
		fakeScrollBar.css('overflow-y', 'scroll');
		var w2 = $('#fakescrollbar').find('div').html('html is required to init new width.').innerWidth();
		fakeScrollBar.remove();
		return (w1-w2);
	}
	return 0;
}
/* 브라우저 가로, 세로크기 측정 */ 
function getWindowWidth () {
	return $(window).outerWidth() + getScrollBarWidth() ;
}
function getWindowHeight () {
	return $(window).height() ;
}

 /* ************************
  * 브라우저의 스크롤바의 수직 위치 측정 함수
  * return 스크롤바 위치 값
  ************************ */
function getScrollTop () {
	return $(window).scrollTop();
}

 /* ************************
  * 브라우저의 스크롤을 이동시키는 함수
  * @param top : 이동지점
  * @param speed : 이동속도
  ************************ */
function moveScrollTop (top, speed) {
	$("html, body").animate({scrollTop:top}, speed ,"easeInOutExpo");
}

 /* ************************
  * object toggleClass 함수
  * @param object : 적용되야할 선택자
  * @param className : toggleClass Name
  ************************ */
/* addClass Active */
function addClassName (object, className) {
	$(object).addClass(className);
}
function removeClassName (object, className) {
	$(object).removeClass(className);
}

/* ************************
  * 갯수체크 함수
  * @param selector : 선택자
  * 1개이상 있으면 return true
  ************************ */
$.exists = function(selector) {
	return ($(selector).length > 0);
}

/* ************************
  * AOS Plugin 
  * aos.js 필요
  * ieVersionCheck() 함수 필요 - IE 10부터 적용
  ************************ */
/* AOS Plugin */
function aosInit () {
	var browserVer = ieVersionCheck();
	if ( !browserVer || browserVer > 9 ) {
		AOS.init({
		 // Global settings:
		  disable: false, // accepts following values: 'phone', 'tablet', 'mobile', boolean, expression or function
		  startEvent: 'DOMContentLoaded', // name of the event dispatched on the document, that AOS should initialize on
		  initClassName: 'aos-init', // class applied after initialization
		  animatedClassName: 'aos-animate', // class applied on animation
		  useClassNames: false, // if true, will add content of `data-aos` as classes on scroll
		  disableMutationObserver: false, // disables automatic mutations' detections (advanced)
		  debounceDelay: 50, // the delay on debounce used while resizing window (advanced)
		  throttleDelay: 99, // the delay on throttle used while scrolling the page (advanced)
		  

		  // Settings that can be overridden on per-element basis, by `data-aos-*` attributes:
		  offset: 150, // offset (in px) from the original trigger point
		  delay: 0, // values from 0 to 3000, with step 50ms
		  duration: 1000, // values from 0 to 3000, with step 50ms
		  easing: 'ease', // default easing for AOS animations
		  once: true, // whether animation should happen only once - while scrolling down
		  mirror: false, // whether elements should animate out while scrolling past them
		  anchorPlacement: 'top-bottom', // defines which position of the element regarding to window should trigger the animation
		});		
	}
}

/* ************************
  * mCustomScrollbar Plugin ( 스크롤바 커스텀 )
  * jquery.mCustomScrollbar.concat.min.js 필요
  * @param selector : 선택자
  ************************ */
/* Custom Scrollbar Plugin (x,y) */
function customScrollX (scrollObject) {
	$(scrollObject).mCustomScrollbar({
		axis:"x",
		theme:"dark",
		scrollInertia: 60,
	});
}
function customScrollY (scrollObject) {
	$(scrollObject).mCustomScrollbar({
		axis:"y",
		theme:"dark",
		scrollInertia: 60,
	});
}

/* ************************
  * 스크롤값에 따라 클래스가 붙는 함수
  * @param object : 선택자
  * @param fixedStartTop : 클래스가 붙는 시작되는지점
  * @param className : 붙여야하는 클래스이름
  * getScrollTop() 함수 필요
  ************************ */
/* Fixed Object */ 
function objectFixed ( object, fixedStartTop, className ) {
	if ( getScrollTop() >  fixedStartTop ) {
		if (!($(object).hasClass(className))) {	
			$(object).addClass(className);
		}
	}else {
		if ($(object).hasClass(className)) {
			$(object).removeClass(className);
		}
	}
}

/* ************************
  * object의 offset 체크 함수
  *  @param object : 선택자
  * return : offset.top 값
  ************************ */
function checkOffset (object) {
	return $(object).offset().top;
}

/* ************************
  * 상단에 fixed를 되고있는 object의 높이값 체크 함수
  * return : top-fixed 되고있는 높이의 total값
  ************************ */
function checkFixedHeight () {
	var fixedTotalHeight = null;
	for (var i=0; i<$(".top-fixed").length; i++) {
		var fixedTotalHeight = fixedTotalHeight + $(".top-fixed").eq(i).outerHeight();
	}
	return fixedTotalHeight;
}

/* ************************
  * 스크롤 event 최적화
  ************************ */
function toFit(cb, _ref) {
	var _ref$dismissCondition = _ref.dismissCondition,
		dismissCondition = _ref$dismissCondition === void 0 ? function () {
		return false;
	} : _ref$dismissCondition,
	  _ref$triggerCondition = _ref.triggerCondition,
	  triggerCondition = _ref$triggerCondition === void 0 ? function () {
	return true;
	} : _ref$triggerCondition;

		if (!cb) {
			throw Error('Invalid required arguments');
		}

		var tick = false;
		return function () {
		//  console.log('scroll call')
		if (tick) {
			return;
		}

		tick = true;
		return requestAnimationFrame(function () {
			if (dismissCondition()) {
				tick = false;
				return;
			}

			if (triggerCondition()) {
				//console.log('real call')
				tick = false;
				return cb();
			}
		});
	};
}

/* ************************
  * html 스크롤바 제어 함수
  * 스크롤 막을때 - true / 스크롤 사용할때 false
  ************************ */
function htmlScrollControl (toggle) {
	if (toggle) {
		$("html").css({
			"margin-right":"5px",
			"overflow-y":"hidden",
			"overflow-x":"hidden"
		});
	}else {
		$("html").css({
			"margin-right":"0",
			"overflow-y":"scroll",
			"overflow-x":"auto"
		});
	}
}
/* ************************
  * 레이어팝업 open/close 함수
  * object = id
  ************************ */

function CommonmodalPopupOpen(msg, e=null) {
	if(e!=null)e.preventDefault();
	//개행문자처리
	msg = msg.replace(/(?:\r\n|\r|\n)/g, '<br />');	
	
	// 오픈할때 모든 modal popup visible 체크 => 1개이상 있을 시 띄우는 팝업의 배경색 투명
	if ( $(".layer-popup:visible").length > 0 ) {
		$('#popupCommon').css("background-color","transparent");
	}
	$('#popupCommon .cm-txt').html(msg);
	$('#popupCommon').show();
	htmlScrollControl(true);
	return false;
}
function modalPopupOpen (e, object) {
	e.preventDefault();	
	// 오픈할때 모든 modal popup visible 체크 => 1개이상 있을 시 띄우는 팝업의 배경색 투명
	if ( $(".layer-popup:visible").length > 0 ) {
		$(object).css("background-color","transparent");
	}
	$(object).show();
	htmlScrollControl(true);
}
function modalPopupClose (object) {
	$(object).hide();
	
	// 닫을때 모든 modal popup visible 체크 => 없을때 html 스크롤바 생성
	if ( $(".layer-popup:visible").length === 0 ) {
		htmlScrollControl(false);
	}	
}
function modalAlertToggle (openState) {
	if ( openState ) {
		$(".modal-fixed-pop-wrapper").show();
		htmlScrollControl(true);	
	}else {
		$(".modal-fixed-pop-wrapper").hide();
		if ( $(".layer-popup:visible").length === 0 ) {
			htmlScrollControl(false);
		}	
	}
}

function SnsDisconnect(url, id=null){
	data = {
	'account' : id
	}
	$.ajax({
		url : url,
		type : 'POST',
		data : data,
		success:function(data){
			$('a.kakao').removeClass('connected')
			CommonmodalPopupOpen('연동해지가 완료되었습니다.');
		},
		error:function(err){
			console.log(err.responseJSON);
		}
	})
}

/* ************************
  * 알림 AJAX 콜
  * placement = pk
  ************************ */
function AlarmAjax(e, pk, url, csrfmiddlewaretoken){
	e.preventDefault();
	$.ajax({
		type: "POST",
		url: url,
		data: {'pk': pk, 'csrfmiddlewaretoken': csrfmiddlewaretoken},
		dataType: "json",
		success: function(res){
			if(res.alarm == 'activate'){
				CommonmodalPopupOpen('알림설정이 완료되었습니다.');
				$(e.target).addClass('deactivate');				
			}
			else if(res.alarm == 'deactivate'){
				CommonmodalPopupOpen('알림설정이 해지되었습니다.');
				$(e.target).removeClass('deactivate');
			}
		},
		error: function(res){
			alert("에러가 발생하였습니다. 다시 시도해주십시오")
			window.location.replace("/auction/list")
		},
		});
}

/* ************************
  * 앵콜 AJAX 콜
  * placement = pk
  ************************ */
function EncoreAjax(e, pk, url, csrfmiddlewaretoken){
	e.preventDefault();	
	$.ajax({
		type: "POST",
		url: url,
		data: {'pk': pk, 'csrfmiddlewaretoken': csrfmiddlewaretoken},
		dataType: "json",
		success: function(res){
			if(res.encore == 'activate'){
				$(e.target).addClass('disabled');
				CommonmodalPopupOpen('앵콜신청이 완료되었습니다.');
			}
			else if(res.encore == 'deactivate'){
				$(e.target).removeClass('disabled');
				CommonmodalPopupOpen('앵콜신청이 취소되었습니다.');
			}
		},
		error: function(res){
			alert("에러가 발생하였습니다. 다시 시도해주십시오")
			window.location.replace("/auction/list")
		},
		});
}

/* ************************
  * 좋아요 AJAX 콜
  * placement = pk
  ************************ */
function PlikeAjax(e, pk, url, csrfmiddlewaretoken){
	console.log(url);
	e.preventDefault();
	$.ajax({
		type: "POST",
		url: url,
		data: {'pk': pk, 'csrfmiddlewaretoken': csrfmiddlewaretoken},
		dataType: "json",
		success: function(res){
			if(res.plike == 'activate'){
				$('.plike.zzim-btn').addClass('activate');
			}
			else if(res.plike == 'deactivate'){
				$('.plike.zzim-btn').removeClass('activate');				
			}
		},
		error: function(res){
			alert("에러가 발생하였습니다. 다시 시도해주십시오")
			window.location.replace("/auction/list")
		},
		});
}

/* ************************
  * Toggle UserPrivacy ( AD )
  ************************ */
function ToggleUserPrivacy(url, csrfmiddlewaretoken){
	$.ajax({
		type: "POST",
		url: url,
		data: {'csrfmiddlewaretoken': csrfmiddlewaretoken},
		dataType: "json",
		success: function(res){
			if(res.ad == 'activate'){
				CommonmodalPopupOpen("원앤온리 정보 수신이 활성화 되었습니다.");
				$("input[rev='userprivacy']").attr('checked', true);
			}
			else if(res.ad == 'deactivate'){
				CommonmodalPopupOpen("원앤온리 정보 수신이 비활성화 되었습니다.");
				$("input[rev='userprivacy']").attr('checked', false);
			}
		},
		error: function(res){
			alert("에러가 발생하였습니다. 다시 시도해주십시오")
		},
		});
}


/* ************************
* 익스플로러 엣지 전환 소스
* 익스플로러 브라우저 업데이트 안내 팝업
************************ */
function convertToEdge () {
	if(/MSIE \d|Trident.*rv:/.test(navigator.userAgent)) {
		window.location = 'microsoft-edge:' + window.location;
		setTimeout(function() {
			top.window.open('about:blank','_self').close(); 
			top.window.opener=self;
			top.self.close();
		},1);
	}
}
function popupUpdateBrowser () {
	var popupBrowser = '';
    popupBrowser += '<article id="browserUpgradePopup">';
    popupBrowser += '<div class="browser-upgrade-popup-dim"></div>';
    popupBrowser += '<div class="browser-upgrade-popup-inner">';
    popupBrowser += '<button class="browser-popup-close-btn" title="close"><i class="xi-close-thin"></i></button>';
    popupBrowser += '<span class="browser-popup-caution-icon"><i class="xi-error-o"></i></span><h2 class="browser-popup-tit"><b>브라우저 업데이트</b> 안내</h2><p class="browser-popup-txt">현재 사용중인 브라우저는 곧 지원이 중단됩니다. <br>원활한 서비스를 제공받기 위해<br><b>보안과 속도가 강화된 브라우저로 업그레이드</b> 하시기 바랍니다.</p>';
    popupBrowser += '</div>';
    popupBrowser += '</article>';
	$("body").append(popupBrowser);
	$(document).on("click",".browser-popup-close-btn",function  () {
		$("#browserUpgradePopup").hide();
		return false;
	});
}

 /* ************************
  * target Check 함수
  * className이 있으면 return true
  ************************ */
function isClassName (target, className) {
	var parents = $(target).parents("."+className+"");
	var isParents = false;

	if (parents.length === 0 && target.className.indexOf(className)  >= 0) {
		return isParents = true;
	}
	 
	for (var i=0; i<parents.length; i++) {
		// console.log(parents[i].className);
		if (parents[i].className.indexOf(className)  >= 0) {
			isParents = true;
		}
	}

	return isParents;
}


 /* ************************
  * urlQuery
  ************************ */
  function searchParam(key) {
    return new URLSearchParams(location.search).get(key);
  };

	function getURLParams(url) {
    var result = {};
    url.replace(/[?&]{1}([^=&#]+)=([^&#]*)/g, function(s, k, v) { result[k] = decodeURIComponent(v); });
    return result;
}	

	/* ************************
  * 카카오톡 공유, 링크복사
  ************************ */
	function KakaoCopy(e){
		e.preventDefault();
		url = window.document.location.href;
		navigator.clipboard.writeText(url);
		CommonmodalPopupOpen('복사가 완료되었습니다.');
	};

	function KakaoShare(e, type, obj){
		e.preventDefault();
		try{
			Kakao.init('473452b14b7dc9d856d7fd5b0c830bb2');
		}
		catch{
			console.log('kakao init error occured')
			return;
		}
		if(type=='placement'){
			var THU = obj.thumbnail;
			var TITLE = obj.title;
			var ARTIST = obj.artist;
			var DESC = obj.description;
			var link=$('meta[property="og:url"]').attr('content');
			var path=window.location.pathname;
			if(path.charAt(0) == '/'){
				path=path.slice('1');
			}
			Kakao.Link.sendCustom({
				templateId: 75100,
				templateArgs: {
					THU: THU, // 썸네일 주소
					TITLE: TITLE, // 제목 텍스트
					ARTIST: ARTIST, //아티스트
					DESC: DESC, // 설명 텍스트
					PATH: path,
				}
			});
		}
		else if(type=='ticket'){
			var QR_THU = obj.qr_src;
			var P_TIME = obj.placement.d_day;
			var P_PLACE = obj.placement.d_place;
			var P_TITLE = obj.placement.title;
			var P_CATEGORY = obj.placement.category;
			var P_THU = obj.placement.thumbnail;
			var P_PATH = obj.placement.path;
			var ARTIST = obj.placement.artist;
			var USERNAME = obj.user.name
			var CNT = obj.quantity;
			if(P_PATH.charAt(0) == '/'){
				P_PATH=P_PATH.slice('1');
			}
			Kakao.Link.sendCustom({
				templateId: 86532,
				templateArgs: {
					QR_THU: QR_THU,
					P_TIME: P_TIME,
					P_PATH : P_PATH,
					P_PLACE : P_PLACE,
					P_TITLE:P_TITLE,
					P_THU:P_THU,
					P_CATEGORY:P_CATEGORY,
					ARTIST:ARTIST,
					USERNAME:USERNAME,
					CNT:CNT,
				}
			});			
		}
		else{
			console.log('Type 파라미터가 입력되지 않았습니다.')
		}

	}
 /* ************************
  * Mypage Certification Iamport
  ************************ */
 
 function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
	}
	// 개인정보취급방침
	function CheckAgreement(e){
		e.preventDefault();
		if($("#phone-agree").is(":checked")){
			$('button[ref=smartrev]').attr('disabled', false)
			$('button[ref=smsrev]').attr('disabled', false)
		}else{
			$('button[ref=smartrev]').attr('disabled', true)
			$('button[ref=smsrev]').attr('disabled', true)
		}
	}
	var HOST = window.location.host
	var PATH = window.location.pathname
	var IMP = window.IMP; // 생략가능
	const iID = 'imp92988775';
	function SmartCef(e){
			e.preventDefault();
			var next = searchParam('next')
			var _m_redirect_url = `http://${HOST}/mobile/auth/?process=auth&${next==null?'&':'next='+next}`
			var IMP = window.IMP; // 생략가능
			IMP.init(iID);  // 가맹점 식별 코드
			IMP.certification
			(
				{
					pg:'inisis.MIIonenonl',
					merchant_uid : 'merchant_' + new Date().getTime(),
					name : '',	//이름
					popup : false,
					request_id:'cef',
					m_redirect_url: _m_redirect_url,
				}, function(rsp) {
							if ( rsp.success ) { // 성공시
								$.ajax({
								url: `http://${HOST}/auth/`, // 가맹점 서버
								method: "POST",
								headers: { "Content-type": "application/json; charset=utf-8", "X-CSRFToken": csrftoken},
								data: JSON.stringify({
									'success' : rsp.success,
									'imp_uid' : rsp.imp_uid,
									'merchant_uid' : rsp.merchant_uid
								})
								})
								.done(function(res) {
									var b = new Date(res.birthday);
									$('td#cef_name').text(res.name);
									$('td#cef_phone').text(res.phone);
									$('td#cef_birthday').text(`${b.getFullYear()}년 ${b.getMonth()+1}월 ${b.getDate()}일`)
									CommonmodalPopupOpen('인증이 완료되었습니다.');
									$('input[ref=checkrev]').attr('disabled', true).attr('checked',true)
									$('button[ref=smartrev]').attr('disabled', true)
									$('button[ref=smsrev]').attr('disabled', true)
									//NEXT?
									if(next && !isMobile()) window.location.replace(next);
								})
								.fail(function(res){
									var msg;
									if(res.responseJSON)msg=res.responseJSON.msg
									if(!msg)msg='인증에 실패하였습니다.'
									CommonmodalPopupOpen(msg);
								})
							}
							else { // 실패시
								CommonmodalPopupOpen('인증에 실패하였습니다.');
							}
						}
			);      
	}

	function SmsCef(e){
			e.preventDefault();
			var IMP = window.IMP; // 생략가능
			var next = searchParam('next')
			var _m_redirect_url = `http://${HOST}/mobile/auth/?process=auth&${next==null?'&':'next='+next}`
			IMP.init(iID);  // 가맹점 식별 코드
			IMP.certification
			(
				{
					pg:'danal.B010007679',
					merchant_uid : 'merchant_' + new Date().getTime(),
					name : '',	// 이름
					popup : false,
					request_id:'cef',
					m_redirect_url: _m_redirect_url,
				}, function(rsp) {
							if ( rsp.success ) { // 성공시
								$.ajax({
								url: `http://${HOST}/auth/`, // 가맹점 서버
								method: "POST",
								headers: { "Content-type": "application/json; charset=utf-8", "X-CSRFToken": csrftoken},
								data: JSON.stringify({
									'success' : rsp.success,
									'imp_uid' : rsp.imp_uid,
									'merchant_uid' : rsp.merchant_uid
								})
								})
								.done(function(res) {
									var b = new Date(res.birthday)
									$('td#cef_name').text(res.name)
									$('td#cef_phone').text(res.phone)
									$('td#cef_birthday').text(`${b.getFullYear()}년 ${b.getMonth()+1}월 ${b.getDate()}일`)
									CommonmodalPopupOpen('인증이 완료되었습니다.');
									$('input[ref=checkrev]').attr('disabled', true).attr('checked',true)									
									$('button[ref=smartrev]').attr('disabled', true)
									$('button[ref=smsrev]').attr('disabled', true)
									//NEXT?
									if(next && !isMobile()) window.location.replace(next);
								})
								.fail(function(res){
									var msg;
									if(res.responseJSON)msg=res.responseJSON.msg
									if(!msg)msg='인증에 실패하였습니다.'
									CommonmodalPopupOpen(msg);
								})
							}
							else { // 실패시
								CommonmodalPopupOpen('인증을 취소하셨습니다.');									
							}
						}
			);      
	}

	function SmartCefSignUp(e){
		e.preventDefault();
		var IMP = window.IMP; // 생략가능
		var next = searchParam('next');
		var _m_redirect_url = `http://${HOST}/mobile/auth/?process=signup&${next==null?'&':'next='+next}`		
		IMP.init(iID);  // 가맹점 식별 코드
		IMP.certification
		(
			{
				pg:'inisis.MIIonenonl',
				merchant_uid : 'merchant_' + new Date().getTime(),
				name : '',
				popup : false,
				request_id:'signup',
				m_redirect_url: _m_redirect_url,
			}, function(rsp) {
						if ( rsp.success ) { // 성공시
							$.ajax({
							url: `http://${HOST}/authsignup/`, // 가맹점 서버
							method: "POST",
							headers: { "Content-type": "application/json; charset=utf-8", "X-CSRFToken": csrftoken},
							data: JSON.stringify({
								'success' : rsp.success,
								'imp_uid' : rsp.imp_uid,
								'merchant_uid' : rsp.merchant_uid,
								'uuid' : uuidv4(),
							})
							})
							.done(function(res) {
								// $('button[type=submit]').attr('disabled', false);
								$('input[ref=checkrev]').attr('disabled', true).attr('checked',true)								
								$('button[ref=smartrev]').attr('disabled', true)
								$('button[ref=smsrev]').attr('disabled', true)
								CommonmodalPopupOpen('인증이 완료되었습니다.');
							})
							.fail(function(res){
								var msg;
								if(res.responseJSON)msg=res.responseJSON.msg
								if(!msg)msg='인증에 실패하였습니다.'
								CommonmodalPopupOpen(msg);
							})
						}
						else { // 실패시
							CommonmodalPopupOpen('인증에 실패하였습니다.');
						}
					}
		);
}

	function SmsCefSignUp(e){
			e.preventDefault();
			var IMP = window.IMP; // 생략가능
			var next = searchParam('next')
			var _m_redirect_url = `http://${HOST}/mobile/auth/?process=signup&${next==null?'&':'next='+next}`
			IMP.init(iID);  // 가맹점 식별 코드
			IMP.certification
			(
				{
					pg:'danal.B010007679',
					merchant_uid : 'merchant_' + new Date().getTime(),
					name : '',
					popup : false,
					request_id:'signup',
					m_redirect_url: _m_redirect_url,
				}, function(rsp) {
							if ( rsp.success ) { // 성공시
								$.ajax({
								url: `http://${HOST}/authsignup/`, // 가맹점 서버
								method: "POST",
								headers: { "Content-type": "application/json; charset=utf-8", "X-CSRFToken": csrftoken},
								data: JSON.stringify({
									'success' : rsp.success,
									'imp_uid' : rsp.imp_uid,
									'merchant_uid' : rsp.merchant_uid,
									'uuid' : uuidv4(),									
								})
								})
								.done(function(res) {
									// $('button[type=submit]').attr('disabled', false);
									$('input[ref=checkrev]').attr('disabled', true).attr('checked',true)									
									$('button[ref=smartrev]').attr('disabled', true)
									$('button[ref=smsrev]').attr('disabled', true)
									CommonmodalPopupOpen('인증이 완료되었습니다.');									
								})
								.fail(function(res){
									var msg;
									if(res.responseJSON)msg=res.responseJSON.msg
									if(!msg)msg='인증에 실패하였습니다.'
									CommonmodalPopupOpen(msg);
								})
							}
							else { // 실패시
								CommonmodalPopupOpen('인증에을 취소하였습니다.');	
							}
						}
			);      
	}

	//OUTDATED
function Danal(e, params){
		e.preventDefault();
		params=JSON.parse(`${params}`);
		var IMP = window.IMP; // 생략가능
		// var next = searchParam('next');
		var _m_redirect_url = `http://${HOST}/checkout/${params.placement.type}/${params.id}/process/`;
		IMP.init(iID);  // 가맹점 식별 코드
		IMP.request_pay
		(
			{
				// pg:'tosspayments.tvivarepublica2',
				// pg:'tosspayments.im_rebnerbyzv',
				// pg:'uplus.im_rebnerbyzv',
				pg:'danal_tpay.A010012249',
				pay_method:'card',
				merchant_uid : `${params.placement.type}_${params.id}_${Date.now()}`,
				name : `${((params.placement.title).replace(/\n/g, "").replace(/\r/g, ""))}*${params.quantity}`,
				amount: params.amountToBePaid,
				buyer_email:params.user.email,
				buyer_tel:params.user.phone,
				buyer_name:params.user.name,

		//	// tax_free: 3000,
		//	// custom_data: { userId: 30930 },		
				// escrow: false,
				// currency: 'KRW',
				// language: 'ko',
				// display: { card_quota: [6] },
				// // appCard: false,
				// useCardPoint: true,
				// app_scheme: `http://${HOST}${PATH}complete`,
				biz_num: '4878802275',
				// bypass: {
				// 	tosspayments: {
				// 		useInternationalCardOnly: false
				// 	}
				// },
				m_redirect_url: _m_redirect_url,
			}, rsp => { //callback(ONLY PC)
				console.log(rsp);
				if (rsp.success || rsp.imp_success || !(rsp.error_msg || rsp.error_code) ) { // 성공시
					if(!(rsp.success && rsp.imp_success)){
						rsp.success='success';
						rsp_imp_success='success';
					}
					$.ajax({
					url: `http://${HOST}/checkout/${params.placement.type}/${params.id}/process/`, // 가맹점 서버
					method: "POST",
					headers: { "Content-type": "application/json; charset=utf-8", "X-CSRFToken": csrftoken},
					data: JSON.stringify({
						'imp_success' : rsp.imp_success,
						'success': rsp.success,
						'imp_uid' : rsp.imp_uid,
						'merchant_uid' : rsp.merchant_uid,
						'uuid' : uuidv4(),
					})
					})
					.done(function(res) {
						var msg;
						if(res){
							msg=res.msg
							paymentData=res.paymentData;
						}
						if(!msg)msg='결제가 완료되었습니다.'
						CommonmodalPopupOpen(msg);
						//결제완료
						if(paymentData)	window.location.href=`http://${HOST}/checkout/${params.placement.type}/${params.id}/complete/?amountToBePaid=${params.amountToBePaid}&card_name=${paymentData.card_name?paymentData.card_name:'토스'}&${paymentData.status=='ready'?'vbank=true':'&'}`;
						else window.location.href=`http://${HOST}/checkout/${params.placement.type}/${params.id}/complete/?amountToBePaid=${params.amountToBePaid}&card_name=카드결제`;
					})
					.fail(function(res){
						var msg;
						if(res.responseJSON)msg=res.responseJSON.msg
						if(!msg)msg='[에러코드:C]결제에 실패하였습니다.'
						CommonmodalPopupOpen(msg);
					})
				}
				else { // 실패시
					if(rsp.error_msg){
						CommonmodalPopupOpen(`${rsp.error_msg}[${rsp.error_code}]`)
					}
					else{
						CommonmodalPopupOpen('[에러코드:D]결제에 실패하였습니다.');
					}

				}
			}
		);

		// IMP.request_pay({
		// 	pg: 'tosspayments', // 반드시 "tosspayments"임을 명시해주세요.
		// 	merchant_uid: 'order_id_1667634130160',
		// 	name: '나이키 와플 트레이너 2 SD',
		// 	pay_method: 'card',
		// 	escrow: false,
		// 	amount: '109000',
		// 	tax_free: 3000,
		// 	buyer_name: '홍길동',
		// 	buyer_email: 'buyer@example.com',
		// 	buyer_tel: '02-1670-5176',
		// 	buyer_addr: '성수이로 20길 16',
		// 	buyer_postcode: '04783',
		// 	m_redirect_url: 'https://helloworld.com/payments/result', // 모바일 환경에서 필수 입력
		// 	notice_url: 'https://helloworld.com/api/v1/payments/notice',
		// 	confirm_url: 'https://helloworld.com/api/v1/payments/confirm',
		// 	currency: 'KRW',
		// 	locale: 'ko',
		// 	custom_data: { userId: 30930 },
		// 	display: { card_quota: [0, 6] },
		// 	appCard: false,
		// 	useCardPoint: true,
		// 	bypass: {
		// 		tosspayments: {
		// 			useInternationalCardOnly: false
		// 		}
		// 	}
		// }, response => {
		// 	console.log('rsp')
		// 	// PC 환경에서 결제 프로세스 완료 후 실행 될 로직
		// })		
}

function Toss(e, params){
	e.preventDefault();	
	var _pay_method=$(e.target).attr('pay_method');
	params=JSON.parse(`${params}`);

	Date.prototype.YYYYMMDDHHMMSS = function () {
		var yyyy = (this.getFullYear()).toString();
		var MM = (this.getMonth()+1).toString().padStart(2,'0');
		var dd = (this.getDate()).toString().padStart(2,'0');
		var hh = (this.getHours()).toString().padStart(2,'0');
		var mm = (this.getMinutes()).toString().padStart(2,'0');
		var ss = (this.getSeconds()).toString().padStart(2,'0');
		return yyyy +  MM + dd+  hh + mm + ss;
	};
	var _vbank_due = new Date(params.due_date);

	var IMP = window.IMP; // 생략가능
	// var next = searchParam('next');
	var _m_redirect_url = `http://${HOST}/checkout/${params.placement.type}/${params.id}/process/`;
	IMP.init(iID);  // 가맹점 식별 코드
	IMP.request_pay
	(
		{
			// pg:'tosspayments.tvivarepublica2', //토스 테스트
			pg:'tosspayments.im_rebnerbyzv', //토스
			// pg:'uplus.im_rebnerbyzv',  //구 토스
			pay_method:_pay_method,
			merchant_uid : `${params.placement.type}_${params.id}_${Date.now()}`,
			name : `${((params.placement.title).replace(/\n/g, "").replace(/\r/g, ""))}*${params.quantity}`,
			amount: params.amountToBePaid,
			buyer_email:params.user.email,
			buyer_tel:params.user.phone,
			buyer_name:params.user.name,
			vbank_due:_vbank_due.YYYYMMDDHHMMSS(),
	//	// tax_free: 3000,
	//	// custom_data: { userId: 30930 },		
			// escrow: false,
			// currency: 'KRW',
			// language: 'ko',
			// display: { card_quota: [6] },
			// appCard: false,
			// useCardPoint: true,
			biz_num: '4878802275',
			// bypass: {
			// 	tosspayments: {
			// 		useInternationalCardOnly: false
			// 	}
			// },
			m_redirect_url: _m_redirect_url,
		}, rsp => { //callback(ONLY PC)
					if (rsp.success || rsp.imp_success || !(rsp.error_msg || rsp.error_code) ) { // 성공시
						if(!(rsp.success && rsp.imp_success)){
							rsp.success='success';
							rsp_imp_success='success';
						}
						$.ajax({
						url: `http://${HOST}/checkout/${params.placement.type}/${params.id}/process/`, // 가맹점 서버
						method: "POST",
						headers: { "Content-type": "application/json; charset=utf-8", "X-CSRFToken": csrftoken},
						data: JSON.stringify({
							'imp_success' : rsp.imp_success,
							'success': rsp.success,
							'imp_uid' : rsp.imp_uid,
							'merchant_uid' : rsp.merchant_uid,
							'uuid' : uuidv4(),
						})
						})
						.done(function(res) {
							var msg;
							if(res){
								msg=res.msg
								paymentData=res.paymentData;
							}
							if(!msg)msg='결제가 완료되었습니다.'
							CommonmodalPopupOpen(msg);
							//결제완료
							if(paymentData)	window.location.href=`http://${HOST}/checkout/${params.placement.type}/${params.id}/complete/?amountToBePaid=${params.amountToBePaid}&card_name=${paymentData.card_name?paymentData.card_name:'토스'}&${paymentData.status=='ready'?'vbank=true':'&'}`;
							else window.location.href=`http://${HOST}/checkout/${params.placement.type}/${params.id}/complete/?amountToBePaid=${params.amountToBePaid}&card_name=카드결제`;
						})
						.fail(function(res){
							var msg;
							if(res.responseJSON)msg=res.responseJSON.msg
							if(!msg)msg='[에러코드:C]결제에 실패하였습니다.'
							CommonmodalPopupOpen(msg);
						})
					}
					else { // 실패시
						if(rsp.error_msg){
							CommonmodalPopupOpen(`${rsp.error_msg}[${rsp.error_code}]`)
						}
						else{
							CommonmodalPopupOpen('[에러코드:D]결제에 실패하였습니다.');
						}

					}
				}
	);

}

	function TabHeightAdjust(){
		var tabWrapper = $(".tab__content");
		var activeTab = tabWrapper.find(".active");
		$(".tab__content").stop().delay(50).animate({
			height: $(".tab__content > .active").outerHeight()
		}, 80, function(){
			//CALLBACK
		});
	}


	/* ************************
  * 더보기
  ************************ */
	function InitSliceItem(unique_classname, init_num=4){
    $(`.${unique_classname}.slice-item`).css('display','none');
    $(`.${unique_classname}.slice-item`).slice(0, init_num).show(function(){
			if($(`.${unique_classname}.slice-item:hidden`).length == 0){
				$(`.${unique_classname}.slice-more-btn`).hide();
			}
			TabHeightAdjust();
		});

    // var tabWrapper = $(".tab__content");
    // var activeTab = tabWrapper.find(".active");
    // var activeTabHeight = activeTab.outerHeight();
    // tabWrapper.height(activeTabHeight);	


    $(`.${unique_classname}.slice-more-btn`).click(function(e){
      e.preventDefault();
      $(`.${unique_classname}.slice-item:hidden`).slice(0,4).show(function(){
        if($(`.${unique_classname}.slice-item:hidden`).length == 0){
          $(`.${unique_classname}.slice-more-btn`).hide();
        }
        // tabWrapper.stop().delay(50).animate({
        //   height: activeTab.outerHeight()
        // }, 500)
				TabHeightAdjust();
    	});
		});
  }