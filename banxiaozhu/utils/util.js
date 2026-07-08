var log = require('./log.js');
var app= getApp()
var now = new Date();

/**
* 格式化时间 
* @param {String} date 原始时间格式
* 格式后的时间：yyyy/mm/dd hh:mm:ss
**/

const formatTime = (date) => {
  var year = date.getFullYear();
  var month = date.getMonth() + 1;
  var day = date.getDate();
  var hour = date.getHours();
  var minute = date.getMinutes();
  var second = date.getSeconds();
  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}
function formatNumber(n){
  n = n.toString()
  return n[1] ? n : '0' + n
}


/**
* 从一个数组中随机取出若干个元素组成数组
* @param {Array} arr 原数组
* @param {Number} count 需要随机取得个数
**/
const getRandomArray = (arr, count) => {
  var shuffled = arr.slice(0),
      i = arr.length, 
      min = i - count, 
      temp, 
      index;
  while (i-- > min) {
    index = Math.floor((i + 1) * Math.random());
    temp = shuffled[index];
    shuffled[index] = shuffled[i];
    shuffled[i] = temp;
  }
  return shuffled.slice(min);
}

/**
* 从一个数组中随机取出一个元素
* @param {Array} arr 原数组
**/
const getRandomArrayElement = arr => {
   return arr[Math.floor(Math.random()*arr.length)];
}

function getMonth(date){
  var date = new Date();
  var year = date.getFullYear();
  var month = date.getMonth() + 1;
  var day = date;
  if (month < 10) {
    month = '0' + month;
  };
  if (day < 10) {
    day = '0' + day;
  };
  // 如果需要时分秒 
  // var h = now.getHours(); 
  // var m = now.getMinutes(); 
  // var s = now.getSeconds(); 
  var formatMonth = year  + month ;
  return formatMonth;
} 

function getPreMonth(date){
  // var now = new Date();
  var year = date.getFullYear();
  var month = date.getMonth() ;
  var day = date;

  console.log('month',month)
  if (month < 10) {
    month = '0' + month;
  };
  if (day < 10) {
    day = '0' + day;
  };
  if(month==0){
    year= (year -1) ;
    month ='12'
  }
  console.log(year,month)
  var formatMonth = year  + month ;
  return formatMonth;
} 

  //获取星期
function  getWeek(date) {
    let weekArray = ['日', '一', '二', '三', '四', '五', '六'];
    return weekArray[date.getDay()];
}

function getMonthFirstDate(){
  var today = new Date();
  var month = today.getMonth();
  var weekday = _this.getWeek(now);
  var day = today.getDate();
  var prevMonth = month==0 ? 11 : month-1;
  var nextMonth = month==11 ? 0 : month+1;
  var lastDay = new Date((new Date().setMonth(month + 1, 1) - 1000 * 60 * 60 * 24)).getDate(); //获取当月最后一天日期;
  var prevLastDay = new Date((new Date().setMonth(month, 1) - 1000 * 60 * 60 * 24)).getDate(); //获取上一个月最后一天日期; 
  return lastDay
}

function getLastMonthLastDate(){
  var today = new Date();
  var day = now.getDate();
  var month = now.getMonth();
  // var weekday = _this.getWeek(today());

  var prevMonth = month==0 ? 11 : month-1;
  var nextMonth = month==11 ? 0 : month+1;
  var lastDay = new Date((new Date().setMonth(month + 1, 1) - 1000 * 60 * 60 * 24)).getDate(); //获取当月最后一天日期;
  var prevLastDay = new Date((new Date().setMonth(month, 1) - 1000 * 60 * 60 * 24)).getDate(); //获取上一个月最后一天日期; 
  return prevLastDay
}

function getToday() {
  var now = new Date();
  var year = now.getFullYear();
  var month = now.getMonth()+1;
  var day = now.getDate();
  if (month < 10) {
    month = '0' + month;
  };
  if (day < 10) {
    day = '0' + day;
  };
  // 如果需要时分秒 
  // var h = now.getHours(); 
  // var m = now.getMinutes(); 
  // var s = now.getSeconds(); 
  var todayDate = year + '-' + month + '-' + day;
  console.log('gettoday()',todayDate)
  return todayDate;
}

function dateDelta(currentdate, deltadays){
  var thatdate = new Date(currentdate)
  console.log(1,thatdate)
  var returndate = thatdate.setDate(thatdate.getDate(currentdate) + deltadays);
  console.log(2,returndate)

  thatdate.getDate(returndate)
  console.log('returndate',returndate, thatdate.getDate(returndate),thatdate)
  // return thatdate
  var year = thatdate.getFullYear()
  var month = thatdate.getMonth()+1
  if (month<9){
    month ='0'+month
  } else{
    month = month
  }
  var date2 = thatdate.getDate()
  console.log(year+'-'+month+'-'+date2)
  return year+'-'+month+'-'+date2
}

function datetostr(option){
  var thatdate=new Date(option)
  console.log('datetostr in ',option, thatdate)
  thatdate.setDate(thatdate.getDate(option))
  var year = thatdate.getFullYear()
  var month = thatdate.getMonth()+1
  var day = thatdate.getDate()
  if (month<10){
    month ='0'+month
  }
  if (day<10){
    day='0'+day
  }
  console.log('datatostr out',year.toString()+month.toString()+day.toString())
  return year.toString()+month.toString()+day.toString()
  // return date.split('-').join('')
}

