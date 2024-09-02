/* *******************************************************
 * filename : common.js
 * description : 전체적으로 사용되는 JS
 * Update : 2022-07-15
******************************************************** */

var laptopWidth = 1366;
var tabletWidth = 1220; // 헤더가 변경되는 시점
var mobileWidth = 800;

if ( detectBrowser() === "ie") {
	popupUpdateBrowser();
	convertToEdge();
}
$(window).on('load', function () {
	aosInit ();
	// 영상 자동재생
	if ( $("#cmVideo").length > 0 ) {
		$("#cmVideo").each(function  () {
			$(this).get(0).play();
		});
	}
 });

$(document).ready(function  () {
	/* ************************
	* Func : 브라우저 체크 및 기기체크
	* isMobile() 필요
	************************ */
	if ( isMobile() ) {
		$("body").addClass("is-mobile").addClass(detectOS()+"-os");
	}else {
		$("body").addClass("is-pc").addClass(detectBrowser()+"-browser");
	}
	

	/* ************************
	* Func : 브라우저별 최대 height 체크 & Footer 위치 조정
	************************ */	
	// footeradjust();


	/* ************************
	* Func : Modal Layer Alert Open/Close
	************************ */
	$(".cm-modal-open-btn").click(function () {
		modalAlertToggle(true);
	});

	$(".cm-modal-close-btn").click(function  () {
		modalAlertToggle(false);
	});

	/* ************************
	* Func : 상단 :: 헤더 FIXED
	************************ */	
	$(window).scroll(function  () {
		objectFixed($("#header"), 0, "top-fixed");
	});

	/* ************************
	* Func : 하단 :: top버튼
	************************ */
	$(".to-top-btn").each(function  () {
		$(this).hover(function () {
			$(this).find('#topBtnPath').attr('d', 'M36,7,5,9-7,50,24,67l31-2L67,24Z');
		},function () {
			$(this).find('#topBtnPath').attr('d', 'M52,2,8,10-2,28,8,72l44-8L62,46Z');
		});
		
		// top버튼 나오게 (필요한 경우에만 넣으세요)
		if ( $(this).length > 0 ) {
			$(window).scroll(function  () {
				objectFixed($(".to-top-btn"), 0, "bottom-fixed");
			});
		}
		// top버튼 클릭
		$(this).on("click",function  () {
			moveScrollTop(0, 300);
			return false;
		});
	});

	/* ************************
	* Func : 셀렉트 커스텀
	************************ */
	if ($.exists('select')) {
		$('select').fakeselect();

		$(".cm-selectbox .select-title").click(function () {
			$(this).closest(".cm-selectbox").toggleClass("open");
		});
		$(document).on("click", function(e){ 
			var isParents = isClassName(e.target, 'cm-selectbox');
			if(!isParents) {
				$(".cm-selectbox").removeClass("open");
			}
		});
	}

	/* ************************
		* Func : 스크롤 커스텀
		************************ */
	$(".scroll-object-box").mCustomScrollbar({
		axis:"y",
		theme:"dark",
	});
	$(".scroll-object-box-outside").mCustomScrollbar({
		axis:"y",
		theme:"dark",
		scrollbarPosition : "outside",
	});

	/* ************************
	* Func : 드롭메뉴 공통
	* getWindowWidth () 필요
	************************ */
	$(".cm-drop-menu-box-JS").each(function  () {
		var $dropBox = $(this);
		var $dropOpenBtn = $(this).find(".cm-drop-open-btn-JS");
		var $dropList = $(this).find(".cm-drop-list-JS");
		var eventState = $dropBox.data("drop-event");
		
		if ( eventState === "click" ) {
			$dropOpenBtn.click(function  () {
				$dropList.slideToggle(500);
				$dropBox.toggleClass("open");
				$dropBox.on("mouseleave", function  () {
					dropClose ();
				});
				return false;
			});
			$("body").click(function  () {
				dropClose();
			});
		}else if ( eventState === "hover" ) {
			$dropBox.hover(function  () {
				$dropList.slideDown(500);
				$dropBox.addClass("open");
			},function  () {
				dropClose ();
			});
		}
		function dropClose () {
			if ( $dropBox.data("drop-width") ) {
				if ( getWindowWidth () < $dropBox.data("drop-width")+1 ) {
					$dropList.slideUp(500);
					$dropBox.removeClass("open");
				}
			}else {
				$dropList.slideUp(500);
				$dropBox.removeClass("open");
			}
		}
		$(window).resize(function  () {
			if ( getWindowWidth () > $dropBox.data("drop-width") ) {
				$dropList.removeAttr("style");
			}else {
				$dropList.hide();
			}
		});
	});

	/* ************************
	* Func : 탭 메뉴 공통 사용
	* getWindowWidth () 필요
	************************ */
	$(".cm-tab-container-JS").each(function  () {
		var $cmTabList = $(this).find(".cm-tab-list-JS");
		var $cmTabListli = $cmTabList.find("li");
		var $cmConWrapper = $(this).children(".cm-tab-content-wrapper-JS");
		var $cmContent = $cmConWrapper.children();
		
		
		// 탭 영역 숨기고 selected 클래스가 있는 영역만 보이게
		var $selectCon = $cmTabList.find("li.selected").find("a").attr("href");
		var selectTxt = $cmTabList.find("li.selected").find("em").text();
		$cmContent.hide();
		$($selectCon).show();

		$cmTabListli.children("a").click(function  () {
			if ( !$(this).parent().hasClass("selected")) {
				var visibleCon = $(this).attr("href");
				$cmTabListli.removeClass("selected");
				$(this).parent("li").addClass("selected");
				$cmContent.hide();
				$(visibleCon).fadeIn();
				//slick
				if($(visibleCon).find('.slick-initialized').length>0){
					$(visibleCon).find('.slick-slider').slick('refresh');
				}
			}
			return false;
		});

		// 모바일 버튼이 있을때 추가
		var $cmTabMobileBtn = $(this).find(".cm-tab-select-btn-JS");
		if ($.exists($cmTabMobileBtn)) {
			$cmTabMobileBtn.find("span").text(selectTxt);
			// Mobile Btn Click
			$cmTabMobileBtn.click(function  () {
				$(this).toggleClass("open").siblings().slideToggle();
				return false;
			});

			// Mobile List Click
			$cmTabListli.children("a").click(function  () {
				$cmTabMobileBtn.find("span").text($(this).find("em").text());
				tabListClose();
			});
			$("body").click(function  () {
				tabListClose();
			});
			function tabListClose () {
				if ( getWindowWidth () < 801 ) {
					$cmTabMobileBtn.removeClass("open").siblings().slideUp();
				}
			}
			$(window).resize(function  () {
				if ( getWindowWidth () > 800 ) {
					$cmTabMobileBtn.siblings().removeAttr("style");
				}else {
					$cmTabMobileBtn.siblings().hide()//.css("display","none");
				}
			});
		}
	});

	/* ************************
	* Func : 컨텐츠 메뉴 FIXED 및 클릭시 해당영역 이동
	* getScrollTop(), getWindowWidth(), checkOffset(), toFit(), checkFixedHeight(), moveScrollTop() 필요
	************************ */
	if ($.exists(".cm-fixed-tab-container-JS")) {
		var $fixedMoveTab = $(".cm-fixed-tab-list-JS");		// fixed되는 메뉴 클래스
		var $moveTabItem = $fixedMoveTab.find("li");
		var menuCount= $moveTabItem.length;
		var nav = [];
		
		$(window).on('load', function  () {
			checkStartOffset();
			nav = checkTopOffset();
		});
		$(window).on('resize', function  () {
			checkStartOffset();
			nav = checkTopOffset();
		});

		var isVisible = false;
		$(window).on('scroll',function() {
			if (!isVisible) {
				checkStartOffset();
				nav = checkTopOffset();
				isVisible=true;
			}
		});
		
		// 탭이 붙기 시작하는 지점 체크
		function checkStartOffset () {
			if (($.exists('.ld-tab-wrapper-style')) && (getWindowWidth () > tabletWidth) ) {
				var fixedStartPoint =  $(".cm-fixed-tab-container-JS").offset().top;	
			}else{
				var fixedStartPoint =  $(".cm-fixed-tab-container-JS").offset().top - checkFixedHeight();	
			}
			return fixedStartPoint;
		}		

		// 해당되는 각각의 영역 상단값 측정
		function checkTopOffset () {
			var arr = [];
			for(var i=0;i < menuCount;i++){
				arr[i]=$($moveTabItem.eq(i).children("a").attr("href")).offset().top;
			}
			return arr;
		}
		
		// 스크롤 0일때 상단fixed되는 높이값 체크
		function checkFixedObjectHeight () {
			var fixedObjectTotalHeight = 0;
			for (var i=0; i<$(".top-fixed-object").length; i++) {
				var fixedObjectTotalHeight = fixedObjectTotalHeight + $(".top-fixed-object").eq(i).outerHeight();
			}
			return fixedObjectTotalHeight;
		}

		// 스크롤 event 
		window.addEventListener('scroll', toFit(function  () {
			if ( getScrollTop() >  checkStartOffset() ) {
				$fixedMoveTab.addClass("top-fixed");
			}else if ( getScrollTop() <  (checkStartOffset() + $fixedMoveTab.height()) ) {
				$fixedMoveTab.removeClass("top-fixed");
			}

			$moveTabItem.each(function  (idx) {
				var eachOffset = nav[idx] -  checkFixedHeight();
				var minusOffset = $(window).height() / 6;	// 스크롤시 selected 붙는 지점을 조금 더 빠르게 하기위해 추가
				
				if( (getScrollTop() + minusOffset) >= eachOffset ){
					$moveTabItem.removeClass('selected');
					$moveTabItem.eq(idx).addClass('selected');
					// 모바일 드롭메뉴일때
					if ($.exists($moveTabItem.parents(".cm-drop-menu-box-JS"))) {
						$fixedMoveTab.find(".cm-drop-open-btn-JS > span").text($moveTabItem.eq(idx).find("em").text());
					}
				};
			});
			}, {
		}),{ passive: true })
		
		// 클릭 event 
		$moveTabItem.find("a").click(function  () {
			var goDivOffset = $($(this).attr("href")).offset().top - checkFixedHeight() +1;	// 이동해야할 지점
			if ( getScrollTop()  < checkStartOffset()) {
				if ( getScrollTop() == 0 ) {
					var goDiv = goDivOffset - checkFixedObjectHeight();
				}else {
					var goDiv = goDivOffset - $fixedMoveTab.height();
				}
			}else {
				var goDiv = goDivOffset;
			}
			setTimeout(function  () {
				moveScrollTop(goDiv);
			});

			// 모바일 드롭메뉴일때
			if ($.exists($(this).parents(".cm-drop-menu-box-JS")) ) {
				if ( getWindowWidth () < $fixedMoveTab.data("drop-width")+1 ) {
					$fixedMoveTab.find("ul").slideUp();
				}
			}
			 
			return false;
		});
	}

});


