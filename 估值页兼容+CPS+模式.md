工单：https://xz.corpautohome.com/requirement/detail/185788?pageDes=估值页兼容 CPS 模式

## 一、需求背景：

估值页兼容 CPS 场景

## 二、需求目标：

业务支持

## 三、项目范围：

涉及的业务：二手车

涉及的平台：NQ，先落地 RN，然后滚动开发转 RNW

涉及入口：所有RN 估值页均修改，主要入口有：

| 入口 | 三级来源 |
| --- | --- |
| NQ-二手车首页糖豆-估值-AI查车专家 | 1981 |
| NQ-二手车首页-车牌号估值 | 2202 |
| NQ-二手车大全糖豆五个版-估值 | 2204 |
| NQ-个人中心-更多糖豆-免费估值 | 1932 |
| NQ-二手车频道-消息提醒-估值 | 2131 |
| NQ-二手车频道-搜索页-腰部估值1 | 2145 |
| NQ-首页搜索结果页-估值工具入口 | 1961 |

## 四、设计图：

260420-CPS-估值.zip

## 五、需求详情：

## 通用调整

### 功能描述
- 1、城市定位询问：
- 缓存场景进入页面时（从填写车辆信息进入不提醒），判断当前定位与车辆所在地是否一致（如拿不到定位则不判断），如不一致弹出弹层询问：“车辆所在地与当前定位不一致，是否切换到【当前城市区县（参数）】？”，点击切换，更新为当前城市，点击不切换，保持不变
- 此时弹层消失
- 如果触发条件，按设备控制 3 个自然日弹出一次
- 线上存在 30 天更新里程的弹层，优先级未先弹城市定位询问，后弹更新里程
- 点击切换，车辆所在地改为当前城市，否则不修改
- 2、使用其他手机号流程：
- 目前线上使用其他号码跳转到单独的页面，完成修改后还回到确认手机号弹层，需修改为直接往下一步走，如没勾选协议直接弹出协议确认，如完成直接过风控，如完成过验证码填写此时不再重复发验证码

### 埋点
- 地区询问弹层展示：
- usc_2sc_mcy_wygz_ydcsdcxw_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- 地区询问弹层点击：
- usc_2sc_mcy_wygz_ydcsdcxw_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid，pos：1 不切换，2 切换

## 分城市控制样式和线索

### 功能描述
- 1、使用同一 RN 估值页面，对不同城市进行区别化展示：
- 如右图，左侧为默认样式，右侧为 CPS 模式样式，识别到页面加载，或用户在页面内切换城市时，判断展示默认还是 CPS 样式，并进行刷新
- 2、CPS 模式根据城市判断：
- 常州，南通，南昌，嘉兴，湖州，绍兴
- 如用户提交的是命中CPS城市的线索，提交线索不区分普通和高质，均带tag= 476，订单结果页跳转CPS订单
- 如用户提交的城市非CPS城市，则不带tag，正常提交线索，跳转原电话线索RN订单页
- 3、按钮展示和吸底：
- 底部固定按钮改为和卖车页效果相同，首屏不吸底，在页面中下部展示，当滑出第一屏时，吸底

### 埋点
- 页面展示（线上埋点）：  show usc_2sc_mcy_wygz_202404xgzbggmkp
- 公共参数   isdealers： 0 普通 1 企微 2 cps

## 车况信息

### 功能描述
- 1、CPS 车况信息位置调整，展示在车辆下方：
- 车龄：[（当前年份 − 上牌年份）× 12 +（当前月份 − 上牌月份）] ÷ 12，四舍五入展示到小数点后一位
- 表现里程：默认取上一页带入，精确值小数点后一位
- 过户次数：默认 0 次
- 外观颜色：默认接口常规颜色
- 车况：默认良好
- 2、交互逻辑：
- 小屏展示不下时，车况档案和修改文案区域前后固定，中间车况信息支持横向滑动
- 点击修改支持弹出线上的弹层，进行修改车况和查看价格，弹层内修改交互和接口均保持线上，修改完信息后关闭弹层，车况和价格需带回到估值页
- 点击我要卖车，留资路径为手机号不外显场景

### 埋点
- 同非 CPS 页修改车况用一套