function strtodate(str){
  return str.substring(0,4)+'-'+str.substring(4,6)+'-'+str.substring(6,8)
}

function uuidtostr(s){
  return s.split('-').join('') 
}

function strtouuid(s){
  return s.substring(0, 8) + '-' + s.substring(8, 12) + '-' + s.substring(12, 16) + '-' + s.substring(16, 20)+ '-' + s.substring(20, 32) 
}

//替换URL中特殊字符
function replaceSpecialChar(url) {
  url = url.replace(/"/g, '"');
  url = url.replace(/&/g, '&');
  url = url.replace(/</g, '<');
  url = url.replace(/>/g, '>');
  url = url.replace(/ /g, ' ');
  console.log("转义字符", url);
  return url;
}


function login(that,event) {
  wx.login({
    success: res => {
      console.log(res)
      //请求后端换取openid的接口
      http.request({
        url: '/get-openid/',
        method: 'POST',
        data: {
          //将code传到后端
          jscode: res.code
        },
        success: res => {
          //获取到openid作为账号密码
          console.log(res)
          console.log(app.globalData.userInfo)
          http.request({
            url: '/wx-login/',
            method: 'POST',
            data: {
              openid: res.openid,
              // session_key: res.session_key,
              nickname: app.globalData.userInfo.nickName,
              avatar_url: app.globalData.userInfo.avatarUrl,
              gender: app.globalData.userInfo.gender
            },
            //登录成功后返回token保存在storage中
            success: res => {
              console.log(res)
              //token存入storage
              wx.setStorageSync('jwt_token', res.token)
              wx.setStorageSync('user_id', res.user_id)
              // that.reFreshUserProfile()
              //登录状态置为true
              that.setData({
                isLogin: true,
                hasUserInfo: true
              })
              app.globalData.isLogin = true
            }
          })

        }
      })
    }
  })
}

function logout(that,res) {
  
  that.setData({
    isLogin: false,
    hasUserInfo: false
  })
  app.globalData.isLogin = false
  wx.removeStorageSync('jwt_token')
  wx.removeStorageSync('user_id')
}

function get_indexImageUrl(){
  var app=getApp()
  app.globalData.indexImageUrl=[
    'https://images.unsplash.com/photo-1551334787-21e6bd3ab135?w=640',
    'https://images.unsplash.com/photo-1551214012-84f95e060dee?w=640',
    'https://images.unsplash.com/photo-1551446591-142875a901a1?w=640'
  ]

  var url = app.globalData.host + 'baseinfo/get_indexImageUrl/'
  console.log('begin get_indexImageUrl')

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      appcode:  app.globalData.appcode,
      page: 'index'
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      log.info('get_indexImageUrl success.res', res)
      if (res.statusCode === 200 && res.data && res.data.length && typeof res.data[0] === 'string') {
        app.globalData.indexImageUrl = res.data
        try {
          var pages = getCurrentPages()
          var page = pages[pages.length - 1]
          if (page && page.route === 'index/index') {
            page.setData({ imgUrls: res.data })
          }
        } catch (e) { }
      }
    },
    fail: function (res) {
      console.log('get_indexImageUrl fail.res',res)
    },
    complete: function (res) {
      console.log("get_indexImageUrl finished",res)
    }
  })
  console.log('end get_indexImageUrl')
}

function showLoading(message) {
  if (wx.showLoading) {
    // 基础库 1.1.0 微信6.5.6版本开始支持，低版本需做兼容处理
    wx.showLoading({
      title: message,
      mask: true
    });
  } else {
    // 低版本采用Toast兼容处理并将时间设为20秒以免自动消失
    wx.showToast({
      title: message,
      icon: 'loading',
      mask: true,
      duration: 20000
    });
  }
}

function hideLoading() {
  if (wx.hideLoading) {
    // 基础库 1.1.0 微信6.5.6版本开始支持，低版本需做兼容处理
    wx.hideLoading();
  } else {
    wx.hideToast();
  }
}

function buttonClicked(that) {
  that.setData({
    buttonClicked: true
  })
  setTimeout(function () {
    that.setData({
      buttonClicked: false
    })
  }, 500)
}

function get_nextvcode(that){
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_nextvcode/';
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      pmcode:app.globalData.ecode
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('res:',res)
      that.setData({
        vcode: res.data
      })
      
      return res.data

    },
    fail: function (res) {
      console.log("failed")
      return 'error'
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function get_nextccode(that,vcode) {
  var app = getApp();
  var url = app.globalData.host + 'adviser/get_nextccode/';
  console.log(url,vcode)
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      vcode: vcode
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('nextccode res.data:', res.data)
      that.setData({
        newccode: res.data
      })
      return res.data

    },
    fail: function (res) {
      console.log("failed")
      return 'error'
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function get_source(that) {
  var app = getApp()
  // var that = this
  var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      seg: 'source'
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res)
      app.globalData.sourcelist=res.data
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}    

function get_PsStatusList(that) {
  var app = getApp()
  // var that = this
  var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      seg: 'psstatus'
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res)
      app.globalData.psstatuslist = res.data
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}    

