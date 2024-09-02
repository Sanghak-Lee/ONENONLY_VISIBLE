/* *******************************************************
 * filename : main.js
 * description :메인에만 사용되는 JS
 * date : 2018-10-23
******************************************************** */

$(document).ready(function  () {
	/* ************************
	* Func : 클라우드펀딩 슬라이드
	************************ */
	if ($.exists(".main-funding-list")) {
		function swap(action) {
			var direction = action;

			//뒤로 이동
			if (direction == "counter-clockwise") {
				var leftitem = $(".left-pos").attr("id") - 1;
				var calc = ( leftitem / itemCount ) * 100;				

				if (leftitem == 0) {
				  leftitem = itemCount;
				}
				$progressBarLabel.css('left', calc + '%');
				$progressBar.attr('aria-valuenow', calc );

				$(".right-pos")
				  .removeClass("right-pos")
				  .addClass("back-pos");
				$(".main-pos")
				  .removeClass("main-pos")
				  .addClass("right-pos");
				$(".left-pos")
				  .removeClass("left-pos")
				  .addClass("main-pos");
				$("#" + leftitem + "")
				  .removeClass("back-pos")
				  .addClass("left-pos");

				startItem--;
				if (startItem < 1) {
				  startItem = itemCount;
				}
			}

			//앞으로 이동
			if (direction == "clockwise" || direction == "" || direction == null) {
				function pos(positionvalue) {
					if (positionvalue != "leftposition") {
						position++;

						if (startItem + position > resetCount) {
						  position = 1 - startItem;
						}
					}

					if (positionvalue == "leftposition") {
						position = startItem - 1;

						if (position < 1) {
						  position = itemCount;
						}
					}

					return position;
				}

				var nextLeftitem = $(".main-pos").attr("id");
				var calcCustom = ( nextLeftitem / itemCount ) * 100;
				//console.log(nextLeftitem);
				if ( nextLeftitem == itemCount ) {
					$progressBarLabel.css('left', 0 + '%');
					$progressBar.attr('aria-valuenow', 0 );
				}else{
					$progressBarLabel.css('left', calcCustom + '%');
					$progressBar.attr('aria-valuenow', calcCustom );
				}

				$("#" + startItem + "")
				  .removeClass("main-pos")
				  .addClass("left-pos");
				$("#" + (startItem + pos()) + "")
				  .removeClass("right-pos")
				  .addClass("main-pos");
				$("#" + (startItem + pos()) + "")
				  .removeClass("back-pos")
				  .addClass("right-pos");
				$("#" + pos("leftposition") + "")
				  .removeClass("left-pos")
				  .addClass("back-pos");

				startItem++;
				position = 0;
				if (startItem > itemCount) {
					startItem = 1;
				}
			}
		}
		//INIT
		$(()=>{
			swap('counter-clockwise');
		})

		var autoSwap = setInterval(swap, 3000);
		$(".main-funding-list").hover(
			function() {
				clearInterval(autoSwap);
			},
			function() {
				clearInterval(autoSwap);
				autoSwap = setInterval(swap, 3000);
			}
		 );

		var items = [];
		var startItem = 1;
		var position = 0;
		var itemCount = $(".main-funding-list").find(".main-funding-item").length;
		var leftpos = itemCount;
		var resetCount = itemCount;
		var $progressBar = $('.main-funding-progress');
		var $progressBarLabel = $progressBar.find( '.progress-bar' );
		var $progressBarW = $progressBar.css("width").replace('px', '');
		$progressBarLabel.css("width", ($progressBarW/itemCount)+"px" );
		$progressBarTop = $(".main-funding-svg").height();
		$progressBar.css("top", $progressBarTop + 10 +"px" );

		if(itemCount == 2){
			$(".main-funding-item").each(function(index){
				if($(this).attr("id")==1) $(this).addClass("main-pos");
				else $(this).addClass("left-pos");
			})
		}else if(itemCount == 3){
			if($(this).attr("id")==1) $(this).addClass("main-pos");
			else if($(this).attr("id")==2) $(this).addClass("right-pos");
			else $(this).addClass("left-pos");
		}else if(itemCount > 3){
			if($(this).attr("id")==1) $(this).addClass("main-pos");
			else if($(this).attr("id")==2)$(this).addClass("right-pos");
			else if($(this).attr("id")==itemCount)$(this).addClass("left-pos");
			else $(this).addClass("back-pos");
		}

		$(window).on("resize", function  () {
			$progressBarTop = $(".main-funding-svg").height();
			$progressBar.css("top", $progressBarTop + 10 +"px" );
		});

		$(".main-funding-item").each(function(index) {
			items[index] = $(this).text();
		});

		//클릭시
		$(".main-funding-item").on("click", function() {
			if ($(this).hasClass("items left-pos")) {
				swap("counter-clockwise");
			} else {
				swap("clockwise");
			}
		});
	}	
	/* ************************
	* Func : 메인 갤러리 슬라이드
	************************ */
	var $mainCelebItem = $('.main-celeb-list');
	var slickOptions = { 		
		slidesToShow: 5,
		slidesToScroll: 1,
		arrows: true,
		fade: false,
		dots:true,
		prevArrow: $('.home.btn.prev-btn'),
		nextArrow: $('.home.btn.next-btn'),
		autoplay: true,
		speed:1000,
		infinite:true,
		autoplaySpeed: 3000,
		easing: 'easeInOutQuint',
		pauseOnHover:false,
		responsive: [
					{
					  breakpoint: 1280,
					  settings: {
						slidesToShow: 4,
						slidesToScroll: 1
					  }
					},
					{
					  breakpoint: 800,
					  settings: {
						slidesToShow: 3,
						slidesToScroll: 1
					  }
					},
					{
					  breakpoint: 640,
					  settings: {
						slidesToShow: 2,
						slidesToScroll: 1
					  }
					},					
					{
					  breakpoint: 480,
					  settings: {
						slidesToShow: 1,
						slidesToScroll: 1
					  }
					},					
				  ]
	};  	
	$mainCelebItem.not('.slick-initialized').slick(slickOptions);

	/* ************************
	* Func : 메인 Q&A
	************************ */
	//FAQ//
	$(".faq-list-con").each(function  () {
		var $faqItem = $(this).find(".faq-item");

		$faqItem.children("dt").click(function  () {
			var $faqCon = $(this).siblings();
			if ($faqCon.css("display") == "block") {
				$(this).siblings().slideUp();
				$(".faq-item").removeClass("open");
			}else {
				$(".faq-item > dd:visible").slideUp();
				$(".faq-item").removeClass("open");
				$(this).parent("dl").addClass("open");
				$faqCon.slideDown();	
			}
		});
	});		
		$('.faq-more').on('click', function(){
			$(this).hide();
			$(".faq-item.hidden").fadeIn();
		})	

});