## CPS 服务弹层入口

### 功能描述
- 1、入口 1：
- 黑色横条，官方 icon 默认，文案由后端带入，本次展示文案：卖车送检测，定价更精准，拍卖价更高 >
- 整个横条均为点击区域，点击后弹出服务弹层
- 2、入口 2：
- 默认样式即可，文案：到底能卖多少钱？了解详情
- 下月下降百分比计算公式为：（下月当前车辆均值-当前车辆均值）
- 当前车辆均值
- 均值接口由后端计算
- 整个蓝色区块均为点击区域，点击后弹出服务弹层

### 埋点
- 弹层入口点击埋点：
- usc_2sc_mcy_wygz_cpsjsdcrkdj_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- pos：1 黑色横条，2 蓝色区块

## CPS 服务弹层

### 功能描述
- 1、静态展示信息：
- 标题：汽车之家官方帮拍卖，卖价真的高
- 步骤和服务：四步卖高价，享三重服务，具体文案和样式见右图
- 2、邀约留资：
- 在后续邀约留资功能详述
- 走手机号不外显流程
- 3、留资按钮展示呼吸动效
- “获取定位”改成“地图选址”
- 4、当前页面 posid = 3034

### 埋点
- 弹层展示埋点：
- usc_2sc_mcy_wygz_cpsfwjsdc_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- 弹层内点击埋点：
- usc_2sc_mcy_wygz_cpsfwjsdc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- pos如下图

## 卖点区域

### 功能描述
- 1、静态展示区域：
- 除【查看检测报告示例】外，其余均为静态展示即可
- 估值主文案：免费检测  帮定价
- 估值附文案：权威检测报告  一车一况定价
- 卖车主文案：全国报价  锁高价
- 卖车附文案：全国拍卖询高价  管家 24 小时陪伴
- 2、点击交互：
- 点击【查看检测报告示例】，弹出报告示例弹层，详情在报告示例区域详述

### 埋点
- 查看报告示例埋点：
- usc_2sc_mcy_wygz_gzbgsl_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid

## 邀约留资

### 功能描述
- 1、页面上邀约交互：（和卖车页保持一致）
- 1）地点：
- 点击输入框位置，光标聚焦支持输入文字，根据输入关键词联想地址信息，用户点击联想地址，填入相应地址信息，并根据经纬度反查城市区县，用于提交线索
- 提交线索时的城市区县使用预约地点对应的城市区县，如地点无法映射，则去页面展示的车辆所在地填充
- *地点输入联想框展示规则：
- 点击输入框：光标聚焦，如有联想内容，开始展示联想
- 用户未输入任何内容时，采用线上H5组件同样的默认联想
- 用户输入文字，优先开始检索是否有可联想地点，展示3条
- 当用户输入文字没有可联想地点时，展示提示语：“暂未找到该地点”，按钮“去选择城市地区”，点击按钮，展示选择【城市】【区县】弹窗，
- 兜底逻辑：如百度所查城市区县与C1城市区县库找不到对应关系，则使用页面展示的车辆所在地
- 点击右侧定位icon，展示当前选择定位弹窗，选择位置后返回页面填充，并拿到城市区县
- 2）期望上门时间：默认不填充，点击跳转检测时间弹窗，默认选中第一个今日-随时可以
- 2、页面上有手机号交互：
- 默认取当前登录手机号，支持修改，修改后验证码校验，与线上的营销弹层带手机号的修改交互一致，完成过修改手机号并接收验证码，在后续留资流程不需要校验手机号验证码，且修改过手机号在当前页面留资全局使用修改过的手机号
- 3、其他说明
- 页面上留资大按钮有呼吸动效
- “获取定位”文案改成“地图选址”
- 时间选择区域靠右增加小 icon 展示，整个条形区域均为点击区域
- 4、点击提交按钮校验路径：（ CPS 页面通用一套）
- 邀约地点、邀约时间、手机号、勾选协议、风控，如哪项缺失则弹层补充
- 全部校验项通过后提交 660
- 5、当前入口提交 posid=3035

