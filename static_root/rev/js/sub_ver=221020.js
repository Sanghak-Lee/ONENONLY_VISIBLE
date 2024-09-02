/* *******************************************************
 * filename : sub.js
 * description : 서브컨텐츠에만 사용되는 JS
 * date : 2022-07-15
******************************************************** */

$(document).ready(function  () {
	/* ************************
	* Func : WHO'S NEXT 슬라이드
	************************ */
	if ($.exists(".unboxing-con02-list")) {
		var $unboxingItem = $(".unboxing-con02-list").find(".unboxing-con02-item").length;
		var $progressBar = $('.unboxing-progress');
		var $progressBarLabel = $progressBar.find( '.progress-bar' );
		var $progressBarW = $progressBar.css("width").replace('px', '');
		$progressBarLabel.css("width", ($progressBarW/$unboxingItem)+"px" );

		$('.unboxing-con02-list').on('beforeChange', function(event, slick, currentSlide, nextSlide) {   
			var calc = ( (nextSlide) / (slick.slideCount) ) * 100;
			$progressBarLabel.css('left', calc + '%');
			$progressBar.attr('aria-valuenow', calc );
		});
		var $WhoSlide = $('.unboxing-con02-list');
		var slickOptionsWho = { 		
			slidesToShow: 4,
			slidesToScroll: 1,
			arrows: false,
			fade: false,
			dots:false,
			autoplay: true,
			speed:1000,
			infinite:true,
			autoplaySpeed: 3000,
			easing: 'easeInOutQuint',
			pauseOnHover:false,
			responsive: [
						{
						  breakpoint: 481,
						  settings: {
							slidesToShow: 1,
							slidesToScroll: 1
						  }
						},
					  ]
		};  	
		if( getWindowWidth () < 481 ) { 			
			$WhoSlide.not('.slick-initialized').slick(slickOptionsWho); 	
		}else{
			if($WhoSlide.hasClass("slick-initialized") === true) {
				$WhoSlide.slick('unslick');
			}
		}
		$(window).on("resize", function  () {
			if( getWindowWidth () < 481 ) { 			
				$WhoSlide.not('.slick-initialized').slick(slickOptionsWho);
			}else{
				if($WhoSlide.hasClass("slick-initialized") === true) {
					$WhoSlide.slick('unslick');
				}
			} 
		});
	}
	/* ************************
	* Func : UNBOXING HISTORY 슬라이드
	************************ */
	if ($.exists(".unboxing-con03-list.history")) {
		var $unboxingItem = $(".unboxing-con03-list.history").find(".unboxing-con03-item").length;
		var $HistorySlide = $('.unboxing-con03-list.history');
		var slickOptionsHistory = {
			slidesToShow: 5,
			slidesToScroll: 5,
			arrows: true,
			prevArrow: $('.btn.prev-btn'),
			nextArrow: $('.btn.next-btn'),
			fade: false,
			dots: true,
			autoplay: true,
			// speed:1000,
			infinite:true,
			autoplaySpeed: 3000,
			easing: 'easeInOutQuint',
			pauseOnHover:false,
			responsive: [
						{
						  breakpoint: 481,
						  settings: {
							centerMode: true,
							slidesToShow: 1,
							slidesToScroll: 1
						  }
						},
						{
						  breakpoint: 801,
						  settings: {
							centerMode: true,
							slidesToShow: 2,
							slidesToScroll: 2
						  }
						}						
					  ]
		};
		$HistorySlide.not('.slick-initialized').slick(slickOptionsHistory);		
		// if( getWindowWidth () < 769 ) { 			
		// 	$HistorySlide.not('.slick-initialized').slick(slickOptionsHistory); 	
		// }else{
		// 	if($HistorySlide.hasClass("slick-initialized") === true) {
		// 		$HistorySlide.slick('unslick');
		// 	}
		// }
		// $(window).on("resize", function  () {
		// 	if( getWindowWidth () < 769 ) {
		// 		$HistorySlide.not('.slick-initialized').slick(slickOptionsHistory);
		// 	}else{ 			
		// 		if($HistorySlide.hasClass("slick-initialized") === true) {
		// 			$HistorySlide.slick('unslick');
		// 		}
		// 	} 
		// });
	}

	/* ************************
	* Func : TIMESTORE ITEM 슬라이드
	************************ */
	$(".unboxing-con03-list.timestore").each(function  () {
		var $unboxingItem = $(this).find(".unboxing-con03-item").length;
		var $HistorySlide = $(this);
		var slickOptionsHistory = {
			centerMode: true,
			centerPadding: '40px',
			slidesToShow: 1,
			arrows: true,
			prevArrow: $HistorySlide.next().find('.btn.prev-btn'),
			nextArrow: $HistorySlide.next().find('.btn.next-btn'),
			fade: false,
			dots: true,
			// autoplay: true,
			// speed:1000,
			infinite: true,
			// autoplaySpeed: 3000,
			easing: 'easeInOutQuint',
			// pauseOnHover:false,
			// responsive: [
			// 				{
			// 					breakpoint: 480,
			// 					settings: {
			// 						centerMode: true,
			// 						slidesToShow: 1
			// 					}
			// 				}
			// 		  ]
		};

		$HistorySlide.not('.slick-initialized').slick(slickOptionsHistory);
		if( getWindowWidth () < 481 ) {
			$HistorySlide.not('.slick-initialized').slick(slickOptionsHistory); 	
		}else{
			if($HistorySlide.hasClass("slick-initialized") === true) {
				$HistorySlide.slick('unslick');
			}			
		}
		$(window).on("resize", function  () {
			if( getWindowWidth () < 481 ) {
				$HistorySlide.not('.slick-initialized').slick(slickOptionsHistory);
			}else{ 			
				if($HistorySlide.hasClass("slick-initialized") === true) {
					$HistorySlide.slick('unslick');
				}
			} 
		});
	})
	


	/* ************************
	* Func : 언박싱 뷰 other 리스트 슬라이드
	************************ */
	$(".unboxing-other-list").slick({
		slidesToShow: 3,
		slidesToScroll: 1,
		arrows: true,
		prevArrow: $('.btn.prev-btn'),
		nextArrow: $('.btn.next-btn'),		
		fade: false,
		dots:false,
		autoplay: true,
		speed:1000,
		infinite:true,
		autoplaySpeed: 3000,
		easing: 'easeInOutQuint',
		pauseOnHover:true,
		responsive: [
					{
					  breakpoint: 481,
					  settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					  }
					},
				  ]	
	});

	/* ************************
	* Func : 펀딩하기 고정바 FIXED
	************************ */	
	$(window).scroll(function  () {
		if ( $(this).length > 0 ) {
			$(window).scroll(function  () {
				objectFixed($(".unboxing-fixed-btn-con"), 0, "bottom-fixed");
			});
		}
	});

	/* ************************
	* Func : 팝업 길어질 때 스크롤
	************************ */	
	customScrollY(".cm-alret-modal-content .popup-inner-con");
	customScrollY(".cm-alret-modal-content .popup-inner-con.long");

	/* ************************
	* Func : 마이페이지 펀딩리스트
	************************ */
	$(".mypage-funding-toggle-JS").each(function  () {
		var $myFundingItem = $(this).find(".funding-item");

		$myFundingItem.children("dt").click(function  () {
			var $myFundingCon = $(this).siblings();
			if ($myFundingCon.css("display") == "block") {
				$(this).siblings().slideUp(function(){
					TabHeightAdjust();
				// footeradjust();
				});
				$(".funding-item").removeClass("open");
			}else {
				$(".funding-item > dd:visible").slideUp();
				$(".funding-item").removeClass("open");
				$(this).parent("dl").addClass("open");
				$myFundingCon.slideDown(function(){
					TabHeightAdjust();
					// footeradjust();
				});
			}		
		});
	});
	/* ************************
	* Func : 서브 탭 FIXED
	************************ */
	if ($.exists(".cm-fixed-page-container-JS")) {
		var $fixedSubMenu = $(".cm-fixed-page-tab-JS");

		$(window).on('load', function  () {
			checkStartOffset();
		});
		$(window).on('resize', function  () {
			checkStartOffset();
		});

		var isVisible = false;
		$(window).on('scroll',function() {
			if (!isVisible) {
				checkStartOffset();
				isVisible=true;
			}
		});
		
		// 탭이 붙기 시작하는 지점 체크
		function checkStartOffset () {
			var fixedStartPoint =  $(".cm-fixed-page-container-JS").offset().top - checkFixedHeight();	
			return fixedStartPoint;
		}	

		window.addEventListener('scroll', toFit(function  () {
			if ( getScrollTop() >  checkStartOffset() ) {
				$fixedSubMenu.addClass("top-fixed");
			}else if ( getScrollTop() <  (checkStartOffset() + $fixedSubMenu.height()) ) {
				$fixedSubMenu.removeClass("top-fixed");
			}
		}, {
		}),{ passive: true })
	}

	/* ************************
	* Func : 회원가입 정보 동의
	************************ */
	$("#checkboxAll").click(function() {
		if($("#checkboxAll").is(":checked")) $("input[type=checkbox].joinCheck").prop("checked", true);
		else $("input[type=checkbox].joinCheck").prop("checked", false);

		if(
			$("input[id=checkbox1-1].joinCheck").is(":checked") &&
			$("input[id=checkbox1-2].joinCheck").is(":checked") &&
			$("input[id=checkbox1-3].joinCheck").is(":checked")
		) $("#joinnext").prop('disabled', false);
		else $("#joinnext").prop('disabled', true);		
	});

	$("input[type=checkbox].joinCheck").click(function() {
		var total = $("input[type=checkbox].joinCheck").length;
		var checked = $("input[type=checkbox].joinCheck:checked").length;

		if(total != checked) $("#checkboxAll").prop("checked", false);
		else $("#checkboxAll").prop("checked", true);

		if(
			$("input[id=checkbox1-1].joinCheck").is(":checked") &&
			$("input[id=checkbox1-2].joinCheck").is(":checked") &&
			$("input[id=checkbox1-3].joinCheck").is(":checked")
		) $("#joinnext").prop('disabled', false);
		else $("#joinnext").prop('disabled', true);
	});

	/* ************************
	* Func : 마이페이지 탭 관리
	************************ */
	// Variables
	var clickedTab = $(".tabs > .active");

	//페이지 로드됐을때 INIT
	if(clickedTab.is($('#tab1'))){
		InitSliceItem('crowd');
		InitSliceItem('open');
		InitSliceItem('openpbd');
		InitSliceItem('secret');
		InitSliceItem('secretpbd');		
	}
	else if(clickedTab.is($('#tab2'))){
		InitSliceItem('like');
	}

	var tabWrapper = $(".tab__content");
	var activeTab = tabWrapper.find(".active");
	var activeTabHeight = activeTab.outerHeight();
	
	// Show tab on page load
	activeTab.show();
	// Set height of wrapper on page load
	tabWrapper.height(activeTabHeight);	
	$(".tabs > li").on("click", function() {
		// //old-active tab stop
		activeTab.stop();

		//slice-item 숨기기
		$('.slice-item').css('display','none');

		// Remove class from active tab
		$(".tabs > li").removeClass("active");
		
		// Add class active to clicked tab
		$(this).addClass("active");
		
		// Update clickedTab variable
		clickedTab = $(".tabs .active");
		
		// fade out activetab
		activeTab.fadeOut(function() {
			// Remove active class all tabs
			$(".tab__content > li").removeClass("active");			
			// Get index of clicked tab
			var clickedTabIndex = clickedTab.index();
			// Add class active to corresponding tab
			$(".tab__content > li").eq(clickedTabIndex).addClass("active");
			// update new active tab
			activeTab = $(".tab__content > .active");
			// Update variable
			activeTabHeight = activeTab.outerHeight();			
			// Animate height of wrapper to new tab height
			tabWrapper.stop().delay(50).animate({
				height: activeTabHeight
			}, 200, function() {
				//Fade out other tab surely
				$(".tab__content > li").not('.active').stop().hide();

				// Fade in active tab
				activeTab.fadeIn(function(){
					if($(this).is($('#tab1_content'))){
						InitSliceItem('crowd');
						InitSliceItem('open');
						InitSliceItem('openpbd');
						InitSliceItem('secret');
						InitSliceItem('secretpbd');
					}
					else if($(this).is($('#tab2_content'))){
						InitSliceItem('like');
					}
				});
			});
		});
	});


});

