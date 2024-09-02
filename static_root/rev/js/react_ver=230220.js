$(document).ready(function  () {


	/* ************************
	* Advertisement POPUP 버튼
	************************ */
  // inspiration: https://dribbble.com/shots/3003823-Notification-Dropdown
	"use strict";
	const {
		Component
	} = React;
	const {
		Motion,
		StaggeredMotion,
		spring,
		presets
	} = ReactMotion;
	class Media extends Component {
		render() {
			const cls = "nav__notifications__list__item" + (this.props.new ? " nav__notifications__list__item--new" : "");
			return /*#__PURE__*/ React.createElement("a", {
				onMouseDown:()=>{window.location.href=this.props.url},
				href: this.props.url,
			},React.createElement("li", {
				style: this.props.style,
				className: cls
			}, 
			
			/*#__PURE__*/React.createElement("div", {
				className: "nav__notifications__list__item__display"
			}, /*#__PURE__*/React.createElement(Motion, {
				defaultStyle: {
					x: 0.6
				},
				style: {
					x: spring(this.props.open ? 1 : 0.6, presets.wobbly)
				}
			}, interp => /*#__PURE__*/React.createElement("img", {
				src: this.props.imageURL,
				className: "nav__notifications__list__item__photo",
				style: {
					transform: `scale(${interp.x})`
				}
			})),
			/*#__PURE__*/React.createElement("div", {
				className: "nav__notifications__list__item__badge"
			}, /*#__PURE__*/React.createElement(Motion, {
				defaultStyle: {
					x: 0.6
				},
				style: {
					x: spring(this.props.open ? 1 : 0.6, presets.wobbly)
				}
			}, interp => /*#__PURE__*/React.createElement("img", {
				src: this.props.badgeURL,
				className: "nav__notifications__list__item__badge_img",
				style: {
					transform: `scale(${interp.x})`
				}
			})))				
			
			),

		

			
			/*#__PURE__*/React.createElement("div", {
				className: "nav__notifications__list__item__desc"
			}, /*#__PURE__*/React.createElement(Motion, {
				defaultStyle: {
					x: 0
				},
				style: {
					x: spring(this.props.open ? 0 : 1, presets.wobbly)
				}
			}, interp => /*#__PURE__*/React.createElement("div", {
				style: {
					transform: `translateZ(0) translateY(${-15 * interp.x}px)`,
					opacity: 1 - interp.x
				}
			}, /*#__PURE__*/"시간상품 : ",React.createElement("em", null, this.props.title),React.createElement('br'), "설명 : ", React.createElement("em", null, this.props.des)))
			)

			) /* li */
			) /* a */			
		}
	}
	class NotificationsBar extends Component {
		constructor(props) {
			super(props);
			let _media=[];
			const _itemlist = $('.ad-item');
			_itemlist.each((index)=>{
				_media.push({
					imgURL:$(_itemlist[index]).attr('imgURL'),
					badgeURL:$(_itemlist[index]).attr('badgeURL'),					
					title:$(_itemlist[index]).attr('title'),
					des:$(_itemlist[index]).attr('des'),
					url:$(_itemlist[index]).attr('url'),
					new:$(_itemlist[index]).attr('new'),
					total:$(_itemlist[index]).attr('total'),
				})
			})
			this.state = {
				media:_media
			}
		}
		render() {
			const {
				media
			} = this.state;
			const motionParams = media.map(_ => Object.assign({}, {
				h: 0
			}));
			return /*#__PURE__*/React.createElement(Motion, {
				defaultStyle: {
					opacity: 0
				},
				style: {
					opacity: spring(this.props.open ? 1 : 0, presets.stiff)
				}
			}, interpOuter => /*#__PURE__*/React.createElement("div", {
				style: interpOuter,
				className: "nav__notification_bar"
			}, /*#__PURE__*/React.createElement(Motion, {
				defaultStyle: {
					x: 0
				},
				style: {
					x: spring(this.props.open ? 0 : -5, presets.stiff)
				}
			}, interp => /*#__PURE__*/React.createElement("h1", {
				style: {
					transform: `translateY(${interp.x}px)`
				}
			}, /*React.createElement("a",{onMouseDown:()=>{window.location.href="/article/?category=5"}},'특별기획')*/    )), /*#__PURE__*/React.createElement(StaggeredMotion, {
				defaultStyles: motionParams,
				styles: prevInterpolatedStyles => prevInterpolatedStyles.map((_, i) => {
					return i === 0 ? {
						h: spring(this.props.open ? 100 : 0, presets.wobbly)
					} : {
						h: spring(prevInterpolatedStyles[i - 1].h)
					};
				})
			}, interps => /*#__PURE__*/React.createElement("ul", {
				className: "nav__notifications__list"
			}, interps.map((style, i) => /*#__PURE__*/React.createElement(Media, {
				key: i,
				// style: {
				// 	height: style.h
				// },
				imageURL: media[i].imgURL,
				badgeURL: media[i].badgeURL,
				title: media[i].title,
				des: media[i].des,
				url: media[i].url,
				new: media[i].new,
				total:media[i].total,
				open: this.props.open
			}))))));
		}
	}
	class Notifications extends Component {
		constructor(props) {
			super(props);
			this.toggleNotificationBar = this.toggleNotificationBar.bind(this);
			this.count = 0;
		}
		toggleNotificationBar() {
			this.props.toggleNotificationsBar();
		}
		render() {
			return /*#__PURE__*/React.createElement("div", {
				className: "nav__notification"
			}, /*#__아이콘__*/React.createElement(Motion, {
				defaultStyle: {
					x: 0
				},
				style:{
					x: spring(this.props.open ? 0 : 1, presets.stiff)
				}
			}, interp => /*#__PURE__*/
			React.createElement("span", {
				className: "nav__notification__icon",
				style: {
					transform: `translateZ(0) scale(${interp.x})`,
					opacity: interp.x
				},
				onClick: this.toggleNotificationBar
			}, null)),
			React.createElement(Motion, {
				defaultStyle: {
					x: 0
				},
				style: {
					x: spring(this.props.open ? 0 : 1, presets.stiff)
				}
			}, interp =>
			React.createElement("span", {
				className: "nav__notification__num",
				style: {
					transform: `translateZ(0) scale(${interp.x}`,
					opacity: interp.x
				}
			}, $('.ad_num').text())),
			 /*#__PURE__*/React.createElement(NotificationsBar, {
				open: this.props.open
			}), null);
		}
	}
	class NavBar extends Component {
		constructor(props) {
			super(props);
			this.state = {
				isNotificationsOpen: false
			};
			this.toggleNotificationsBar = this.toggleNotificationsBar.bind(this);
			this.closeNotificationsBar = this.closeNotificationsBar.bind(this);
		}
		toggleNotificationsBar(event) {
			this.setState({
				...this.state,
				isNotificationsOpen: !this.state.isNotificationsOpen
			});
			$('#ad').toggleClass('open');
			if(isMobile())htmlScrollControl(true);
			else htmlScrollControl(false);
		}
		closeNotificationsBar(event) {
			if (!this.state.isNotificationsOpen) return;
			this.setState({
				...this.state,
				isNotificationsOpen: false
			});
			$('#ad').removeClass('open');
			htmlScrollControl(false);
		}
		render() {
			return /*#__PURE__*/React.createElement("nav", {
				tabIndex: "0",
				onBlur: this.closeNotificationsBar
			}, /*#__PURE__*/React.createElement(Notifications, {
				toggleNotificationsBar: this.toggleNotificationsBar,
				open: this.state.isNotificationsOpen
			}));
		}
	}
	ReactDOM.render( /*#__PURE__*/React.createElement(NavBar, null), document.getElementById('ad'));
})