### 埋点
- 页面上点击：usc_2sc_mcy_wygz_cpsgzylz_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid，
- pos如下图
- 地图弹层：
- 展现：usc_2sc_mcy_wygz_cpsgzydtdc_show
- ityid，cityname，pvareaid，sourceclassthree，seriesid，specid
- 点击：usc_2sc_mcy_wygz_cpsgzydtdc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid，pos 如下
- 时间选择弹层：
- 展现：usc_2sc_mcy_wygz_cpsgzysjxzdc_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid
- 点击：usc_2sc_mcy_wygz_cpsgzysjdc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid，pos：1 关闭，2 完成时间选择
- 手机号弹层（所有当前CPS 页的手机号弹层用这一套就行）：
- 展现：usc_2sc_mcy_wygz_cpsgzysjhdc_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid
- 点击：usc_2sc_mcy_wygz_cpsgzysjhdc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid，pos：
- 3.关闭
- 4.取消
- 5.取消
- 6.使用其他号码
- 协议弹层：
- 展现：usc_2sc_mcy_wygz_cpsgzyxydc_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid
- 点击：usc_2sc_mcy_wygz_cpsgzyxydc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid，specid，pos：
- 1.协议点击
- 2.协议详情

## 平台管家

### 功能描述
- 文案静态展示，点击直达按钮，跳转微信添加企微，与卖车页企微一致

### 埋点
- 点击添加企微：usc_2sc_mcy_wygz_tjqw_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid

## 检测报告示例

### 功能描述
- 1、弹层标题：
- 检测报告示例
- 2、展示信息：
- 均为 UI 给设计稿即可
- 3、页面交互：
- 弹层内支持上下滑动，所有内容均无法点击，静态展示
- 点击检测卖车支持留资，走页面通用校验路径
- 3、当前入口下单 posid = 3036

### 埋点
- 弹层展示埋点：
- usc_2sc_mcy_wygz_jcbgsldc_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- 弹层点击埋点：
- usc_2sc_mcy_wygz_jcbgsldc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- pos：1 卖车按钮，2协议点击，3  关闭弹层，4 其他任意位置点击

## 15 秒弹层

### 功能描述
- 1、主标题：
- 198 项专业检测报告免费送（和设计稿有区别）
- 2、亮点：
- 车况总结、权威报告、行情数据、报告解读
- 3、限时补贴：
- 卖车送价值 299 元官方检测报告，XX 人成功获取，人数10000 为基数，每日累加 100-1000 人随机数
- 4、手机号：
- 默认登录手机号，支持修改，与线上逻辑保持一致
- 5、留资：
- 点击大按钮支持留资
- 6、弹层弹出时机：
- 页面浏览至 15 秒时弹出，当识别到用户操作弹层，倒计时关闭消失，CPS 城市不展示原来的倒计时弹层，只展示这个新弹层

### 埋点
- 弹层展示埋点：
- usc_2sc_mcy_wygz_15mdc_show
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- 弹层内点击埋点：
- usc_2sc_mcy_wygz_15mdc_click
- cityid，cityname，pvareaid，sourceclassthree，seriesid
- pos：1 手机号，2 预约大按钮，3 协议，4 关闭弹层，5其他任意位置

## 二屏及以下

### 功能描述
- 1、隐藏报价入口
- 当识别到 CPS 城市时，隐藏价格展示入口
- 2、其他信息
- 均与线上保持一致，无需修改，简述模块为
- 一键查维保出险入口：
- 点击跳转付费查维保页面
- 看看大家卖多少，
- 点击我要卖车，支持提交线索
- 车抵贷：
- 点击跳转车抵贷页面
- 月在售价格趋势：
- 点击更多
- 换车攻略
- 3、弹层留资入口
- 样式可不做改动，点击走 CPS 提单流程


API

- 获取估值页兼容CPS服务入口https://zhishi.autohome.com.cn/home/teamplace/file?targetId=1E2iaIsvRkO
- 获取用户领取数量接口：https://zhishi.autohome.com.cn/home/teamplace/file?targetId=1E7QyOwCc0e

补充：

#### 1、现状修改手机号页已走验证码流程，如果回到估值页可不走风控，继续走提交订单

#### 2、现状估值页填写邀约地点时联想地会被键盘遮挡，需处理为不遮挡