function get_vipcasetype() {
  var app = getApp()
  // var that = this
  var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      seg: 'vipcasetype'
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('getvipcasetype.res',res)
      app.globalData.vipcasetypeList = res.data
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}   

function get_stypelist() {
  var app = getApp()
  // var that = this
  var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'
  console.log('begin get_stypelist')

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      seg: 'stype'
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      log.info('getstypelist success.res', res)
      app.globalData.stypelist = res.data
    },
    fail: function (res) {
      console.log('getstypelist fail.res',res)
    },
    complete: function (res) {
      console.log("getstypelist finished",res)
    }
  })
  console.log('end get_stypelist')

}   

function get_appoption_byseg(that,options) {
  var app = getApp()
  var seg = options.seg
  var list= options.list
  // var that = this
  var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      seg: seg
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res)
      var key='app.globalData.'+list
      // [key]=res.data
      app.globalData.sourcelist = res.data
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}   

function get_empllist(that){
  
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_empllist/';
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_pmcodelist res.data',res.data)
      app.globalData.empllist=res.data
    },
    fail: function (res) {
      console.log("failed")
      
      // return []
    },
    complete: function (res) {
      console.log("finished")
    }
  });  
}

function get_pmcodelist(that) {
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_pmcodelist/';
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_pmcodelist res.data',res.data)
      app.globalData.pmcodelist=res.data
    },
    fail: function (res) {
      console.log("failed")
      
      // return []
    },
    complete: function (res) {
      console.log("finished")
    }
  });
} 

function get_seccodelist(that) {
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_seccodelist/';
  console.log('get_seccodelist param',app.globalData.company,app.globalData.storecode)
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_seccodelist res.data',res.data)
      app.globalData.seccodelist = res.data
      wx.setStorage({
        key: 'seccodelist',
        data: res.data,
      })
    },
    fail: function (res) {
      console.log("failed")
      return []
    },
    complete: function (res) {
      console.log("finished")
    }
  });
}

function get_cardtypelist(that) {
  // var that = this;
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_cardtypelist'
  wx.request({
    url: url,
    data: {
      company: app.globalData.company,
      suptype: '10'
    },
    method: 'GET',
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      // return res.data
      app.globalData.cardtype10list=res.data
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  });
  var url = app.globalData.host + 'baseinfo/get_cardtypelist'
  wx.request({
    url: url,
    data: {
      company: app.globalData.company,
      suptype: '20'
    },
    method: 'GET',
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      // return res.data
      app.globalData.cardtype20list=res.data
    },
    fail: function (res) {
      console.log("failed")
      return []
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function get_amountcardtypelist() {
  // var that = this;
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_cardtypelist'
  wx.request({
    url: url,
    data: {
      company: app.globalData.company,
      comptype: 'amount'
    },
    method: 'GET',
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
        app.globalData.amountcardtypelist = res.data
        console.log('app.globalData.amountcardtypelist:',app.globalData.amountcardtypelist)
    },
    fail: function (res) {
      console.log("failed")
      return []
    },
    complete: function (res) {
      console.log("finished")
    }
  });
}

function get_timescardtypelist(that) {
  // var that = this;
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_cardtypelist'
  wx.request({
    url: url,
    data: {
      company: app.globalData.company,
      comptype: 'times'
    },
    method: 'GET',
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      app.globalData.timescardtypelist = res.data
    },
    fail: function (res) {
      console.log("failed")
      return []
    },
    complete: function (res) {
      console.log("finished")
    }
  });
}

function get_periodcardtypelist(that) {
  // var that = this;
  var app = getApp();
  var url = app.globalData.host + 'baseinfo/get_cardtypelist'
  wx.request({
    url: url,
    data: {
      company: app.globalData.company,
      comptype: 'period'
    },
    method: 'GET',
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_periodcardtypelist res.data',res.data)
      app.globalData.periodcardtypelist = res.data
    },
    fail: function (res) {
      console.log("failed")
      return []
    },
    complete: function (res) {
      console.log("finished")
    }
  });
}

function get_VipList() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "baseinfo/get_viplist_byecode/";
  console.log(url);
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode
    },
    // header: {
    //   'content-type': 'application/json' // 默认值
    // },
    success(res) {
      console.log('get_VipList res.data:', res.data)
      app.globalData.viplist= res.data
      wx.setStorage({
        key: 'viplist',
        data: res.data
      })
    },
    fail(res) {
      // console.log(data)
      console.log(res)
    }
  });
}

function get_Vip10List() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "adviser/get_vipList_byviptypeandecode/"
  // var url = host + "baseinfo/vip/";
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode:app.globalData.storecode,
      ecode: app.globalData.ecode,
      viptype:'10'
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_Vip10List res.data:', res.data)
      app.globalData.vip10list = res.data
    },
    fail(res) {
      // console.log(data)
      console.log(res)
    }
  });
}

function get_Vip20List() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "adviser/get_vipList_byviptypeandecode/"
  // var url = host + "baseinfo/vip/";
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode,
      viptype: '20'
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_Vip20List res.data:', res.data)
      app.globalData.vip20list = res.data
    },
    fail(res) {
      // console.log(data)
      console.log(res)
    }
  });
}

