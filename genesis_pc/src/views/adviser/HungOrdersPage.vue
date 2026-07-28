<template>
  <div style="height:100%;display:flex;flex-direction:column">
    <h2 style="flex-shrink:0;margin:0 0 12px 0;font-size:18px;font-weight:600">开单管理</h2>

    <!-- 状态筛选标签 -->
    <el-card shadow="never" style="margin-bottom:12px;flex-shrink:0">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
        <span style="font-size:13px;color:#606266;white-space:nowrap">状态：</span>
        <el-radio-group v-model="filterStatus" size="small" @change="onStatusChange">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="10">开单</el-radio-button>
          <el-radio-button value="40">服务完成</el-radio-button>
          <el-radio-button value="50">可结账</el-radio-button>
          <el-radio-button value="60">挂账</el-radio-button>
          <el-radio-button value="70">已结账</el-radio-button>
          <el-radio-button value="__void__">已作废</el-radio-button>
        </el-radio-group>
        <el-date-picker v-if="filterStatus === '70' || filterStatus === '__void__'" v-model="dateRange" type="daterange"
          range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"
          size="small" style="width:240px" value-format="YYYYMMDD"
          @change="fetchData" />

        <el-button type="primary" size="small" @click="openCustomerCheckout">客户结账</el-button>
        <div style="flex:1" />

        <!-- 会员快捷筛选 -->
        <span style="font-size:13px;color:#606266;white-space:nowrap">会员：</span>
        <div class="vip-chips">
          <el-tag
            v-for="vip in vipList" :key="vip.vcode"
            :type="filterVip === vip.vcode ? 'primary' : 'info'"
            size="small"
            style="cursor:pointer;margin-right:4px"
            @click="toggleVipFilter(vip.vcode)"
          >
            {{ vip.vname }} ({{ vip.count }})
          </el-tag>
          <el-tag v-if="filterVip" type="danger" size="small" style="cursor:pointer" @click="filterVip = ''">
            清除筛选
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 挂单列表 -->
    <el-card shadow="never" class="hung-card" style="flex:1;min-height:0;display:flex;flex-direction:column">
      <div style="flex:5.5;min-height:0;overflow-y:auto" v-loading="loading">
      <div v-if="!hungList.length && !loading" style="padding:40px;text-align:center;color:#c0c4cc;font-size:14px">暂无开单管理</div>
      <div v-for="group in groupedByDate" :key="group.date" class="date-group">
        <div class="date-group-header">
          📅 <span style="font-weight:600">{{ formatDate(group.date) }}</span>
          <span class="date-count">{{ group.items.length }} 单</span>
        </div>
        <el-table :data="group.items" size="small" stripe
          @row-click="selectRow" :row-class-name="selectedRowClass">
          <el-table-column label="挂单号" width="170">
            <template #default="{ row }">{{ row.exptxserno }}</template>
          </el-table-column>
          <el-table-column label="会员" width="150">
            <template #default="{ row }">{{ row.vname || '--' }}<span style="color:#909399;font-size:11px;margin-left:4px">（{{ row.vcode || '' }}）</span></template>
          </el-table-column>
          <el-table-column label="日期" width="90">
            <template #default="{ row }">{{ row.vsdate ? row.vsdate.slice(0,8) : '--' }}</template>
          </el-table-column>
          <el-table-column label="时间" width="70">
            <template #default="{ row }">{{ row.vstime || '--' }}</template>
          </el-table-column>
          <el-table-column label="金额" width="105" align="right">
            <template #default="{ row }">¥{{ (row.totmount || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="项目数" width="60" align="center">
            <template #default="{ row }">{{ row.itemcount || 0 }}</template>
          </el-table-column>
          <el-table-column label="类型" width="55">
            <template #default="{ row }">{{ ttypeLabel(row.ttype) }}</template>
          </el-table-column>
          <el-table-column label="付款卡" width="120">
            <template #default="{ row }">{{ row.paycode || '--' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="statusType(row.psstatus)" size="small" effect="dark" style="cursor:pointer" @click="filterStatus = row.psstatus; fetchData()">
                {{ statusLabel(row.psstatus) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.psstatus === '70'" text type="primary" size="small" @click.stop="showReceiptForRow(row)">消费单</el-button>
              <el-button v-if="row.psstatus !== '70' && row.valiflag !== 'N'" text type="warning" size="small" @click.stop="checkout(row)">结账</el-button>
              <el-button v-if="row.psstatus !== '70' && row.valiflag !== 'N'" text type="danger" size="small" @click.stop="voidHung(row)">作废</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      </div>
      <el-card shadow="never" class="hung-detail-card" style="flex:4.5;min-height:0;display:flex;flex-direction:column;margin-top:12px">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>明细<span v-if="selectedOrder"> - {{ selectedOrder.exptxserno }}</span></span>
            <div style="display:flex;gap:4px">
              <el-button v-if="selectedOrder?.psstatus === '70'" text type="primary" size="small" @click="showReceiptForRow(selectedOrder)">消费单</el-button>
              <el-button text type="info" size="small" @click="selectedOrder = null; detailItems = []">关闭</el-button>
            </div>
          </div>
        </template>
        <el-table :data="detailItems" size="small" stripe v-loading="detailLoading">
          <el-table-column label="项目" min-width="160">
            <template #default="{ row }">{{ row.itemname || '--' }}<span style="color:#909399;font-size:11px;margin-left:4px">（{{ row.srvcode || '' }}）</span></template>
          </el-table-column>
          <el-table-column label="类型" width="50">
            <template #default="{ row }">{{ row.ttypename }}</template>
          </el-table-column>
          <el-table-column label="属性" width="55">
            <template #default="{ row }">{{ row.stypename || row.stype || '--' }}</template>
          </el-table-column>
          <el-table-column label="单价" width="100" align="right">
            <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="数量" width="55" align="right">
            <template #default="{ row }">{{ row.qty }}</template>
          </el-table-column>
          <el-table-column label="金额" width="110" align="right">
            <template #default="{ row }">¥{{ row.mount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="员工" min-width="280">
            <template #default="{ row }">
              <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap">
                <el-select v-model="row.pmcode" size="small" placeholder="开单" @change="saveEmp(row)" style="width:80px">
                  <el-option label="--" value="" />
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
                <el-select v-model="row.asscode1" size="small" placeholder="美1" @change="saveEmp(row)" style="width:80px">
                  <el-option label="--" value="" />
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
                <el-select v-model="row.asscode2" size="small" placeholder="美2" @change="saveEmp(row)" style="width:80px">
                  <el-option label="--" value="" />
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!detailItems.length && !detailLoading" :description="selectedOrder ? '无明细数据' : '请从上方选择一条挂单'" />
      </el-card>

      <div v-if="stats.cardCount > 0" class="stats-bar" style="flex-shrink:0">
        <span>共 <b>{{ stats.cardCount }}</b> 单，会员 <b>{{ stats.vipCount }}</b> 人，总计 <b>¥{{ stats.totalAmount.toFixed(2) }}</b></span>
      </div>
      <el-empty v-if="!hungList.length && !loading" description="暂无开单管理" style="flex-shrink:0" />
    </el-card>
    <!-- 客户结账弹窗 -->
    <el-dialog v-model="custCheckoutVisible" title="客户结账" width="720px" top="3vh" :close-on-click-modal="false">
      <template v-if="!custCheckoutVipSelected">
        <div style="margin-bottom:10px">
          <div style="font-size:13px;font-weight:600;color:#606266;margin-bottom:6px">请选择要结账的客户：</div>
          <el-input v-model="custCheckoutSearchKeyword" placeholder="输入客户姓名/手机号/会员号" clearable size="default" @keyup.enter="searchCheckoutVip" @clear="custCheckoutSearchResults=[]">
            <template #append><el-button @click="searchCheckoutVip">搜索</el-button></template>
          </el-input>
        </div>
        <div v-if="custCheckoutSearchResults.length" style="border:1px solid #ebeef5;border-radius:6px;max-height:300px;overflow-y:auto">
          <div v-for="v in custCheckoutSearchResults" :key="v.uuid" style="display:flex;align-items:center;padding:8px 10px;border-bottom:1px solid #f5f5f5;cursor:pointer" @click="selectCheckoutVip(v)">
            <span style="font-size:14px;font-weight:500">{{ v.vname }}</span>
            <span style="font-size:12px;color:#909399;margin-left:6px">{{ v.vcode }}</span>
            <span style="font-size:11px;color:#c0c4cc;margin-left:6px">{{ v.mtcode }}</span>
          </div>
        </div>
        <el-empty v-if="!custCheckoutLoading && custCheckoutSearchKeyword && !custCheckoutSearchResults.length" description="未找到匹配的客户" :image-size="50" />
      </template>
      <template v-else>
        <div v-if="custCheckoutLoading" style="text-align:center;padding:40px;color:#909399">加载中...</div>
        <template v-else-if="custCheckoutData">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:linear-gradient(135deg,#f0f9ff,#e6f7ff);border-radius:8px;margin-bottom:10px">
          <div>
            <span style="font-size:15px;font-weight:600">👤 {{ custCheckoutData.vname }}</span>
            <span style="font-size:12px;color:#909399;margin-left:6px">({{ custCheckoutData.vcode }})</span>
            <el-button text type="info" size="small" style="margin-left:6px;font-size:11px" @click="custCheckoutVipSelected = false; custCheckoutSearchKeyword=''; custCheckoutSearchResults=[]">切换客户</el-button>
          </div>
          <div style="text-align:right">
            <div style="font-size:12px;color:#606266">{{ custCheckoutData.orders }} 单 / {{ custCheckoutData.items }} 项</div>
            <div style="font-size:16px;font-weight:700;color:#e6a23c">总计 ¥{{ custCheckoutData.total.toFixed(2) }}</div>
          </div>
        </div>
        <div style="max-height:48vh;overflow-y:auto">
          <!-- 按挂单分组展示 -->
          <div v-for="grp in custGroupedOrders" :key="grp.order_no" style="border:1px solid #ebeef5;border-radius:6px;margin-bottom:6px;overflow:hidden">
            <div style="display:flex;align-items:center;padding:5px 10px;background:#f5f7fa;font-size:12px;font-weight:600;color:#606266;border-bottom:1px solid #ebeef5">
              <span style="font-family:monospace">{{ grp.order_no }}</span>
              <span style="margin-left:auto">¥{{ grp.total.toFixed(2) }}</span>
            </div>
            <div style="display:flex;align-items:center;padding:3px 10px;background:#fafafa;font-size:11px;color:#909399;border-bottom:1px solid #f0f0f0">
              <span style="width:16px"></span>
              <span style="flex:1">交易类型 - 项目</span>
              <span style="width:24px;text-align:center">量</span>
              <span style="width:55px;text-align:right">单价</span>
              <span style="width:55px;text-align:right">金额</span>
              <span style="width:90px;text-align:center">处理方式</span>
              <span style="width:80px;text-align:center">员工</span>
            </div>
            <div v-for="item in grp.items" :key="item.name + item.mount" style="display:flex;align-items:center;padding:4px 10px;border-bottom:1px solid #f5f5f5;font-size:12px">
              <span :style="{color: item._cat === 'pending' ? '#e6a23c' : '#67c23a', width:16, flexShrink:0}">{{ item._cat === 'pending' ? '⚠' : '✅' }}</span>
              <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ item.name }}</span>
              <span style="width:24px;text-align:center;color:#606266">×{{ Number(item.qty).toFixed(0) }}</span>
              <span style="width:55px;text-align:right">¥{{ Number(item.price).toFixed(2) }}</span>
              <span style="width:55px;text-align:right;font-weight:500">¥{{ Number(item.mount).toFixed(2) }}</span>
              <span style="width:90px;text-align:center;font-size:11px">
                <el-tag size="small" :type="item._cat === 'pending' ? 'warning' : item._cat === 'gift' ? 'info' : 'success'" effect="plain" style="font-size:10px">
                  {{ item._cat === 'times' ? '扣次 ' + (item.times_qty || 1) : item._cat === 'auto' ? '卡付' : item._cat === 'gift' ? '赠送' : '待付' }}
                </el-tag>
              </span>
              <span style="width:80px;text-align:center;font-size:11px;color:#909399;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ empNamesFromCodes(item.pmcode, item.asscode1, item.asscode2) }}</span>
            </div>
          </div>
          <!-- 结算汇总 -->
          <div style="border:1px solid #ebeef5;border-radius:6px;padding:8px;margin-bottom:6px">
            <div style="font-size:12px;font-weight:600;color:#606266;margin-bottom:4px">📊 结算汇总</div>
            <div v-for="ac in custCheckoutData.summary.auto_cards" :key="ac.ccode" style="display:flex;align-items:center;font-size:12px;padding:3px 0">
              <span>✅ 💳 {{ ac.ccode }}</span><span style="color:#909399;margin-left:4px;font-size:11px">余额 ¥{{ ac.balance.toFixed(0) }}</span>
              <span style="margin-left:auto;font-weight:600;color:#67c23a">¥{{ ac.deduct_amount.toFixed(2) }}</span>
            </div>
            <div v-for="tc in custCheckoutData.summary.times_cards" :key="tc.ccode" style="display:flex;align-items:center;font-size:12px;padding:3px 0">
              <span>✅ 💳 {{ tc.ccode }}</span><span style="color:#909399;margin-left:4px;font-size:11px">余 {{ tc.leftqty }} 次</span>
              <span style="margin-left:auto;font-weight:600;color:#e6a23c">{{ tc.deduct_qty }} 次</span>
            </div>
            <div v-if="custCheckoutData.summary.gift.total > 0" style="display:flex;align-items:center;font-size:12px;padding:3px 0">
              <span>✅ 🎁 赠送</span>
              <span style="margin-left:auto;font-weight:600;color:#909399">-¥{{ custCheckoutData.summary.gift.total.toFixed(2) }}</span>
            </div>
            <div style="border-top:1px dashed #dcdfe6;margin:4px 0 2px"></div>
            <div style="display:flex;align-items:center;font-size:13px;font-weight:600;padding:3px 0">
              <span>⚠ 待付金额</span>
              <span style="margin-left:auto;color:#e6a23c">¥{{ custCheckoutData.summary.pending.total.toFixed(2) }}</span>
            </div>
          </div>
          <!-- 待付付款分配 -->
          <div v-if="custCheckoutData.summary.pending.total !== undefined" style="border:2px solid #e6a23c;border-radius:6px;padding:8px;margin-bottom:6px">
            <div style="font-size:12px;font-weight:600;color:#e6a23c;margin-bottom:6px">💳 付款分配（金额 ¥{{ custCheckoutData.summary.pending.total.toFixed(2) }}）</div>
            <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:4px">
              <div v-for="(pm, pi) in custCheckoutPayments" :key="pi" style="display:inline-flex;align-items:center;gap:2px;padding:2px 4px;background:#fff;border:1px solid #ebeef5;border-radius:4px;font-size:12px">
                <el-select v-model="pm.pcode" size="small" style="width:130px" filterable @change="custOnPmChange(pi)">
                  <el-option v-for="opt in allPaymodeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
                <el-input-number v-model="pm.amount" :min="0" :max="Math.abs(custCheckoutData.summary.pending.total)" size="small" :controls="false" :precision="2" style="width:110px" @change="custOnAmountChange" />
                <span style="font-size:10px;color:#909399">元</span>
                <el-button v-if="custCheckoutPayments.length > 1" text type="danger" size="small" style="padding:0" @click="custRemovePayment(pi)">✕</el-button>
              </div>
              <el-button size="small" text type="primary" @click="custAddPayment" style="font-size:11px;padding:0 4px">+ 添加</el-button>
            </div>
            <div style="text-align:right;font-size:12px">
              已分配: ¥{{ custPaidTotal.toFixed(2) }}
              <b :style="{color:custRemaining <= 0.01 ? '#67c23a' : '#f56c6c',marginLeft:6}">
                {{ custRemaining <= 0.01 ? '✅ 已平衡' : `剩余 ¥${custRemaining.toFixed(2)}` }}
              </b>
            </div>
          </div>
          <div v-else-if="custCheckoutData.summary.pending.total < 0" style="padding:8px;text-align:center;background:#f0f9eb;border-radius:6px;color:#67c23a;font-size:13px">✅ 所有项目已自动结算，无需额外付款</div>
        </div>
        <!-- 收银员 -->
        <div style="margin-top:8px;display:flex;align-items:center;gap:8px;padding:8px 12px;background:#fafafa;border-radius:6px">
          <span style="font-size:13px;font-weight:500;white-space:nowrap">🔑 收银员：</span>
          <span style="font-size:14px;color:#303133">👤 {{ checkoutCashierName }}（{{ checkoutCashier }}）</span>
          <el-button text type="primary" size="small" @click="showCashierPicker = true">切换</el-button>
          <span style="font-size:11px;color:#c0c4cc;margin-left:4px">开单与结账人员可以是不同的人</span>
        </div>
      </template>
      </template>
      <template #footer>
        <el-button size="default" @click="custCheckoutVisible = false">取消</el-button>
        <el-button size="default" type="primary" :loading="checkoutSubmitting"
          :disabled="custCheckoutData?.summary?.pending?.total > 0.01 && custRemaining > 0.01 || !checkoutCashier"
          @click="confirmCustomerCheckout">确认结账</el-button>
      </template>
    </el-dialog>
    
    <!-- 结账确认弹窗 -->
    <el-dialog v-model="checkoutDialogVisible" title="结账确认" width="700px" :close-on-click-modal="false" top="5vh">
      <div v-if="checkoutLoading" style="text-align:center;padding:40px;color:#909399;font-size:14px">加载中...</div>
      <template v-else>
        <div v-if="!checkoutOrders.length" style="text-align:center;padding:40px;color:#c0c4cc;font-size:14px">该会员暂无待结账的挂单</div>
        <template v-else>
          <!-- 会员信息头 -->
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:linear-gradient(135deg,#f0f9ff,#e6f7ff);border-radius:8px;margin-bottom:12px">
            <div>
              <div style="font-size:15px;font-weight:600;color:#303133">👤 {{ checkoutVipName }}</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:13px;color:#606266"><b style="color:#e6a23c;font-size:18px">{{ checkoutSelectedCount }}</b><span style="font-size:13px;color:#c0c4cc">/{{ checkoutOrders.length }}</span> 单</div>
              <div style="font-size:15px;font-weight:700;color:#e6a23c">合计 ¥{{ checkoutTotal.toFixed(2) }}</div>
            </div>
          </div>

          <!-- 全选 + 表格表头 -->
          <div style="margin-bottom:6px;display:flex;align-items:center;gap:8px;padding:0 4px">
            <el-checkbox v-model="checkoutSelectAll" @change="toggleAllCheckout" :indeterminate="checkoutIndeterminate" style="font-size:13px">全选</el-checkbox>
            <span style="font-size:12px;color:#909399">共 {{ checkoutOrders.length }} 单</span>
          </div>

          <!-- 挂单列表 -->
          <div style="border:1px solid #ebeef5;border-radius:6px;overflow:hidden">
            <!-- 表头 -->
            <div style="display:flex;align-items:center;padding:6px 10px;background:#fafafa;font-size:12px;font-weight:600;color:#606266;border-bottom:1px solid #ebeef5">
              <span style="width:30px;flex-shrink:0"></span>
              <span style="flex:1">挂单内容</span>
              <span style="width:100px;text-align:right">金额</span>
              <span style="width:110px;text-align:center">付款方式</span>
            </div>
            <!-- 行 -->
            <template v-for="o in checkoutOrders" :key="o.uuid">
            <div :style="{
              display:'flex', alignItems:'center', padding:'8px 10px',
              borderBottom: o.item_details?.length ? 'none' : '1px solid #f5f5f5',
              background: checkoutSelections[o.uuid] ? '#ecf5ff' : '#fff',
              fontSize: '13px'
            }">
              <span style="width:30px;flex-shrink:0"><el-checkbox v-model="checkoutSelections[o.uuid]" /></span>
              <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:center;gap:6px">
                  <span style="font-family:monospace;font-size:12px;color:#303133">{{ o.exptxserno }}</span>
                  <span style="font-size:11px;color:#909399">{{ (o.vsdate||'').slice(0,4) }}/{{ (o.vsdate||'').slice(4,6) }}/{{ (o.vsdate||'').slice(6,8) }}</span>
                </div>
              </div>
              <span style="width:100px;text-align:right;font-weight:600;color:#e6a23c">¥{{ (o.totmount||0).toFixed(2) }}</span>
              <span style="width:110px;text-align:center;font-size:11px;color:#909399">付款 {{ checkoutSplits[o.uuid]?.length || 0 }} 项</span>
            </div>
            <div style="padding:4px 10px 4px 46px;background:#f8f8f8;border-bottom:1px solid #f0f0f0;font-size:12px">
              <div style="display:flex;align-items:center;gap:4px;flex-wrap:wrap">
                <span style="font-weight:600;color:#606266;font-size:12px;margin-right:2px">付款方式：</span>
                <template v-for="(sp, si) in checkoutSplits[o.uuid]" :key="si">
                  <div style="display:inline-flex;align-items:center;gap:2px;padding:2px 4px;background:#fff;border:1px solid #ebeef5;border-radius:4px;margin:1px">
                    <el-select v-model="sp.pcode" size="small" style="width:130px" @change="onSplitMethodChange(o, si)" filterable>
                      <el-option v-for="pm in availableSplitsForSplit(o, sp)" :key="pm.value" :label="pm.label" :value="pm.value" />
                    </el-select>
                    <el-input-number v-model="sp.amount" :min="0" :max="sp.cardBalance || (o.totmount||0)" size="small" :controls="false" :precision="2" style="width:110px" @change="onSplitAmountChange(o, si)" :step="0.01" />
                    <span style="font-size:10px;color:#909399">元</span>
                    <el-button v-if="!sp._default" text type="danger" size="small" :disabled="checkoutSplits[o.uuid].length <= 1" @click="removeSplit(o, si)" style="padding:0">✕</el-button>
                    <span v-if="sp._default" style="font-size:10px;color:#c0c4cc">(默认)</span>
                  </div>
                </template>
                <el-button size="small" text type="primary" @click="addSplitMethod(o)" style="font-size:11px;padding:0 4px">+ 添加</el-button>
                <span style="margin-left:auto;font-size:11px;color:#909399">
                  剩余: <b :style="{color:splitRemaining(o) <= 0.01 ? '#67c23a' : '#f56c6c'}">¥{{ splitRemaining(o).toFixed(2) }}</b>
                </span>
              </div>
            </div>
            <div v-if="o.item_details?.length" style="padding:4px 10px 4px 46px;background:#f8f8f8;border-bottom:1px solid #f0f0f0;font-size:12px">
              <div style="display:flex;gap:6px;padding:2px 0;color:#909399;font-weight:500;border-bottom:1px solid #ebeef5">
                <span style="flex:1">交易类型 - 项目</span>
                <span style="width:38px;text-align:center">数量</span>
                <span style="width:60px;text-align:right">单价</span><span style="width:60px;text-align:right">金额</span>
                <span style="width:44px;text-align:center">属性</span>
                <span style="width:95px;text-align:center">员工</span>
              </div>
              <div v-for="d in o.item_details" :key="d.name" style="display:flex;gap:6px;align-items:center;padding:3px 0;color:#606266;border-bottom:1px solid #f5f5f5">
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ (d.ttypename ? d.ttypename + '-' : '') + d.name + (['售卡','充值'].includes(d.ttypename) && d.ccode ? '（' + d.ccode.split('-').pop() + '）' : '') }}</span>
                <span style="width:38px;text-align:center;color:#606266">×{{ Number(d.qty).toFixed(0) }}</span>
                <span style="width:60px;text-align:right">¥{{ Number(d.price).toFixed(2) }}</span>
                <span style="width:60px;text-align:right;font-weight:500;color:#e6a23c">¥{{ Number(d.subtotal).toFixed(2) }}</span>
                <span style="width:44px;text-align:center"><el-tag size="small" effect="plain" :type="d.stypename === '赠送' ? 'warning' : undefined">{{ d.stypename }}</el-tag></span>
                <span style="width:95px;text-align:center;font-size:11px;color:#909399;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ empNamesFromCodes(d.pmcode, d.asscode1, d.asscode2) }}</span>
              </div>
            </div>
            </template>
          </div>

          <!-- 付款汇总 -->
          <div v-if="Object.keys(checkoutPaymentSummary).length > 0" style="border:1px solid #ebeef5;border-radius:6px;padding:8px;margin:10px 0">
            <div style="font-size:12px;font-weight:600;color:#606266;margin-bottom:4px">💰 付款汇总</div>
            <div v-for="(total, pcode) in checkoutPaymentSummary" :key="pcode" style="display:flex;justify-content:space-between;font-size:13px;padding:3px 0">
              <span>{{ findPaymodeName(pcode) }}</span>
              <span style="font-weight:600">¥{{ total.toFixed(2) }}</span>
            </div>
            <div style="border-top:1px dashed #dcdfe6;margin:4px 0 2px"></div>
            <div style="display:flex;justify-content:space-between;font-size:14px;font-weight:700;padding:3px 0;color:#303133">
              <span>合计</span>
              <span style="color:#e6a23c">¥{{ checkoutTotal.toFixed(2) }}</span>
            </div>
          </div>

          <div style="margin-top:14px;display:flex;align-items:center;gap:8px;padding:10px 12px;background:#fafafa;border-radius:6px">
            <span style="font-size:13px;font-weight:500;color:#606266;white-space:nowrap">🔑 收银员：</span>
            <span style="font-size:14px;color:#303133">👤 {{ checkoutCashierName }}（{{ checkoutCashier }}）</span>
            <el-button text type="primary" size="small" @click="showCashierPicker = true">切换</el-button>
            <span style="font-size:11px;color:#c0c4cc;margin-left:4px">开单与结账人员可以是不同的人</span>
          </div>
        </template>
      </template>
      <template #footer>
        <el-button size="default" @click="checkoutDialogVisible = false">取消</el-button>
        <el-button size="default" type="primary" :loading="checkoutSubmitting"
          :disabled="checkoutSelectedCount === 0 || !checkoutCashier"
          @click="confirmCheckout">确认结账（{{ checkoutSelectedCount }} 单）</el-button>
      </template>
    </el-dialog>

    <!-- 切换收银员弹窗 -->
    <el-dialog v-model="showCashierPicker" title="选择收银员" width="400px" :close-on-click-modal="false">
      <div style="margin-bottom:10px">
        <el-input v-model="cashierSearchKeyword" placeholder="输入工号或姓名搜索" clearable @keyup.enter="searchCashierUser" @clear="cashierSearchResults=[]">
          <template #append><el-button @click="searchCashierUser" :loading="cashierSearching">搜索</el-button></template>
        </el-input>
      </div>
      <div v-if="cashierSearchResults.length" style="border:1px solid #ebeef5;border-radius:6px;max-height:300px;overflow-y:auto">
        <div v-for="u in cashierSearchResults" :key="u.uuid"
          style="display:flex;align-items:center;padding:8px 10px;border-bottom:1px solid #f5f5f5;cursor:pointer;border-radius:4px"
          :style="{background: checkoutCashier === u.sys_userid ? '#ecf5ff' : 'transparent'}"
          @click="selectCashier(u)">
          <span style="font-size:14px;font-weight:500">{{ u.sys_fullname || u.sys_userid }}</span>
          <span style="font-size:12px;color:#909399;margin-left:6px">{{ u.sys_userid }}</span>
          <span v-if="u.storelist" style="font-size:11px;color:#c0c4cc;margin-left:8px">{{ u.storelist }}</span>
          <el-tag v-if="checkoutCashier === u.sys_userid" size="small" type="success" style="margin-left:auto">当前</el-tag>
        </div>
      </div>
      <el-empty v-if="!cashierSearching && cashierSearchKeyword && !cashierSearchResults.length" description="未找到匹配的用户" :image-size="50" />
      <template #footer>
        <el-button size="default" @click="showCashierPicker = false">取消</el-button>
      </template>
    </el-dialog>
    
    <!-- 消费单弹窗 -->
    <el-dialog v-model="receiptDialogVisible" title="消费单" width="580px" top="3vh" :close-on-click-modal="false">
      <template v-if="receiptData">
        <div id="receipt-content" style="padding:8px 0">
          <h2 style="text-align:center;margin:0 0 16px;font-size:17px;color:#303133;font-weight:600">消 费 单</h2>
          <div style="display:flex;justify-content:space-between;font-size:13px;color:#606266;margin-bottom:10px;border-bottom:1px solid #ebeef5;padding-bottom:8px">
            <span>客户：<b>{{ receiptData.vipName }}</b>（{{ receiptData.vipCode }}）</span>
            <span>日期：{{ receiptData.date }}</span>
          </div>
          <div v-for="(o, oi) in receiptData.orders" :key="oi" style="margin-bottom:8px;border:1px solid #ebeef5;border-radius:6px;overflow:hidden">
            <div style="display:flex;align-items:center;padding:6px 10px;background:#f5f7fa;font-size:12px;font-weight:600;color:#606266;border-bottom:1px solid #ebeef5">
              <span>第 {{ oi + 1 }} 单</span>
              <span style="margin-left:auto;font-size:10px;font-family:monospace;color:#c0c4cc">{{ o.serno }}</span>
            </div>
            <div style="display:flex;align-items:center;padding:4px 10px;background:#fafafa;font-size:11px;color:#909399;border-bottom:1px solid #f0f0f0">
              <span style="width:30px;text-align:center">类别</span>
              <span style="flex:3">项目</span>
              <span style="width:38px;text-align:center">数量</span>
              <span style="width:70px;text-align:right">单价</span>
              <span style="width:70px;text-align:right">金额</span>
              <span style="width:38px;text-align:center">属性</span>
              <span style="width:80px;text-align:center">员工</span>
            </div>
            <template v-for="grp in groupedItems(o.items)" :key="grp.type">
              <div v-for="(item, ii) in grp.items" :key="ii" style="display:flex;align-items:center;padding:5px 10px;border-bottom:1px solid #f5f5f5;font-size:13px">
                <span style="width:30px;text-align:center;font-size:11px;color:#909399">{{ ii === 0 ? grp.type : '' }}</span>
                <span style="flex:3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ item.name }}</span>
                <span style="width:38px;text-align:center;color:#606266">×{{ Number(item.qty).toFixed(0) }}</span>
                <span style="width:70px;text-align:right">¥{{ Number(item.price).toFixed(2) }}</span>
                <span style="width:70px;text-align:right;font-weight:500">¥{{ Number(item.amount).toFixed(2) }}</span>
                <span style="width:38px;text-align:center"><el-tag size="small" effect="plain" :type="item.stype === '赠送' ? 'warning' : undefined" style="font-size:10px">{{ item.stypeabbr || item.stype }}</el-tag></span>
                <span style="width:80px;text-align:center;font-size:11px;color:#909399;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ item.empName }}</span>
              </div>
              <div style="display:flex;justify-content:flex-end;padding:3px 10px;gap:10px;font-size:12px;color:#303133;font-weight:500;border-bottom:1px dashed #e0e0e0">
                <span>{{ grp.type }}小计</span>
                <span style="color:#e6a23c">¥{{ grp.subtotal.toFixed(2) }}</span>
              </div>
            </template>
          </div>
          <div style="border:1px solid #ebeef5;border-radius:6px;padding:8px;margin-bottom:8px">
            <div style="font-size:12px;font-weight:600;color:#606266;margin-bottom:4px">💳 付款方式</div>
            <div v-for="(p, pi) in receiptData.payments" :key="pi" style="display:flex;justify-content:space-between;font-size:13px;padding:3px 0">
              <span>{{ p.method }}</span>
              <span style="font-weight:500">¥{{ Number(p.amount).toFixed(2) }}</span>
            </div>
            <div v-if="receiptData.cards?.length" style="border-top:1px dashed #ebeef5;margin-top:6px;padding-top:6px">
              <div style="font-size:12px;font-weight:600;color:#606266;margin-bottom:4px">💳 卡余额</div>
              <div v-for="(c, ci) in receiptData.cards" :key="ci" style="display:flex;gap:6px;font-size:12px;padding:2px 0">
                <span style="flex:1">{{ c.comptype === 'times' ? '📋' : '💳' }} {{ c.cardname || c.ccode }}</span>
                <div style="text-align:right">
                  <template v-if="c.comptype === 'times'">
                    <div v-if="c.added_qty && Number(c.added_qty) > 0" style="font-weight:500;color:#409eff">充值 {{ Number(c.added_qty || 0).toFixed(0) }} 次</div>
                    <div style="font-weight:500;color:#e6a23c">消费 {{ Number(c.consumed_qty || 0).toFixed(0) }} 次</div>
                  </template>
                  <template v-else>
                    <div v-if="c.added_amount && Number(c.added_amount) > 0" style="font-weight:500;color:#409eff">充值 ¥{{ Number(c.added_amount || 0).toFixed(2) }}</div>
                    <div style="font-weight:500;color:#e6a23c">消费 ¥{{ Number(c.consumed_amount || 0).toFixed(2) }}</div>
                  </template>
                  <div style="font-weight:500;color:#67c23a">{{ c.comptype === 'times' ? '剩余 ' + Number(c.leftqty).toFixed(0) + ' 次' : '剩余 ¥' + Number(c.leftmoney).toFixed(2) }}</div>
                </div>
              </div>
            </div>
            <div style="border-top:2px solid #303133;margin-top:6px;padding-top:6px;display:flex;justify-content:space-between;font-size:15px;font-weight:700">
              <span>合计</span>
              <span style="color:#e6a23c">¥{{ Number(receiptData.total).toFixed(2) }}</span>
            </div>
          </div>
          <div style="text-align:center;font-size:11px;color:#c0c4cc;margin-top:4px">
            收银员：{{ receiptData.cashierName }}（{{ receiptData.cashierCode }}）
          </div>
        </div>
      </template>
      <template #footer>
        <el-button size="default" @click="receiptDialogVisible = false">关闭</el-button>
        <el-button size="default" @click="copyReceiptText">复制文本</el-button>
        <el-button size="default" type="primary" @click="printReceipt">🖨 打印</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store/app'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()