/* ************************
* Func : 유튜브 연결
************************ */
/* 유투브 API 가져오기 */ 
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var done = false;
var player;
var playerID = $("#player").data("code");

function onYouTubeIframeAPIReady() {
	player = new YT.Player('player', {
		playerVars: {
			'autoplay': 1,
			'controls': 0,
			'autohide': 1,
			'wmode': 'opaque',
			'showinfo': 0,
			'loop': 1,
			'mute':0,
			'playsinline':1,
			'playlist': playerID	// Youtube ID
		},
		videoId: playerID,	// Youtube ID
		events: {
			'onReady': onPlayerReady,
			'onStateChange': onPlayerStateChange
		}
	});
}
function onPlayerReady(event) {
	event.target.stopVideo();
	$(".video-iframe-wrapper").on('click', function(){
		if (event.target.getPlayerState() == YT.PlayerState.ENDED) {
			console.log("Video Ended");
			$(".video-cover-box").fadeOut();
			player.playVideo();
		}

		if (event.target.getPlayerState() == YT.PlayerState.PLAYING) {             
			$(".video-cover-box").fadeIn();
			player.pauseVideo();
			if(player.isMuted())player.unMute();
			else player.mute();
			console.log("Video Playing");
		}

		if (event.target.getPlayerState() == YT.PlayerState.PAUSED) {              
				console.log("Video Paused");
				$(".video-cover-box").fadeOut();
				player.playVideo();
		}

		if (event.target.getPlayerState() == YT.PlayerState.BUFFERING) {               
				console.log("Video Buffering");
				$(".video-cover-box").fadeOut();
				player.playVideo();				
		}

		if (event.target.getPlayerState() == YT.PlayerState.CUED) {                
			console.log("Video Cued");			
			$(".video-cover-box").fadeOut();
			player.playVideo();			
		}
	});		
}
function onPlayerStateChange(event) {
	$(".video-cover-box").on("click",function(){
		$(this).fadeOut();
		player.playVideo();
	});
	// $(".video-iframe-wrapper").on('click', function(){
	// 	if (event.data == YT.PlayerState.ENDED) {               
	// 		console.log("Video Ended");
	// 		$(".video-cover-box").fadeOut();
	// 		player.playVideo();
	// 	}

	// 	if (event.data == YT.PlayerState.PLAYING) {             
	// 		$(".video-cover-box").fadeIn();
	// 		player.pauseVideo();
	// 		console.log("Video Playing");
	// 	}

	// 	if (event.data == YT.PlayerState.PAUSED) {              
	// 			console.log("Video Paused");
	// 			$(".video-cover-box").fadeOut();
	// 			player.playVideo();				
	// 	}

	// 	if (event.data == YT.PlayerState.BUFFERING) {               
	// 			console.log("Video Buffering");
	// 			$(".video-cover-box").fadeOut();
	// 			player.playVideo();				
	// 	}

	// 	if (event.data == YT.PlayerState.CUED) {                
	// 		console.log("Video Cued");			
	// 		$(".video-cover-box").fadeOut();
	// 		player.playVideo();			
	// 	}
	// });	
}