function get_Vip30List() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "adviser/get_vipList_byviptypeandecode/"
  // var url = host + "baseinfo/vip/";
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode,
      viptype: '30'
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_Vip30List res.data:', res.data)
      app.globalData.vip30list = res.data
    },
    fail(res) {
      // console.log(data)
      console.log(res)
    }
  });
}

function get_VipInList() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "adviser/get_viplist_bylevel/"
  // var url = host + "baseinfo/vip/";
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      ecode:app.globalData.ecode,
      rpttype:'in'
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_VipInList res.data:', res.data)
      app.globalData.vipinlist = res.data
    },
    fail(res) {
      // console.log(data)
      console.log(res)
    }
  });
}

function get_VipNotinList() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "adviser/get_viplist_bylevel/"
  // var url = host + "baseinfo/vip/";
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode,
      rpttype: 'notin'
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_VipNotinList res.data:', res.data)
      app.globalData.vipnotinlist = res.data
    },
    fail(res) {
      // console.log(data)
      console.log(res)
    }
  });
}

function get_VipcntList(that,querymonth,key){
  var app =getApp()
  var url = app.globalData.host + "report/get_invipcnt"
  wx.request({
    method: 'GET',
    url: url,
    data: {
      appcode: app.globalData.appcode,
      openid: app.globalData.openid,
      month: querymonth
    },
    success: (res) => {
      console.log('get_Vipcnt',res.data)
      app.globalData.vipCntList= res.data
      that.setData({
        [key]: res.data
      })
    },
    fail: (res) => {
      console.log(res)
    },
    complete: (res) => {
      console.log(res)
    }
  })  
}

function get_DailyStoreData(that,fromdate,todate){
  var app =getApp()
  var storedata = []
  var url = app.globalData.host + "report/get_dailystoredata"
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company:app.globalData.company,
      storecode: '01',
      appcode: app.globalData.appcode,
      openid: app.globalData.openid,
      fromdate: fromdate,
      todate: todate
    },
    success: (res) => {
      console.log('get_DailyStoreData res.data:',res.data)
      if (res.statusCode === 200){
        that.data.storelist.forEach((storecode) => {
          var cells = res.data.filter(item => item.storecode == storecode)
          // var vsdate = that.data.vipcntlist.filter(vsdate => item.storecode === storecode).vsdate
    
          console.log('cells',cells)
          storedata.push({
            storecode,
            cells
          })
        })
        var key = 'thismonthdata'
        that.setData({
          [key]: res.data,
          storedata:storedata
        })
      }
    },
    fail: (res) => {
      console.log('get_DailyStoreData fail',res)
    },
    complete: (res) => {
      console.log(res)
    }
  })  
}
// 获取服务项目
function get_SrvList(that) {
  var app = getApp();
  var url = app.globalData.host + "adviser/get_vip_itemlist"
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      vipuuid: app.globalData.currentvip.uuid,
      ttype: 'S'
    },
    success: (res) => {
      console.log('get_SrvList',res.data)
      app.globalData.srvList= res.data
      wx.setStorage({
        key: 'srvlist',
        data: res.data
      })
      // that.setData({
      //   srvlist: res.data
      // })
      // that.init_srvList()
    },
    fail: (res) => {
      console.log(res)
    },
    complete: (res) => {
      console.log(res)
    }
  })
} 

// 获取商品项目
function get_GoodsList(that) {
  var app = getApp();
  var url = app.globalData.host + "adviser/get_vip_itemlist"
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      vipuuid: app.globalData.currentvip.uuid,
      ttype: 'G'
    },
    success: (res) => {
      console.log('get_GoodsList res.data',res.data)
      app.globalData.goodslist= res.data
      wx.setStorage({
        key: 'goodslist',
        data: res.data
      })
      // that.setData({
      //   goodslist:res.data
      // })
      // that.init_srvList()
    },
    fail: (res) => {
      console.log(res)
    },
    complete: (res) => {
      console.log(res)
    }

  })
} 

function get_RoomList() {
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "baseinfo/get_roomlist/";
  console.log(url);
  wx.request({
    method: 'GET',
    url: url, 
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_RoomList res.data', res.data)
      app.globalData.roomlist=res.data
      wx.setStorage({
        key: 'roomlist',
        data: res.data
      })
    }
  });

}

function get_InstrumentList() {
  // this.getNowTime()
  var app = getApp();
  var host = app.globalData.host;
  var company = app.globalData.company
  var url = host + "baseinfo/get_instrumentlist/";
  // var url = host + "baseinfo/vip/";
  console.log(url);
  wx.request({
    method: 'GET',
    url: url, //仅为示例，并非真实的接口地址
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log(' get_InstrumentList res.data', res.data)
      app.globalData.instrumentlist=res.data
      wx.setStorage({
        key: 'instrumentlist',
        data: res.data
      })
    }
  });
}