const hdsysuserid = appStore.user?.username || ''
const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''
const dateRange = ref<string[]>([])

const fullData = ref<any[]>([])
const selectedOrder = ref<any>(null)
const detailItems = ref<any[]>([])
const employees = ref<{ecode: string; ename: string}[]>([])
const detailLoading = ref(false)

const hungList = computed(() => {
  if (!filterVip.value) return fullData.value
  return fullData.value.filter((h: any) => h.vcode === filterVip.value)
})

function formatDate(s: string): string {
  if (!s || s.length < 8) return s || '--'
  return s.slice(0,4) + '-' + s.slice(4,6) + '-' + s.slice(6,8)
}

const groupedByDate = computed(() => {
  const map = new Map<string, any[]>()
  for (const h of hungList.value) {
    const d = (h.vsdate || '').slice(0, 8) || '未知'
    if (!map.has(d)) map.set(d, [])
    map.get(d)!.push(h)
  }
  return Array.from(map.entries())
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, items]) => ({ date, items }))
})

const loading = ref(false)
const filterStatus = ref('')
const filterVip = ref('')

const PSSTATUS_MAP: Record<string, { label: string; type: string }> = {
  '10': { label: '开单', type: 'info' },
  '20': { label: '到店', type: '' },
  '30': { label: '配料', type: '' },
  '40': { label: '服务完成', type: 'success' },
  '50': { label: '可结账', type: 'warning' },
  '60': { label: '挂账', type: 'warning' },
  '70': { label: '已结账', type: 'success' },
}

