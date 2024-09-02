	//MODAL//
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