function get_emplarch_bymonth(that) {
  // this.getNowTime()
  var app = getApp();
  var host = app.globalData.host;
  var company = app.globalData.company
  var today = new Date();
  var thisyear = today.getFullYear();
  var thismonth = this.getMonth(today);
  console.log('this month=', thismonth)

  if (today.getMonth() == 1) {
    var lastyear = (thisyear - 1).toString()
    var lastmonth = lastyear + '12'
    console.log(lastmonth)

  } else {
    var lastyear = thisyear.toString()
    var lastmonth = today.getMonth()
    if (lastmonth < 9) {
      lastmonth = lastyear + '0' + lastmonth
      console.log(lastmonth)
    }
  }

  // 取上个月的数据
  var url = host + "cashier/get_emplarch_bymonth/";
  wx.request({
    method: 'GET',
    url: url, //仅为示例，并非真实的接口地址
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode:app.globalData.ecode,
      month:lastmonth
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      res.data.forEach((item) => {
        item.yejiamount = Number(item.yejiamount).toFixed(2); 
        item.shihao = Number(item.shihao).toFixed(2); 
        item.shichao = Number(item.shichao).toFixed(2);
      })

      app.globalData.lastmonth_emplarch=res.data
      that.setData({
        lastmonth: lastmonth,
        lastmonth_emplarch: res.data
      })
      var vipcnt = 0
      var viptimes = 0
      var yeji = 0
      var shihao = 0
      var shichao = 0
      var jidian = 0
      for (var item in that.data.lastmonth_emplarch) {
        vipcnt = vipcnt + that.data.lastmonth_emplarch[item].vipcnt
        viptimes = viptimes + that.data.lastmonth_emplarch[item].viptimes
        yeji = yeji + Number(that.data.lastmonth_emplarch[item].yejiamount)
        shihao = shihao + Number(that.data.lastmonth_emplarch[item].shihao)
        shichao = shichao + Number(that.data.lastmonth_emplarch[item].shichao)        
      }
      that.setData({
        lastmonth_vipcnt: vipcnt,
        lastmonth_viptimes: viptimes,
        lastmonth_yeji: yeji.toFixed(2),
        lastmonth_shihao: shihao.toFixed(2),
        lastmonth_shichao: shichao.toFixed(2)
      })
    }
  });

  // 取当月数据
  wx.request({
    method: 'GET',
    url: url, //仅为示例，并非真实的接口地址
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode,
      month: thismonth
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      res.data.forEach((item) => {
        item.yejiamount = Number(item.yejiamount).toFixed(2);
        item.shihao = Number(item.shihao).toFixed(2);
        item.shichao = Number(item.shichao).toFixed(2);
      })

      app.globalData.thismonth_emplarch=res.data
      that.setData({
        thismonth: thismonth,
        thismonth_emplarch: res.data
      })
      var vipcnt = 0
      var viptimes = 0
      var yeji = 0
      var shihao = 0
      var shichao = 0
      for (var item in that.data.thismonth_emplarch) {
        vipcnt = vipcnt + that.data.thismonth_emplarch[item].vipcnt
        viptimes = viptimes + that.data.thismonth_emplarch[item].viptimes
        yeji = yeji + Number(that.data.thismonth_emplarch[item].yejiamount)
        shihao = shihao + Number(that.data.thismonth_emplarch[item].shihao)
        shichao = shichao + Number(that.data.thismonth_emplarch[item].shichao)
      }
      that.setData({
        thismonth_vipcnt: vipcnt,
        thismonth_viptimes: viptimes,
        thismonth_yeji: yeji.toFixed(2),
        thismonth_shihao: shihao.toFixed(2),
        thismonth_shichao: shichao.toFixed(2)
      })
    }
  });
}

function openToast(option) {
  wx.showToast({
    title: option.title,
    icon: option.icon,//success
    duration: 3000
  });
}

function openLoading (option) {
  wx.showToast({
    title: option.title,
    icon: option.icon,  //'loading',
    duration: 3000
  });
}