function statusLabel(s: string): string { return PSSTATUS_MAP[s]?.label || s || '--' }
function statusType(s: string): string { return PSSTATUS_MAP[s]?.type || 'info' }
const checkoutDialogVisible = ref(false)
const checkoutOrders = ref<any[]>([])
const checkoutSelections = ref<Record<string, boolean>>({})
const checkoutSelectAll = ref(false)
const checkoutLoading = ref(false)
const checkoutSubmitting = ref(false)
const checkoutCashier = ref('')
const checkoutCashierName = ref('')
const showCashierPicker = ref(false)
const cashierSearchKeyword = ref('')
const cashierSearchResults = ref<any[]>([])
const cashierSearching = ref(false)
const receiptDialogVisible = ref(false)
const receiptData = ref<any>(null)

const cashierPickerLoading = ref(false)
const custCheckoutVisible = ref(false)
const custCheckoutData = ref<any>(null)
const custCheckoutLoading = ref(false)
const custCheckoutVipUuid = ref('')
const custCheckoutPayments = ref<{pcode:string;amount:number}[]>([])
const custCheckoutSearchKeyword = ref('')
const custCheckoutSearchResults = ref<any[]>([])
const custCheckoutVipSelected = ref(false)

async function searchCheckoutVip() {
  if (!custCheckoutSearchKeyword.value) { custCheckoutSearchResults.value = []; return }
  try {
    const res = await request.get('/adviser/search_vip/', { params: { company, keyword: custCheckoutSearchKeyword.value } })
    custCheckoutSearchResults.value = Array.isArray(res.data) ? res.data : []
  } catch { custCheckoutSearchResults.value = [] }
}

async function selectCheckoutVip(vip: any) {
  custCheckoutSearchKeyword.value = vip.vname + ' ' + (vip.vcode || '')
  custCheckoutSearchResults.value = []
  custCheckoutVipUuid.value = vip.uuid
  custCheckoutVipSelected.value = true
  custCheckoutData.value = null
  custCheckoutLoading.value = true
  custCheckoutPayments.value = []
  try {
    const res = await request.get('/cashier/customer_checkout/', { params: { company, storecode, vipuuid: vip.uuid } })
    if (res.data?.ok) {
      custCheckoutData.value = res.data
      const pendingTotal = res.data.summary?.pending?.total || 0
      if (pendingTotal > 0.01) {
        const defPcode = paymentDefaults.value?.normal_pcode || ''
        custCheckoutPayments.value = [{ pcode: defPcode, amount: pendingTotal, _default: true }]
      }
    } else {
      ElMessage.warning(res.data?.message || '无法获取结账汇总')
    }
  } catch { ElMessage.error('获取结账汇总失败') }
  finally { custCheckoutLoading.value = false }
}

const checkoutVipName = ref('')
const checkoutVipUuid = ref('')
const checkoutPayments = ref<Record<string, string>>({})
const vipCheckoutCards = ref<{ccode:string;cardname:string;comptype:string;leftmoney:number;leftqty:number}[]>([])
const paymodes = ref<any[]>([])
const paymentDefaults = ref<Record<string, string>>({})
const checkoutSplits = ref<Record<string, any[]>>({})