function checkNetwork(that){
  var app = getApp();
  // var that = this;
  // console.log('checkNetwork e:', e)
  that.setData({
    showTopTips: false,
    errormsg: '登陆时发生错误'
  })
  wx.startWifi({
    success(res) {
      console.log('startWifi success',res.errMsg)
    },
    fail(res){
      console.log('startWifi fail', res)
      return false
    }
  })
  wx.getNetworkType({
    success(res) {
      console.log('getNetworkType', res.networkType)
      var networkType = res.networkType
      if (networkType=='wifi'){
        wx.getConnectedWifi({
          success: function (res) {
            console.log('getConnectedwifi res', res)
            var wf = res && res.wifi ? res.wifi : {}
            that.setData({
              networkType: networkType,
              local_SSID: wf.SSID || '',
              local_BSSID: wf.BSSID || ''
            })
            var url = app.globalData.host + 'common/check_wifilist/'
            console.log(url);
            wx.request({
              method: 'GET',
              url: url, //仅为示例，并非真实的接口地址
              data: {
                // company: that.data.company,
                // storecode:that.data.storecode,
                networktype: that.data.networkType,
                ssid: that.data.local_SSID,
                bssid: that.data.local_BSSID
                // ecode:that.data.usercode
              },
              header: {
                'content-type': 'application/json' // 默认值
                // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
              },
              success(res) {
                console.log('checkNetwork: ', res)
                var payload = res && res.data
                if (
                  res.statusCode !== 200 ||
                  payload == null ||
                  typeof payload !== 'object' ||
                  Array.isArray(payload)
                ) {
                  console.warn('check_wifilist 响应异常', res.statusCode, payload)
                  that.setData({
                    wifi_flag: true,
                    bssid_flag: false,
                    showTopTips: true,
                    errormsg: '门店网络校验接口异常'
                  })
                  setTimeout(function () {
                    that.setData({ showTopTips: false })
                  }, 3000)
                  return
                }
                var company = payload.company != null ? String(payload.company) : ''
                var companyname = payload.companyname != null ? String(payload.companyname) : ''
                var storecode = payload.storecode != null ? String(payload.storecode) : ''
                var storename = payload.storename != null ? String(payload.storename) : ''
                console.log('log info:', company, companyname, storecode, storename, company.length)

                if (company.length > 0) {
                  var bssid_flag = true
                } else {
                  var bssid_flag = false
                }
                console.log('bssid_flag', bssid_flag)
                that.setData({
                  company: company,
                  storecode: storecode,
                  companyname:companyname,
                  storename:storename,
                  wifi_flag: true,
                  bssid_flag: bssid_flag
                })
                app.globalData.networkenable=true
                app.globalData.company=that.data.company
                app.globalData.companyname = companyname
                app.globalData.storecode = that.data.storecode
                app.globalData.storename = storename
                app.globalData.local_SSID = that.data.local_SSID
                app.globalData.local_BSSID = that.data.local_BSSID
                app.globalData.networkType = networkType
                app.globalData.bssid_flag = bssid_flag

                console.log('app.globalData.local_SSID', that.data.local_SSID)

                if (app.globalData.isDev) { 
                  wx.reLaunch({
                    url: '/my/login/login',
                  })
                } else {
                  app.globalData.networkenable = true
                  app.globalData.company = that.data.company
                  app.globalData.companyname = companyname
                  app.globalData.storecode = that.data.storecode
                  app.globalData.storename = storename
                  app.globalData.local_SSID = that.data.local_SSID
                  app.globalData.local_BSSID = that.data.local_BSSID
                  app.globalData.networkType = networkType
                  app.globalData.bssid_flag = bssid_flag

                  that.data.networkType = networkType
                  that.data.bssid_flag = bssid_flag

                  if (that.data.bssid_flag) {
                    wx.reLaunch({
                      url: '/my/login/login',
                    })
                  }
                }
                return true
              },
              fail(res) {
                console.log('getConnectedWifi fail res:', res)
                that.setData({
                  wifi_flag: true,
                  bssid_flag: false,
                  showTopTips: true,
                  errormsg: '网络检测失败'
                })
                setTimeout(function () {
                  that.setData({
                    showTopTips: false
                  });
                }, 3000);
                app.globalData.tempnetwork.networkenable = false
                app.globalData.tempnetwork.company = ''
                app.globalData.tempnetwork.companyname=''
                app.globalData.tempnetwork.storecode = ''
                app.globalData.tempnetwork.storename=''
                app.globalData.tempnetwork.local_SSID = that.data.local_SSID
                app.globalData.tempnetwork.local_BSSID = that.data.local_BSSID
                app.globalData.tempnetwork.bssid_flag = false
                return false
              }
            })
          },

          fail: function (res) {
            console.log('getConnectedWifi fail res:',res)
            app.globalData.tempnetwork.networkenable = true
            app.globalData.tempnetwork.company = app.globalData.democompany
            app.globalData.tempnetwork.companyname =app.globalData.democompanyname
            app.globalData.tempnetwork.storecode = app.globalData.demostorecode
            app.globalData.tempnetwork.storename =app.globalData.demostorename
            app.globalData.tempnetwork.ecode = app.globalData.ecode
            app.globalData.tempnetwork.local_SSID = ''
            app.globalData.tempnetwork.local_BSSID = ''
            app.globalData.tempnetwork.networkType = networkType
            app.globalData.tempnetwork.bssid_flag = false
            app.globalData.isDev=true

            that.setData({
              wifi_flag: false,
              bssid_flag: false,
              showTopTips: true,
              errormsg: '未连接网络',
              isDev:true
            })
            setTimeout(function () {
              that.setData({
                showTopTips: false
              });
            }, 3000);

            if (app.globalData.isDev) {
              wx.reLaunch({
                url: '/my/login/login',
              })
            }
            return false
          }
        })
      } 
      else {
        //    非wifi环境
        console.log('networkType=',networkType)
        that.setData({
          company:app.globalData.democompany,
          storecode:app.globalData.demostorecode,
          companyname:app.globalData.democompanyname,
          storename:app.globalData.demostorename,
          usercode:app.globalData.demostorecode,
          isDev:true
        })
        // app.globalData.tempnetwork.networkenable = true
        // app.globalData.tempnetwork.company = app.globalData.democompany
        // app.globalData.tempnetwork.companyname =app.globalData.democompanyname
        // app.globalData.tempnetwork.storecode = app.globalData.demostorecode
        // app.globaldata.tempnetwork.storename =app.globaldata.demostorename
        // app.globalData.tempnetwork.usercode = app.globalData.demoecode
        // app.globalData.tempnetwork.local_SSID = ''
        // app.globalData.tempnetwork.local_BSSID = ''
        // app.globalData.tempnetwork.networkType = networkType
        // app.globalData.tempnetwork.bssid_flag = false

        app.globalData.isDev=true

        if (app.globalData.isDev) {
          wx.reLaunch({
            url: '/my/login/login',
          })
        }
      }
    },
    // 检测网络失败
    fail(res) {
      console.log('getNetworkType fail', res)
      app.globalData.network_allow_flag = false
      that.setData({
        wifi_flag: false,
        bssid_flag: false,
        showTopTips: true,
        errormsg: '非知网络连接类型'
      })
      setTimeout(function () {
        that.setData({
          showTopTips: false
        });
      }, 3000);
      return false
    }
  })
}