const checkoutTotal = computed(() =>
  checkoutOrders.value
    .filter((o: any) => checkoutSelections.value[o.uuid])
    .reduce((s: number, o: any) => s + (o.totmount || 0), 0)
)
const checkoutSelectedCount = computed(() => Object.values(checkoutSelections.value).filter(Boolean).length)
const checkoutPaymentSummary = computed(() => {
  const summary: Record<string, number> = {}
  for (const o of checkoutOrders.value) {
    if (!checkoutSelections.value[o.uuid]) continue
    const sps = checkoutSplits.value[o.uuid] || []
    for (const sp of sps) {
      const key = sp.pcode || '__default__'
      summary[key] = (summary[key] || 0) + (sp.amount || 0)
    }
  }
  return summary
})

const checkoutIndeterminate = computed(() => {
  const vals = Object.values(checkoutSelections.value)
  return vals.some(Boolean) && !vals.every(Boolean)
})

function paymodeOptionsForOrder(o: any) {
  const hasCard = !!(o.paycode)
  const allGift = o.stype_summary === 'all_gift'
  const allNormal = o.stype_summary === 'all_normal'
  const defs = paymentDefaults.value || {}
  const opts: {label:string;value:string}[] = []
  if (hasCard) {
    const card = vipCheckoutCards.value.find((c: any) => c.ccode === o.paycode)
    opts.push({ label: `💳 ${card ? card.cardname + '(' + card.ccode + ')' : o.paycode}`, value: o.paycode })
    for (const pm of paymodes.value) {
      if (pm.iscash === '1') opts.push({ label: `💵 ${pm.pname}`, value: '' })
    }
  } else if (allGift) {
    for (const pm of paymodes.value) {
      if (pm.iscash === '2') {
        const def = pm.pcode === defs.send_pcode ? ' (默认)' : ''
        opts.push({ label: `🎁 ${pm.pname}${def}`, value: pm.pcode })
      }
    }
  } else {
    for (const pm of paymodes.value) {
      if (pm.iscash === '1') {
        const def = pm.pcode === defs.normal_pcode ? ' (默认)' : ''
        opts.push({ label: `💵 ${pm.pname}${def}`, value: pm.pcode })
      }
    }
    if (!allNormal) {
      for (const pm of paymodes.value) {
        if (pm.iscash === '2') opts.push({ label: `🎁 ${pm.pname}`, value: pm.pcode })
      }
    }
  }
  return opts
}

function toggleAllCheckout(val: boolean) {
  for (const o of checkoutOrders.value) {
    checkoutSelections.value[o.uuid] = val
  }
}

const allPaymodeOptions = computed(() => paymodes.value.map((pm: any) => ({ label: (pm.iscash === '0' ? '💳' : pm.iscash === '1' ? '💵' : '🎁') + ' ' + pm.pname, value: pm.pcode })))

function empNamesFromCodes(pmcode?: string, a1?: string, a2?: string): string {
  const es = employees.value
  const parts: string[] = []
  if (pmcode) { const e = es.find((x: any) => x.ecode === pmcode); if (e) parts.push(e.ename) }
  if (a1) { const e = es.find((x: any) => x.ecode === a1); if (e) parts.push(e.ename) }
  if (a2) { const e = es.find((x: any) => x.ecode === a2); if (e) parts.push(e.ename) }
  return parts.join(', ') || '--'
}

function initCheckoutSplitsForOrder(o: any) {
  const total = o.totmount || 0
  const sps: any[] = []
  const defPcode = paymentDefaults.value?.normal_pcode || ''
 if (o.paycode) {
   const card = vipCheckoutCards.value.find((c: any) => c.ccode === o.paycode)
   const bal = parseFloat(card?.leftmoney || 0)
    const cardPcode = (o.paytype && paymodes.value.find((pm: any) => pm.pcode === o.paytype)) ? o.paytype : defPcode
    sps.push({ pcode: cardPcode, ccode: o.paycode, amount: Math.min(total, bal), cardBalance: bal, _isCard: true })
 }
 const remaining = total - sps.reduce((s: number, sp: any) => s + sp.amount, 0)
  if (remaining > 0.01 || sps.length === 0) {
    sps.push({ pcode: defPcode, ccode: '', amount: Math.round(remaining * 100) / 100, _default: true })
  }
  return sps
}

function rebalanceSplits(o: any) {
  const sps = checkoutSplits.value[o.uuid]
  if (!sps || !sps.length) return
  const total = o.totmount || 0
  const paid = sps.reduce((s: number, sp: any) => s + (sp.amount || 0), 0)
  const diff = paid - total
  if (diff > 0.01) {
    ElMessage.warning('多付了※实际应付 ¥' + total.toFixed(2))
    for (let i = sps.length - 1; i >= 0; i--) {
      if (!sps[i]._default) {
        sps[i].amount = Math.max(0, Math.round((sps[i].amount - diff) * 100) / 100)
        break
      }
    }
  } else if (diff < -0.01) {
    const def = sps.find((sp: any) => sp._default)
    if (def) {
      def.amount = Math.max(0, Math.round((total - (paid - (def.amount || 0))) * 100) / 100)
    } else {
      const defPcode = paymentDefaults.value?.normal_pcode || ''
      sps.push({ pcode: defPcode, ccode: '', amount: Math.round(-diff * 100) / 100, _default: true })
    }
  }
}

function onSplitAmountChange(o: any, si: number) {
  const sps = checkoutSplits.value[o.uuid]
  if (!sps || si >= sps.length) return
  const sp = sps[si]
  if (sp._isCard && sp.cardBalance && sp.amount > sp.cardBalance) sp.amount = sp.cardBalance
  if (sp.amount < 0) sp.amount = 0
  rebalanceSplits(o)
}

function onSplitMethodChange(o: any, si: number) {
  const sps = checkoutSplits.value[o.uuid]
  if (!sps || si >= sps.length) return
  const sp = sps[si]
  const card = vipCheckoutCards.value.find((c: any) => c.ccode === sp.pcode)
  if (card) {
    sp.ccode = sp.pcode
    sp._isCard = true
    sp.cardBalance = parseFloat(card.leftmoney || 0)
  } else {
    sp.ccode = ''
    sp._isCard = false
    sp.cardBalance = undefined
  }
}

function addSplitMethod(o: any) {
  const sps = checkoutSplits.value[o.uuid]
  if (!sps) return
  const total = o.totmount || 0
  const usedPcodes = new Set(sps.map((s: any) => s.pcode))
  const firstAvail = allSplitOptions.value.find((opt: any) => !usedPcodes.has(opt.value) && opt.value !== '')
  if (!firstAvail) return
  const defaultIdx = sps.findIndex((s: any) => s._default)
  const amt = defaultIdx >= 0 ? Math.min(sps[defaultIdx].amount, total) : 0
  sps.splice(defaultIdx >= 0 ? defaultIdx : sps.length, 0, {
    pcode: firstAvail.value, ccode: firstAvail.isCard ? firstAvail.value : '', amount: amt, cardBalance: firstAvail.balance, _isCard: !!firstAvail.isCard,
  })
  if (defaultIdx >= 0) {
    sps[sps.length - 1].amount = Math.max(0, total - sps.reduce((s: number, sp2: any, i: number) => s + (i !== sps.length - 1 ? sp2.amount : 0), 0))
  }
}

function removeSplit(o: any, si: number) {
  const sps = checkoutSplits.value[o.uuid]
  if (!sps || si >= sps.length || sps.length <= 1) return
  sps.splice(si, 1)
  rebalanceSplits(o)
}

function splitRemaining(o: any) {
  const sps = checkoutSplits.value[o.uuid]
  if (!sps) return (o.totmount || 0)
  const total = sps.reduce((s: number, sp: any) => s + (sp.amount || 0), 0)
  return (o.totmount || 0) - total
}

const allSplitOptions = computed(() => {
  const opts: {label:string;value:string;isCard?:boolean;balance?:number}[] = []
  for (const pm of paymodes.value) {
    opts.push({ label: (pm.iscash === '0' ? '💳' : pm.iscash === '1' ? '💵' : '🎁') + ' ' + pm.pname, value: pm.pcode })
  }
  for (const c of vipCheckoutCards.value) {
    if (!opts.some((o: any) => o.value === c.ccode)) {
      const bal = c.comptype === 'times' ? parseFloat(c.leftqty || 0) : parseFloat(c.leftmoney || 0)
      opts.push({ label: '💳 ' + (c.cardname || c.ccode) + ' (余额¥' + bal.toFixed(0) + ')', value: c.ccode, isCard: true, balance: bal })
    }
  }
  return opts
})

function availableSplitsForSplit(o: any, currentSp: any) {
  const sps = checkoutSplits.value[o.uuid] || []
  const used = new Set(sps.map((s: any) => s.pcode))
  return allSplitOptions.value.filter((opt: any) => !used.has(opt.value) || opt.value === currentSp.pcode)
}

function findPaymodeName(pcode: string): string {
  if (!pcode) return '未指定'
  const m = paymodes.value.find((p: any) => p.pcode === pcode)
  return m ? m.pname : pcode
}

const paymodeOptions = ref<{label:string;value:string;iscash:string}[]>([])

function ttypeLabel(t: string): string {
  const map: Record<string, string> = { S: '服务', G: '商品', C: '售卡', I: '充值' }
  return map[t] || t || '--'
}

// 从当前数据中提取 VIP 列表
const vipList = computed(() => {
  const map = new Map<string, { vcode: string; vname: string; count: number }>()
  for (const h of fullData.value) {
    const name = h.vname || h.vcode || ''
    if (!name) continue
    const key = name
    if (map.has(key)) {
      map.get(key)!.count++
    } else {
      map.set(key, { vcode: h.vcode || '', vname: name, count: 1 })
    }
  }
  return Array.from(map.values()).sort((a, b) => b.count - a.count)
})

const stats = computed(() => {
  const data = hungList.value
  const vips = new Set(data.map((h: any) => h.vcode))
  return {
    cardCount: data.length,
    vipCount: vips.size,
    totalAmount: data.reduce((s: number, h: any) => s + (h.totmount || 0), 0),
  }
})

function toggleVipFilter(vcode: string) {
  filterVip.value = filterVip.value === vcode ? '' : vcode
}

function removeVipFilter(vcode: string) {
  if (filterVip.value === vcode) filterVip.value = ''
}

function onStatusChange() {
  const fmt = (d: Date) => {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return y + m + day
  }
  const today = fmt(new Date())
  if (filterStatus.value === '__void__') {
    dateRange.value = [today, today]
  } else if (filterStatus.value === '70') {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 30)
    dateRange.value = [fmt(start), fmt(end)]
  }
  fetchData()
}

async function fetchData() {
  selectedOrder.value = null
  detailItems.value = []
  loading.value = true
  try {
    const params: Record<string, string> = { company, storecode }
    if (filterStatus.value) {
      params.psstatus = filterStatus.value
    }
    if (hdsysuserid) {
      params.hdsysuserid = hdsysuserid
    }
    if ((filterStatus.value === '70' || filterStatus.value === '__void__') && dateRange.value && dateRange.value.length === 2) {
      params.vsdate_from = dateRange.value[0]
      params.vsdate_to = dateRange.value[1]
    }
    const res = await request.get('/adviser/get_hung_list/', { params })
    fullData.value = Array.isArray(res.data) ? res.data : []
  } catch { fullData.value = [] }
  finally { loading.value = false }
}


async function selectRow(row: any) {
  if (selectedOrder.value?.uuid === row.uuid) {
    selectedOrder.value = null
    detailItems.value = []
    return
  }
  selectedOrder.value = row
  detailLoading.value = true
  try {
    const res = await request.get('/adviser/get_hung_detail/', { params: { hunguuid: row.uuid, company } })
    detailItems.value = Array.isArray(res.data) ? res.data : []
  } catch { detailItems.value = [] }
  finally { detailLoading.value = false }
}

function selectedRowClass({ row }: { row: any }): string {
  return selectedOrder.value?.uuid === row.uuid ? 'selected-row' : ''
}

function viewHung(row: any) {
  ElMessage.info('订单：' + row.exptxserno + ' 共 ' + row.itemcount + ' 项')
}

function continueBilling(row: any) {
  // 跳转到开单页并选中该会员
  router.push('/adviser/billing')
}

async function checkout(row: any) {
  console.log("[checkout] called", row?.exptxserno)
  const vipuuid = row.vipuuid
  if (!vipuuid) { ElMessage.warning('无法获取会员信息'); return }
  checkoutVipName.value = row.vname || row.vcode || ''
  checkoutVipUuid.value = vipuuid
  checkoutDialogVisible.value = true
  checkoutLoading.value = true
  checkoutOrders.value = []
  checkoutSelections.value = {}
  checkoutSelectAll.value = false
  checkoutCashier.value = appStore.cashierCode || appStore.ecode
  checkoutCashierName.value = appStore.cashierName || appStore.fullname
  ''
  try {
    const res = await request.get('/adviser/get_hung_list/', { params: { company, storecode, vipuuid, checkout_mode: '1' } })
    const list = Array.isArray(res.data) ? res.data : []
    checkoutOrders.value = list
    checkoutPayments.value = {}
      checkoutSplits.value = {}
      for (const o of list) { 
      checkoutSelections.value[o.uuid] = (o.uuid === row.uuid)
       checkoutPayments.value[o.uuid] = o.paycode || (paymentDefaults.value?.normal_pcode || paymentDefaults.value?.send_pcode || '')
      // 初始化付款拆分
      const total = o.totmount || 0
      const sps: any[] = []
      const defPcode = paymentDefaults.value?.normal_pcode || ''
      const defPm = paymodes.value.find((pm: any) => pm.pcode === defPcode)
      if (o.paycode) {
        const card = vipCheckoutCards.value.find((c: any) => c.ccode === o.paycode)
       const bal = parseFloat(card?.leftmoney || 0)
       const cardAmt = Math.min(total, bal)
        const cardPcode = (o.paytype && paymodes.value.find((pm: any) => pm.pcode === o.paytype)) ? o.paytype : defPcode
        sps.push({ pcode: cardPcode, ccode: o.paycode, amount: cardAmt, cardBalance: bal, _isCard: true })
     }
     const remaining = total - sps.reduce((s: number, sp: any) => s + sp.amount, 0)
      if (remaining > 0.01 || sps.length === 0) {
        sps.push({ pcode: defPcode, ccode: '', amount: Math.round(remaining * 100) / 100, _default: true })
      }
      checkoutSplits.value[o.uuid] = sps
    }
    checkoutSelectAll.value = false
    // 获取会员可用卡片
    try {
      const cardRes = await request.get('/adviser/get_vip_cardlist/', { params: { company, vipuuid } })
      const cardList = Array.isArray(cardRes.data) ? cardRes.data : cardRes.data?.cards ?? []
      vipCheckoutCards.value = cardList.map((c: any) => ({
        ccode: c.ccode || '', cardname: c.cardname || '', comptype: c.comptype || '',
        leftmoney: c.leftmoney || 0, leftqty: c.leftqty || 0,
      }))
    } catch { vipCheckoutCards.value = [] }
    // 加载付款方式列表
    try {
      const pmRes = await request.get('/cashier/payment_methods/', { params: { company } })
      if (pmRes.data?.paymodes) {
        paymodes.value = pmRes.data.paymodes
        paymentDefaults.value = pmRes.data.defaults || {}
      } else {
        paymodes.value = Array.isArray(pmRes.data) ? pmRes.data : []
      }
    } catch { paymodes.value = [] }
    // 重新初始化付款拆分（此时 paymodes/paymentDefaults 已就绪）
    for (const o of checkoutOrders.value) {
      checkoutSplits.value[o.uuid] = initCheckoutSplitsForOrder(o)
    }
  } catch { checkoutOrders.value = [] }
  finally { checkoutLoading.value = false }
}