function get_bssid(){
  var app=getApp()
  wx.getNetworkType({
    success(res) {
      var networkType = res.networkType
      if (networkType=='wifi'){
        wx.getConnectedWifi({
          success: function (res) {
            console.log('getConnectedwifi res', res)
            return res.wifi.BSSID
          },

          fail: function (res) {
            return ''
          }
        })
      } else {
        return ''
      }

    },

    // 检测网络失败
    fail(res) {
      console.log('fail', res)
      app.globalData.network_allow_flag = false
      that.setData({
        wifi_flag: false,
        bssid_flag: false,
        showTopTips: true,
        errormsg: '非知网络连接类型'
      })
      setTimeout(function () {
        that.setData({
          showTopTips: false
        });
      }, 3000);
      return false
    }
  })
}

function get_ssid() {
  var app = getApp()
  wx.getNetworkType({
    success(res) {
      var networkType = res.networkType
      if (networkType == 'wifi') {
        wx.getConnectedWifi({
          success: function (res) {
            console.log('getConnectedwifi res', res)
            return res.wifi.SSID
          },

          fail: function (res) {
            return ''
          }
        })
      } else {
        return ''
      }

    },

    // 检测网络失败
    fail(res) {
      console.log('fail', res)
      app.globalData.network_allow_flag = false
      that.setData({
        wifi_flag: false,
        bssid_flag: false,
        showTopTips: true,
        errormsg: '非知网络连接类型'
      })
      setTimeout(function () {
        that.setData({
          showTopTips: false
        });
      }, 3000);
      return false
    }
  })
}

function applyNetwork(){
  var app = getApp();
  var host = app.globalData.host;
  var url = host + "baseinfo/get_roomlist/";
  console.log(url);
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_RoomList res.data', res.data)
      app.globalData.roomlist = res.data
      wx.setStorage({
        key: 'roomlist',
        data: res.data
      })
    }
  });  
}

function commonrequest(that,url, param,key){
  var app = getApp();
  var host = app.globalData.host;
  // var url = host + url;
  param.company=app.globalData.company,
  param.storecode = app.globalData.storecode,
  param.appcode = app.globalData.appcode,
  param.ecode = app.globalData.ecode
  console.log('commonrequest:',url,param);
  wx.showToast({
    title: '数据加载中...',
    icon: 'loading',
  });
  wx.request({
    method: 'GET',
    url: url,
    data: param,
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      that.setData({
        [key]:res.data
      })
      wx.hideLoading()     
      // return res.data
    },
    fail(res){
      console.log('fail res',res)
      wx.hideLoading()     
    },
    finished(res){
  
    }
  });    
}

/** 首页 grids：若后台未配置「在店客人」，则补充入口（与 DB 同结构：id/text/url/image） */
function mergeInstoreVipGridItem(grids) {
  var list = grids;
  if (list == null) {
    list = [];
  }
  if (typeof list === 'string') {
    try {
      list = JSON.parse(list);
    } catch (e) {
      list = [];
    }
  }
  if (!Array.isArray(list)) {
    list = [];
  }
  var hasInstore = list.some(function (g) {
    return g && g.url && String(g.url).indexOf('instore_vips') !== -1;
  });
  if (hasInstore) {
    return list;
  }
  list.unshift({
    id: 'instore_vips',
    text: '未结账客人',
    url: '/index/instore_vips/instore_vips',
    image: '/index/instore_vips_icon.png'
  });
  return list;
}

/** 会员详情 grids：若后台未配置「结账」，则补充入口 */
function mergeVipCheckoutGridItem(grids) {
  var list = grids;
  if (list == null) {
    list = [];
  }
  if (typeof list === 'string') {
    try {
      list = JSON.parse(list);
    } catch (e) {
      list = [];
    }
  }
  if (!Array.isArray(list)) {
    list = [];
  }
  var hasCheckout = list.some(function (g) {
    return g && g.url && String(g.url).indexOf('/vip/checkout/checkout') !== -1;
  });
  if (hasCheckout) {
    return list;
  }
  list.push({
    id: 'vip_checkout',
    text: '结账',
    url: '/vip/checkout/checkout',
    image: '../images/cart.png'
  });
  return list;
}

function getWechatFunction(that,option) {
  console.log('getWechatFunction option',option)
  var app = getApp();
  var host = app.globalData.host;
  var functionid = option.functionid
  var key= option.key
  var url = host + "wechat/get_wechatapp_function/";
  console.log(this.url);
  wx.request({
    method: 'GET',
    url: url,
    data: {
      user_uuid:app.globalData.user_uuid,
      appcode: app.globalData.appcode,
      wxusertype: app.globalData.wxusertype,
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      type:'100',
      ecode: app.globalData.ecode,
      functionid: functionid
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      console.log('get_wechatapp_function', res.data)
      var payload = res.data;
      if (functionid === 'index' && key === 'grids') {
        payload = mergeInstoreVipGridItem(payload);
      }
      if (functionid === 'vip' && key === 'grids') {
        payload = mergeVipCheckoutGridItem(payload);
      }
      that.setData({
        [key]: payload
      })
    }
  });
}