async function confirmCheckout() {
  const uuids = Object.entries(checkoutSelections.value).filter(([, v]) => v).map(([k]) => k)
  if (!uuids.length) return
  checkoutSubmitting.value = true
  try {
  console.log('[confirmCheckout] uuids:', uuids)
    const splits: Record<string, any[]> = {}
    for (const uuid of uuids) {
      const sp = checkoutSplits.value[uuid]
      if (sp?.length) {
        splits[uuid] = sp.map((s: any) => ({ pcode: s.pcode, ccode: s.ccode || '', amount: s.amount }))
      }
    }
  console.log('[confirmCheckout] splits:', JSON.parse(JSON.stringify(splits)))
    const res = await request.post('/cashier/batch_checkout/', {
      company, storecode, cashier: checkoutCashier.value, uuids, splits,
      payments: checkoutPayments.value,
    })
  console.log('[confirmCheckout] response:', res.data)
    if (res.data?.ok) {
      const s = res.data.success || 0
      ElMessage.success(`结账完成：${s}/${res.data.total || uuids.length} 单成功`)
      checkoutDialogVisible.value = false
      fetchData()
      // 显示消费单
      const selOrder = checkoutOrders.value.filter((o: any) => uuids.includes(o.uuid))
      if (selOrder.length) {
        const items: any[] = []
        for (const o of selOrder) {
          if (o.item_details?.length) {
            for (const d of o.item_details) {
              items.push({
                name: d.name, qty: d.qty, price: d.price, amount: d.subtotal || Number(d.price) * Number(d.qty),
                stype: d.stypename || (d.stype_hung === 'P' ? '赠送' : '正常'),
                stypeabbr: d.stype_hung === 'P' ? '赠' : '',
                empName: empNamesFromCodes(d.pmcode, d.asscode1, d.asscode2),
              })
            }
          }
        }
        const payments: any[] = []
        const seenPcodes = new Set<string>()
        for (const o of selOrder) {
          const sp = checkoutSplits.value[o.uuid] || []
          for (const s of sp) {
            if (!seenPcodes.has(s.pcode)) {
              seenPcodes.add(s.pcode)
              payments.push({ method: findPaymodeName(s.pcode), amount: s.amount })
            }
          }
        }
        showReceipt({
          vipName: checkoutVipName.value,
          vipCode: selOrder[0]?.vcode || selOrder[0]?.vipuuid || '',
          date: new Date().toLocaleDateString('zh-CN'),
          orders: selOrder.map((o: any) => ({
            serno: o.exptxserno,
            items: o.item_details?.map((d: any) => ({
              name: d.name, qty: d.qty, price: d.price, amount: d.subtotal || Number(d.price) * Number(d.qty),
              stype: d.stypename || (d.stype_hung === 'P' ? '赠送' : '正常'),
              stypeabbr: d.stype_hung === 'P' ? '赠' : '',
              empName: empNamesFromCodes(d.pmcode, d.asscode1, d.asscode2),
            })) || [],
          })),
          payments,
          total: selOrder.reduce((s: number, o: any) => s + (o.totmount || 0), 0),
          cashierName: checkoutCashierName.value,
          cashierCode: checkoutCashier.value,
        })
      }
    } else {
      ElMessage.error(res.data?.message || '结账失败')
    }
  } catch (e: any) { ElMessage.error('结账失败: ' + (e?.message || String(e))) }
  finally { checkoutSubmitting.value = false }
}

onMounted(() => { fetchData(); fetchEmployees() })

async function fetchEmployees() {
  try {
    const res = await request.get('/adviser/get_bookingable_empllist/', { params: { company, storecode } })
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    employees.value = list.map((e: any) => ({ ecode: e.ecode || '', ename: e.ename || '' }))
  } catch { employees.value = [] }
}

async function saveEmp(row: any) {
  if (!selectedOrder.value?.uuid) return
  try {
    await request.post('/adviser/update_hung_item_employees/', {
      hunguuid: selectedOrder.value.uuid,
      ditem: row.ditem,
      company,
      pmcode: row.pmcode || '',
      asscode1: row.asscode1 || '',
      asscode2: row.asscode2 || '',
    })
  } catch {}
}
async function voidHung(row: any) {
  try {
    await ElMessageBox.confirm('确认作废挂单「' + row.exptxserno + '」？此操作不可恢复。', '确认作废', { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
  } catch { return }
  try {
    const res = await request.post('/adviser/void_hung_order/', { hunguuid: row.uuid, company })
    if (res.data?.ok) {
      ElMessage.success('已作废')
      if (selectedOrder.value?.uuid === row.uuid) {
        selectedOrder.value = null
        detailItems.value = []
      }
      fetchData()
    } else {
      ElMessage.error(res.data?.message || '作废失败')
    }
  } catch (e: any) {
    ElMessage.error('作废失败: ' + (e?.message || String(e)))
  }
}

function groupedItems(details: any[]) {
  if (!details?.length) return []
  const groups: Record<string, { type: string; items: any[]; subtotal: number }> = {}
  for (const d of details) {
    const t = d.ttypename || '\u5176\u4ed6'
    if (!groups[t]) groups[t] = { type: t, items: [], subtotal: 0 }
    groups[t].items.push(d)
    groups[t].subtotal += Number(d.subtotal || d.amount || 0)
  }
  return Object.values(groups)
}

function showReceipt(data: any) {
  receiptData.value = data
  receiptDialogVisible.value = true
}

function printReceipt() {
  const el = document.getElementById('receipt-content')
  if (!el) return
  const win = window.open('', '_blank')
  if (!win) return
  win.document.write('<html><head><title>消费单</title>')
  win.document.write('<style>')
  win.document.write('body{font-family:"Microsoft YaHei",sans-serif;padding:30px;color:#333;max-width:600px;margin:0 auto}')
  win.document.write('h2{text-align:center;margin-bottom:20px;color:#303133}')
  win.document.write('.info{display:flex;justify-content:space-between;font-size:13px;color:#606266;margin-bottom:12px;border-bottom:1px solid #eee;padding-bottom:8px}')
  win.document.write('.item{display:flex;padding:6px 0;font-size:13px;border-bottom:1px solid #f5f5f5}')
  win.document.write('.item-name{flex:3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}')
  win.document.write('.item-qty{width:40px;text-align:center}')
  win.document.write('.item-price{width:80px;text-align:right}')
  win.document.write('.item-amount{width:80px;text-align:right;font-weight:500}')
  win.document.write('.item-tag{width:44px;text-align:center;font-size:11px;color:#909399}')
  win.document.write('.item-emp{width:80px;text-align:center;font-size:11px;color:#909399}')
  win.document.write('.pay-row{display:flex;justify-content:space-between;padding:4px 0;font-size:13px}')
  win.document.write('.total{border-top:2px solid #333;margin-top:8px;padding-top:8px;display:flex;justify-content:space-between;font-size:15px;font-weight:700}')
  win.document.write('.footer{text-align:center;margin-top:20px;font-size:11px;color:#c0c4cc}')
  win.document.write('@media print{body{padding:20px}}')
  win.document.write('</style></head><body>')
  win.document.write(el.innerHTML)
  win.document.write('</body></html>')
  win.document.close()
  setTimeout(() => { win.focus(); win.print() }, 300)
}

function copyReceiptText() {
  if (!receiptData.value) return
  const d = receiptData.value
  const lines: string[] = []
  lines.push('\u2501\u2501\u2501 \u6d88\u8d39\u5355 \u2501\u2501\u2501')
  lines.push('\u5ba2\u6237\uff1a' + d.vipName + '  (' + d.vipCode + ')')
  lines.push('\u65e5\u671f\uff1a' + d.date)
  lines.push('')
  for (const o of d.orders || []) {
    lines.push('\u250c ' + o.serno + ' \u2500\u2500\u2500\u2500\u2500')
    for (const item of o.items || []) {
      const tag = item.stype === '\u8d60\u9001' ? '[\u8d60]' : ''
      lines.push('  ' + tag + item.name + '  \u00d7' + item.qty + '  \u00a5' + Number(item.price).toFixed(2) + '  \u00a5' + Number(item.amount).toFixed(2))
    }
    lines.push('\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')
  }
  lines.push('')
  lines.push('\u2500\u2500 \u4ed8\u6b3e\u65b9\u5f0f \u2500\u2500')
  for (const p of d.payments || []) {
    lines.push('  ' + p.method + '\uff1a\u00a5' + Number(p.amount).toFixed(2))
  }
  lines.push('')
  lines.push('\u5408\u8ba1\uff1a\u00a5' + Number(d.total).toFixed(2))
  lines.push('\u6536\u94f6\u5458\uff1a' + d.cashierName + ' (' + d.cashierCode + ')')
  lines.push('\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501')
  navigator.clipboard.writeText(lines.join('\n')).then(() => {
    ElMessage.success('\u5df2\u590d\u5236\u6d88\u8d39\u5355\u5185\u5bb9')
  }).catch(() => {
    ElMessage.warning('\u590d\u5236\u5931\u8d25')
  })
}


async function showReceiptForRow(row: any) {
  try {
    const res = await request.get('/cashier/get_receipt/', { params: { hunguuid: row.uuid, company } })
    if (res.data?.ok) {
      showReceipt(res.data)
    } else {
      ElMessage.warning(res.data?.message || '无法加载消费单')
    }
  } catch (e: any) { console.error('get_receipt error', e); ElMessage.error('加载消费单失败: ' + (e?.message || String(e))) }
}

async function openCustomerCheckout() {
  // 从当前列表获取第一个有 vipuuid 的行
  const vip = fullData.value.find((h: any) => h.vipuuid)
  if (!vip) { ElMessage.warning('请先加载会员数据'); return }
  custCheckoutVipUuid.value = vip.vipuuid
  // 初始化收银员
  if (!checkoutCashier.value) {
    checkoutCashier.value = appStore.cashierCode || appStore.ecode
    checkoutCashierName.value = appStore.cashierName || appStore.fullname
  }
  // 加载付款方式
  if (!paymodes.value.length) {
    try {
      const pmRes = await request.get('/cashier/payment_methods/', { params: { company } })
      if (pmRes.data?.paymodes) {
        paymodes.value = pmRes.data.paymodes
        paymentDefaults.value = pmRes.data.defaults || {}
      }
    } catch {}
  }
  custCheckoutVisible.value = true
  custCheckoutLoading.value = true
  custCheckoutData.value = null
  custCheckoutPayments.value = []
  try {
    const res = await request.get('/cashier/customer_checkout/', {
      params: { company, storecode, vipuuid: vip.vipuuid }
    })
    if (res.data?.ok) {
      custCheckoutData.value = res.data
      // 初始化待付付款方式: 默认现金
      const pendingTotal = res.data.summary?.pending?.total || 0
      if (pendingTotal > 0.01) {
        const defPcode = paymentDefaults.value?.normal_pcode || ''
        custCheckoutPayments.value = [{ pcode: defPcode, amount: pendingTotal, _default: true }]
      }
    } else {
      ElMessage.warning(res.data?.message || '无法获取结账汇总')
    }
  } catch { ElMessage.error('获取结账汇总失败') }
  finally { custCheckoutLoading.value = false }
}

const custPendingTotal = computed(() => custCheckoutData.value?.summary?.pending?.total || 0)
const custPaidTotal = computed(() => custCheckoutPayments.value.reduce((s: number, p: any) => s + (p.amount || 0), 0))
const custGroupedOrders = computed(() => {
  const data = custCheckoutData.value
  if (!data) return []
  const groups: Record<string, {order_no:string;items:any[];total:number;}> = {}
  const pushItem = (item: any, cat: string, cardCcode?: string) => {
    const key = item.order_no || '未知'
    if (!groups[key]) groups[key] = { order_no: key, items: [], total: 0 }
    groups[key].items.push({ ...item, _cat: cat, _card: cardCcode || '' })
    groups[key].total += item.mount || 0
  }
  for (const c of (data.summary.times_cards || [])) {
    for (const it of (c.items || [])) pushItem(it, 'times', c.ccode)
  }
  for (const c of (data.summary.auto_cards || [])) {
    for (const it of (c.items || [])) pushItem(it, 'auto', c.ccode)
  }
  for (const it of (data.summary.gift?.items || [])) pushItem(it, 'gift')
  for (const it of (data.summary.pending?.items || [])) pushItem(it, 'pending')
  return Object.values(groups).sort((a, b) => a.order_no.localeCompare(b.order_no))
})
const custRemaining = computed(() => Math.max(0, custPendingTotal.value - custPaidTotal.value))

async function confirmCustomerCheckout() {
  const remaining = custRemaining.value
  if (remaining > 0.01) { ElMessage.warning('待付金额未分配完成'); return }
  if (!checkoutCashier.value) {
    // fallback to logged-in user
    checkoutCashier.value = appStore.ecode
    checkoutCashierName.value = appStore.fullname
  }
  checkoutSubmitting.value = true
  try {
    const res = await request.post('/cashier/customer_checkout_confirm/', {
      company, storecode,
      vipuuid: custCheckoutVipUuid.value,
      cashier: checkoutCashier.value,
      payments: custCheckoutPayments.value,
    })
    if (res.data?.ok) {
      ElMessage.success(`结账完成：${res.data.orders} 单共 ¥${res.data.total}`)
      custCheckoutVisible.value = false
      fetchData()
      // 显示消费单
      const d = custCheckoutData.value
      if (d) {
        const orders = (d.orders || []).map((o: any) => ({
          serno: o.exptxserno || o.order_no || '',
          items: (o.items || []).map((item: any) => ({
            name: item.name || '',
            qty: item.qty || 0,
            price: item.price || 0,
            amount: item.mount || (Number(item.price || 0) * Number(item.qty || 0)),
            stype: item._cat === 'gift' ? '赠送' : (item._cat === 'times' || item._cat === 'auto' ? '正常' : '待付'),
            stypeabbr: item._cat === 'gift' ? '赠' : (item._cat === 'pending' ? '待' : ''),
            empName: empNamesFromCodes(item.pmcode, item.asscode1, item.asscode2),
          })),
        }))
        const payments = (res.data.payments || custCheckoutPayments.value).map((p: any) => ({
          method: findPaymodeName(p.pcode || p.method),
          amount: p.amount || 0,
        }))
        showReceipt({
          vipName: d.vname || custCheckoutVipName.value || '',
          vipCode: d.vcode || '',
          date: new Date().toLocaleDateString('zh-CN'),
          orders,
          payments,
          total: d.total || 0,
          cashierName: checkoutCashierName.value,
          cashierCode: checkoutCashier.value,
        })
      }
    } else {
      ElMessage.error(res.data?.message || '结账失败')
    }
  } catch (e: any) { ElMessage.error('结账失败: ' + (e?.message || String(e))) }
  finally { checkoutSubmitting.value = false }
}

function custAddPayment() {
  const used = new Set(custCheckoutPayments.value.map((p: any) => p.pcode))
  const avail = paymodes.value.find((pm: any) => !used.has(pm.pcode) && pm.iscash === '1')
  if (!avail) { ElMessage.info('没有更多可用的付款方式'); return }
  const remaining = custRemaining.value
  if (remaining <= 0.01) { ElMessage.info('金额已分配完毕'); return }
  custCheckoutPayments.value.push({ pcode: avail.pcode, amount: Math.round(remaining * 100) / 100, _default: false })
}

function custRemovePayment(idx: number) {
  if (custCheckoutPayments.value.length <= 1) return
  custCheckoutPayments.value.splice(idx, 1)
  rebalancePayments()
}

function rebalancePayments() {
  const total = custPendingTotal.value
  if (total <= 0) return
  const paid = custCheckoutPayments.value.reduce((s: number, p: any) => s + (p.amount || 0), 0)
  const diff = paid - total
  if (diff > 0.01) {
    // 超付：警告并截断最后一个非默认项
    ElMessage.warning('多付了※实际应付 ¥' + total.toFixed(2))
    for (let i = custCheckoutPayments.value.length - 1; i >= 0; i--) {
      const p = custCheckoutPayments.value[i]
      if (!p._default) {
        const cut = Math.min(p.amount, diff)
        p.amount = Math.max(0, Math.round((p.amount - cut) * 100) / 100)
        break
      }
    }
  } else if (diff < -0.01) {
    // 少付：找默认项补足，无默认项时自动添加
    const def = custCheckoutPayments.value.find((p: any) => p._default)
    if (def) {
      // 有默认项 → 调整其金额使合计 = 待付金额
      def.amount = Math.round((total - (paid - (def.amount || 0))) * 100) / 100
    } else {
      // 无默认项（用户改了付款方式）→ 自动添加一行默认付款金额 = 差额
      const defPcode = paymentDefaults.value?.normal_pcode || ''
      custCheckoutPayments.value.push({ pcode: defPcode, amount: Math.round(-diff * 100) / 100, _default: true })
    }
  }
  // 强制刷新剩余显示
}

function custOnAmountChange() {
  rebalancePayments()
}

function custOnPmChange(idx: number) {
  const pm = custCheckoutPayments.value[idx]
  if (pm?._default) {
    // 默认项被改了付款方式，仅取消其默认标记，不新增行
    pm._default = false
  }
  rebalancePayments()
}

</script>

<style scoped>

.hung-card { flex:1; min-height:0; display:flex; flex-direction:column; }
.hung-card :deep(.el-card__body) { flex:1; min-height:0; display:flex; flex-direction:column; padding:12px; }
.hung-detail-card { display:flex; flex-direction:column; min-height:0; }
.hung-detail-card :deep(.el-card__body) { flex:1; min-height:0; display:flex; flex-direction:column; overflow:auto; }
.date-group { margin-bottom:10px; }
.date-group-header { padding:6px 10px; font-size:13px; color:#606266; background:#f5f7fa; border-radius:4px; margin-bottom:2px; display:flex; align-items:center; gap:6px; }
.date-count { font-weight:400; color:#909399; font-size:12px; margin-left:auto; }
:deep(.selected-row) { background-color: var(--el-table-current-row-bg-color, #ecf5ff); }
:deep(.selected-row td:first-child .cell)::before { content: "● "; color: #409eff; font-size:13px; font-weight:700; }
.vip-chips { display:flex; flex-wrap:wrap; gap:4px; }
.stats-bar { margin-top:12px; padding:8px 12px; background:#f5f7fa; border-radius:6px; font-size:13px; color:#606266; }
</style>