function get_SalonList(that) {
  console.log('get_SalonList ')
  var app = getApp();
  var host = app.globalData.host;
  var company = app.globalData.company;
  var url = host + "baseinfo/get_salonlist/";

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
    },
    // header: {
    //   'content-type': 'application/json' // 默认值
    // },
    success(res) {
      console.log('get_salonlist', res.data)
      app.globalData.salonlist= res.data
      wx.setStorage({
        key: 'salonlist',
        data: res.data
      })
    }
  });
}

function get_ViplevelList(that) {
  var app = getApp()
  // var that = this
  var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      seg: 'viplevel'
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_ViplevelList',res)
      app.globalData.viplevellist=res.data
    },
    fail: function (res) {
      console.log("get_ViplevelList failed")
    },
    complete: function (res) {
      console.log("get_ViplevelList finished")
    }
  })
}    

/** 开单未结账（有效挂单）客人列表 */
function getInstoreVipList(that, vsdateOpt) {
  var app = getApp();
  var url = app.globalData.host + 'adviser/get_instore_vips/';
  var vsdate = vsdateOpt;
  if (!vsdate) {
    vsdate = getToday().split('-').join('');
  }
  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      vsdate: vsdate
    },
    header: {
      'content-type': 'application/json'
    },
    success: function (res) {
      var list = [];
      if (res.statusCode === 200 && Array.isArray(res.data)) {
        list = res.data;
      }
      that.setData({
        instoreVipList: list,
        instoreVipLoaded: true
      });
    },
    fail: function () {
      that.setData({
        instoreVipList: [],
        instoreVipLoaded: true
      });
    }
  });
}
// request get 请求


// // request post 请求
// const postData = (url, param) => {
//   return new Promise((resolve, reject) => {
//     wx.request({
//       url: url,
//       method: 'POST',
//       data: param,
//       success (res) {
//         console.log(res)
//         resolve(res.data)
//       },
//       fail (err) {
//         console.log(err)
//         reject(err)
//       }
//     })
//   })
// }

// // loading加载提示
// function showLoading()  {
//   return new Promise((resolve, reject) => {
//     wx.showLoading({
//       title: '加载中...',
//       mask: true,
//       success (res) {
//         console.log('显示loading')
//         resolve(res)
//       },
//       fail (err) {
//         reject(err)
//       }
//     })
//   })
// }

// // 关闭loading
// function hideLoading() {
//   return new Promise((resolve) => {
//     wx.hideLoading()
//     console.log('隐藏loading')
//     resolve()
//   })
// }

module.exports = {
  formatTime: formatTime,
  getRandomArray: getRandomArray,
  getRandomArrayElement: getRandomArrayElement,
  getToday: getToday,
  getMonth: getMonth,
  getPreMonth:getPreMonth,
  getLastMonthLastDate:getLastMonthLastDate,
  getWeek: getWeek,
  dateDelta:dateDelta,
  datetostr: datetostr,
  strtodate: strtodate,
  uuidtostr: uuidtostr,
  strtouuid: strtouuid,
  showLoading: showLoading,
  hideLoading: hideLoading,
  // buttonClicked: buttonClicked,
  get_indexImageUrl: get_indexImageUrl,
  get_nextvcode: get_nextvcode,
  get_nextccode: get_nextccode,
  get_source: get_source,
  get_vipcasetype: get_vipcasetype,
  get_stypelist: get_stypelist,
  get_empllist:get_empllist,
  get_pmcodelist: get_pmcodelist,
  get_seccodelist: get_seccodelist,
  get_cardtypelist: get_cardtypelist,
  get_amountcardtypelist: get_amountcardtypelist,
  get_timescardtypelist: get_timescardtypelist,
  get_periodcardtypelist: get_periodcardtypelist,
  get_VipList: get_VipList,
  get_Vip10List: get_Vip10List,
  get_Vip20List: get_Vip20List,
  get_Vip30List: get_Vip30List,
  get_VipInList: get_VipInList,
  get_VipNotinList: get_VipNotinList,
  get_VipcntList: get_VipcntList,
  get_DailyStoreData:get_DailyStoreData,
  get_SrvList: get_SrvList,
  get_GoodsList: get_GoodsList,
  get_RoomList: get_RoomList,
  get_InstrumentList: get_InstrumentList,
  get_PsStatusList: get_PsStatusList,
  get_emplarch_bymonth: get_emplarch_bymonth,
  checkNetwork: checkNetwork,
  get_bssid: get_bssid,
  get_ssid: get_ssid,
  getWechatFunction: getWechatFunction,
  openToast: openToast,
  openLoading:  openLoading,
  commonrequest:commonrequest,
  replaceSpecialChar: replaceSpecialChar,
  get_SalonList:get_SalonList,
  get_ViplevelList:get_ViplevelList,
  getInstoreVipList: getInstoreVipList
  // getData,
  // postData,
  // showLoading,
  // hideLoading


}
