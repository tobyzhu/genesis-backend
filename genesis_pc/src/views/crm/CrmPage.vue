<template>
  <div class="crm-page">
    <div class="page-head">
      <h2 class="page-title">客户关怀</h2>
      <el-button type="primary" :icon="Plus" @click="openNewTask()">新建任务</el-button>
    </div>

    <el-tabs v-model="activeTab" class="crm-tabs">
      <el-tab-pane label="回访工作台" name="tasks">
        <div class="toolbar">
          <el-select v-model="taskFilters.scope" placeholder="范围" style="width:100px" @change="loadTasks()">
            <el-option label="我的待办" value="mine" />
            <el-option label="门店全部" value="store" />
          </el-select>
          <div class="stat-chips">
            <span
              v-for="s in statChips"
              :key="s.key"
              class="stat-chip"
              :class="{ active: isStatActive(s.key) }"
              @click="setStatFilter(s.key)"
            >
              {{ s.label }} {{ taskSummary.counts?.[s.key] ?? 0 }}
            </span>
          </div>
          <el-select v-model="taskFilters.rule_type" placeholder="规则类型" clearable style="width:120px" @change="loadTasks()">
            <el-option v-for="r in dicts.rule_type" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
          <el-input
            v-model="taskFilters.keyword"
            placeholder="姓名/会员号/手机"
            clearable
            style="width:160px"
            @keyup.enter="loadTasks()"
            @clear="loadTasks()"
          />
          <el-button type="primary" :icon="Search" @click="loadTasks()">查询</el-button>
          <el-button :icon="Refresh" circle @click="loadTasks()" />
        </div>
        <div class="group-bar">
          <span class="group-label">分组</span>
          <el-select v-model="groupBy" placeholder="不分组" clearable size="small" style="width:120px" @change="onGroupByChange">
            <el-option v-for="g in groupTypes" :key="g.value" :label="g.label" :value="g.value" />
          </el-select>
          <template v-if="groupBy && taskSummary.groups?.[groupBy]">
            <el-tag
              v-for="g in taskSummary.groups[groupBy]"
              :key="g.key"
              class="group-chip"
              :class="{ active: isGroupActive(g.key) }"
              @click="selectGroup(g)"
            >
              {{ g.label }} {{ g.count }}
            </el-tag>
          </template>
          <el-tag v-if="currentGroup" closable type="warning" class="current-group" @close="clearGroup">
            {{ currentGroup.label }}
          </el-tag>
        </div>

        <template v-if="!groupBy || currentGroup || statFilterActive">
          <el-table :data="tasks" v-loading="taskLoading" size="small" stripe border class="data-table">
            <el-table-column label="客户" min-width="190">
              <template #default="{ row }">
                <div class="cell-main">
                  <span>{{ row.vip?.vname || '-' }}</span>
                  <el-button v-if="row.vip?.uuid" text type="primary" size="small" @click="openVipProfile(row)">
                    查看详情
                  </el-button>
                </div>
                <div class="cell-sub">{{ row.vip?.vcode || '' }}</div>
              </template>
            </el-table-column>
            <el-table-column label="手机号" width="120">
              <template #default="{ row }">{{ maskPhone(row.vip?.mtcode) }}</template>
            </el-table-column>
            <el-table-column label="任务类型" width="120">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.casetype_name || row.casetype || '-' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="计划期" width="190">
              <template #default="{ row }">
                <span class="date-cell">{{ row.planbegindate || '--' }} ~ {{ row.planfinishdate || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="casedesc" label="任务内容" min-width="180" show-overflow-tooltip />
            <el-table-column label="负责人" width="100">
              <template #default="{ row }">{{ row.empl_name || row.ecode || '未派单' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="statusTagType(row.status)">{{ row.status_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button size="small" :icon="View" @click="openTaskDetail(row.uuid)" circle />
                <el-button size="small" type="success" :icon="CircleCheck" @click="handleComplete(row)" circle />
                <el-button size="small" type="warning" :icon="VideoPause" @click="handlePause(row)" circle />
                <el-button size="small" :icon="Switch" @click="handleReassign(row)" circle />
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-if="taskTotal > 0"
            v-model:current-page="taskPage"
            :page-size="taskPageSize"
            :total="taskTotal"
            layout="total, prev, pager, next"
            class="pagination-bar"
            @current-change="loadTasks()"
          />
        </template>
        <el-empty v-else description="选择上方分组或状态查看对应任务" :image-size="60" />
      </el-tab-pane>

      <el-tab-pane label="关怀规则" name="rules">
        <div class="toolbar">
          <el-button type="primary" :icon="Plus" @click="openRuleDialog()">新增规则</el-button>
          <el-button :icon="Refresh" @click="loadRules()">刷新</el-button>
        </div>
        <el-table :data="rules" v-loading="ruleLoading" size="small" stripe border class="data-table">
          <el-table-column prop="rule_name" label="规则名称" min-width="150" />
          <el-table-column label="类型" width="110">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ row.rule_type_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="任务类型" width="120">
            <template #default="{ row }">{{ row.casetype_name || '-' }}</template>
          </el-table-column>
          <el-table-column label="触发配置" min-width="150">
            <template #default="{ row }">{{ ruleTriggerText(row) }}</template>
          </el-table-column>
          <el-table-column label="派单" width="110">
            <template #default="{ row }">{{ row.assignee_policy_name }}</template>
          </el-table-column>
          <el-table-column label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch :model-value="row.enabled === 'Y'" @change="(v: string | number | boolean) => toggleRule(row, v === true || v === 'true')" />
            </template>
          </el-table-column>
          <el-table-column label="上次执行" width="150">
            <template #default="{ row }">
              <div>{{ row.last_run_at || '--' }}</div>
              <div class="cell-sub">{{ row.last_run_summary || '' }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="190" fixed="right">
            <template #default="{ row }">
              <el-button size="small" :icon="Edit" @click="openRuleDialog(row)" circle />
              <el-button size="small" :icon="VideoPlay" @click="previewRule(row)" circle />
              <el-button size="small" type="success" :icon="Document" @click="runRule(row)" circle />
              <el-button size="small" type="danger" :icon="Delete" @click="deleteRule(row)" circle />
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="客户沟通档案" name="timeline">
        <div class="toolbar">
          <el-select
            v-model="timelineVip"
            filterable
            remote
            reserve-keyword
            placeholder="搜索客户（姓名/手机/会员号）"
            :remote-method="searchVipRemote"
            style="width:260px"
          >
            <el-option
              v-for="v in vipOptions"
              :key="v.uuid"
              :label="`${v.vname} (${v.vcode || ''}) ${v.mtcode || ''}`"
              :value="v.uuid"
            />
          </el-select>
          <el-button type="primary" :icon="Search" @click="loadTimeline()">查看</el-button>
          <el-button type="primary" plain :icon="Plus" :disabled="!timelineVip" @click="openLogDialog()">新增记录</el-button>
        </div>
        <el-table :data="timeline" v-loading="timelineLoading" size="small" stripe border class="data-table">
          <el-table-column label="客户" min-width="140">
            <template #default="{ row }">{{ row.vname || '-' }} ({{ row.vcode || '-' }})</template>
          </el-table-column>
          <el-table-column label="时间" width="140">
            <template #default="{ row }">{{ row.create_time }}</template>
          </el-table-column>
          <el-table-column label="类型" width="110">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ row.casetype_name || '-' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="记录内容" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">{{ row.content || row.detail || row.detaildescription || '-' }}</template>
          </el-table-column>
          <el-table-column label="员工" width="90">
            <template #default="{ row }">{{ row.ecode || '-' }}</template>
          </el-table-column>
          <el-table-column label="下次回访" width="110">
            <template #default="{ row }">{{ row.nextdate || '--' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="110" fixed="right">
            <template #default="{ row }">
              <el-button size="small" :icon="Edit" @click="openLogDialog(row)" circle />
              <el-button size="small" type="danger" :icon="Delete" @click="deleteLog(row)" circle />
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 任务详情抽屉 -->
    <el-drawer v-model="taskDrawerVisible" title="回访任务" size="560px" destroy-on-close>
      <template v-if="currentTask">
        <div class="task-hero">
          <div class="hero-vip">
            <div class="hero-name">{{ currentTask.vip?.vname || '未知客户' }}</div>
            <div class="hero-sub">{{ currentTask.vip?.vcode }} · {{ maskPhone(currentTask.vip?.mtcode) }}</div>
          </div>
          <el-tag :type="statusTagType(currentTask.status)">{{ currentTask.status_name }}</el-tag>
        </div>
        <el-descriptions :column="2" size="small" border class="task-desc">
          <el-descriptions-item label="任务类型">{{ currentTask.casetype_name }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ currentTask.empl_name || currentTask.ecode || '未派单' }}</el-descriptions-item>
          <el-descriptions-item label="计划期">{{ currentTask.planbegindate }} ~ {{ currentTask.planfinishdate }}</el-descriptions-item>
          <el-descriptions-item label="来源规则">{{ currentTask.rule?.rule_name || '手工创建' }}</el-descriptions-item>
          <el-descriptions-item label="任务内容" :span="2">{{ currentTask.casedesc || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">触达记录</div>
        <el-timeline v-if="attempts.length" class="attempts-timeline">
          <el-timeline-item v-for="a in attempts" :key="a.uuid" :timestamp="a.contact_time">
            <div class="attempt-row">
              <el-tag size="small">{{ a.channel_name }}</el-tag>
              <el-tag size="small" :type="outcomeTagType(a.outcome)">{{ a.outcome_name }}</el-tag>
              <span class="attempt-emp">{{ a.ecode || '-' }}</span>
            </div>
            <div class="attempt-detail">{{ a.content || a.detail || a.detaildescription || '（无内容记录）' }}</div>
            <div v-if="a.nextdate" class="attempt-next">下次跟进：{{ a.nextdate }}（{{ a.nextecode || '未指定' }}）</div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无触达记录" :image-size="50" />

        <div class="section-title">新增触达</div>
        <div class="suggest-actions">
          <el-button size="small" type="primary" plain :icon="MagicStick" :loading="suggesting" @click="requestSuggestion">
            AI 话术建议
          </el-button>
          <el-button size="small" :icon="Refresh" :loading="suggesting" @click="requestSuggestion">换一批</el-button>
          <span v-if="suggestion" class="suggest-source">
            {{ suggestion.source === 'llm' ? 'AI 生成' : '按模板生成' }} · {{ suggestion.count || 0 }} 套可选
          </span>
        </div>
        <div v-if="suggestion?.variants?.length" class="suggestion-panel">
          <div v-for="(v, vi) in suggestion.variants" :key="vi" class="variant-card">
            <div class="variant-head">
              <span class="variant-title">方案 {{ vi + 1 }}</span>
              <el-button size="small" type="primary" link @click="applySuggestion(`${v.opening}\n${v.invitation || ''}`)">
                整段使用
              </el-button>
            </div>
            <div class="sug-block">
              <div class="sug-label">开场白</div>
              <div class="sug-row">
                <span class="sug-text">{{ v.opening }}</span>
                <el-button size="small" type="primary" link @click="applySuggestion(v.opening)">使用</el-button>
              </div>
            </div>
            <div v-if="v.care_points?.length" class="sug-block">
              <div class="sug-label">关怀点</div>
              <div v-for="(p, i) in v.care_points" :key="i" class="sug-row">
                <span class="sug-text">{{ p }}</span>
                <el-button size="small" type="primary" link @click="applySuggestion(p)">使用</el-button>
              </div>
            </div>
            <div v-if="v.invitation" class="sug-block">
              <div class="sug-label">邀约 / 推进</div>
              <div class="sug-row">
                <span class="sug-text">{{ v.invitation }}</span>
                <el-button size="small" type="primary" link @click="applySuggestion(v.invitation)">使用</el-button>
              </div>
            </div>
            <div v-if="v.closing" class="sug-block">
              <div class="sug-label">收尾</div>
              <div class="sug-row">
                <span class="sug-text">{{ v.closing }}</span>
                <el-button size="small" type="primary" link @click="applySuggestion(v.closing)">使用</el-button>
              </div>
            </div>
            <div v-if="v.avoid?.length" class="sug-block">
              <div class="sug-label">避免事项</div>
              <div v-for="(a, i) in v.avoid" :key="i" class="sug-avoid">{{ a }}</div>
            </div>
          </div>
        </div>
        <el-form :model="attemptForm" label-width="80px" size="small">
          <el-form-item label="渠道" required>
            <el-select v-model="attemptForm.channel" style="width:100%">
              <el-option v-for="c in dicts.channel" :key="c.value" :label="c.label" :value="c.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="结果" required>
            <el-select v-model="attemptForm.outcome" style="width:100%">
              <el-option v-for="o in dicts.outcome" :key="o.value" :label="o.label" :value="o.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="内容" required>
            <el-input v-model="attemptForm.detail" type="textarea" :rows="3" placeholder="本次沟通情况" />
          </el-form-item>
          <el-form-item label="下次跟进">
            <el-date-picker v-model="attemptForm.nextdate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
          </el-form-item>
          <el-form-item label="跟进人">
            <el-select v-model="attemptForm.nextecode" clearable filterable style="width:100%">
              <el-option v-for="e in employees" :key="e.ecode" :label="e.ename" :value="e.ecode" />
            </el-select>
          </el-form-item>
          <div class="drawer-actions">
            <el-button type="primary" :loading="attemptSaving" @click="saveAttempt">保存触达</el-button>
            <el-button type="success" :loading="completing" @click="completeTask()">完成回访</el-button>
          </div>
        </el-form>
      </template>
    </el-drawer>

    <!-- 新建任务 -->
    <el-dialog v-model="newTaskVisible" title="新建回访任务" width="560px">
      <el-form :model="newTaskForm" label-width="90px" size="small">
        <el-form-item label="客户" required>
          <el-select
            v-model="newTaskForm.vipuuid"
            filterable
            remote
            reserve-keyword
            placeholder="搜索客户"
            :remote-method="searchVipRemote"
            style="width:100%"
          >
            <el-option
              v-for="v in vipOptions"
              :key="v.uuid"
              :label="`${v.vname} (${v.vcode || ''}) ${v.mtcode || ''}`"
              :value="v.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="newTaskForm.casetype" style="width:100%">
            <el-option v-for="c in dicts.casetype" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始">
          <el-date-picker v-model="newTaskForm.planbegindate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="计划完成">
          <el-date-picker v-model="newTaskForm.planfinishdate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="newTaskForm.ecode" clearable filterable style="width:100%">
            <el-option v-for="e in employees" :key="e.ecode" :label="e.ename" :value="e.ecode" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务内容">
          <el-input v-model="newTaskForm.casedesc" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newTaskVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingTask" @click="saveNewTask">保存</el-button>
      </template>
    </el-dialog>

    <!-- 规则编辑 -->
    <el-dialog v-model="ruleDialogVisible" :title="ruleForm.uuid ? '编辑规则' : '新增规则'" width="620px">
      <el-form :model="ruleForm" label-width="110px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="ruleForm.rule_name" placeholder="如：下月生日关怀" />
        </el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="ruleForm.rule_type" style="width:100%" @change="onRuleTypeChange">
            <el-option v-for="r in dicts.rule_type" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="ruleForm.casetype" clearable style="width:100%">
            <el-option v-for="c in dicts.casetype" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item v-if="ruleForm.rule_type === 'birthday' || ruleForm.rule_type === 'anniversary'" label="月份偏移">
              <el-input-number v-model="ruleForm.month_offset" :min="-12" :max="12" style="width:100%" />
            </el-form-item>
            <el-form-item v-else label="天数偏移">
              <el-input-number v-model="ruleForm.days_offset" :min="0" :max="365" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item v-if="ruleForm.rule_type === 'transaction'" label="交易类型">
              <el-select v-model="ruleForm.ttype" style="width:100%">
                <el-option label="服务" value="S" />
                <el-option label="商品" value="G" />
                <el-option label="售卡" value="C" />
                <el-option label="充值" value="I" />
              </el-select>
            </el-form-item>
            <el-form-item v-else-if="ruleForm.rule_type === 'lifecycle'" label="预警分段">
              <el-select v-model="ruleForm.lifecycle_segment" style="width:100%">
                <el-option v-for="s in dicts.lifecycle_segment" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="派单策略">
          <el-select v-model="ruleForm.assignee_policy" style="width:100%">
            <el-option v-for="p in dicts.assignee_policy" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="ruleForm.assignee_policy === 'fixed'" label="固定员工">
          <el-select v-model="ruleForm.fixed_ecode" clearable filterable style="width:100%">
            <el-option v-for="e in employees" :key="e.ecode" :label="e.ename" :value="e.ecode" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述模板">
          <el-input v-model="ruleForm.casedesc_template" placeholder="支持 {vname} {vcode} {birth} {segment} 等占位符" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="ruleForm.enabledFlag" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingRule" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>

    <!-- 规则预览结果 -->
    <el-dialog v-model="previewVisible" title="生成预览" width="760px" top="6vh">
      <div class="preview-summary">
        <span>将生成 <b>{{ previewResult.created }}</b> 条</span>
        <span>跳过 <b>{{ previewResult.skipped }}</b> 条</span>
        <span v-if="previewResult.errors?.length" class="error-text">错误 {{ previewResult.errors.length }} 条</span>
      </div>
      <el-table :data="previewResult.previews || []" size="small" border max-height="360">
        <el-table-column prop="vname" label="客户" width="110" />
        <el-table-column prop="vcode" label="会员号" width="100" />
        <el-table-column prop="planbegindate" label="计划开始" width="110" />
        <el-table-column prop="planfinishdate" label="计划完成" width="110" />
        <el-table-column prop="ecode" label="负责人" width="90" />
        <el-table-column prop="casedesc" label="任务内容" min-width="180" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <!-- 沟通记录编辑 -->
    <el-dialog v-model="logDialogVisible" :title="logForm.uuid ? '编辑记录' : '新增沟通记录'" width="520px">
      <el-form :model="logForm" label-width="80px" size="small">
        <el-form-item label="类型">
          <el-select v-model="logForm.casetype" style="width:100%">
            <el-option v-for="c in dicts.casetype" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="记录内容" required>
          <el-input v-model="logForm.detail" type="textarea" :rows="3" placeholder="本次联系客户的情况" />
        </el-form-item>
        <el-form-item label="下次回访">
          <el-date-picker v-model="logForm.nextdate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="跟进人">
          <el-select v-model="logForm.nextecode" clearable filterable style="width:100%">
            <el-option v-for="e in employees" :key="e.ecode" :label="e.ename" :value="e.ecode" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="logDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingLog" @click="saveLog">保存</el-button>
      </template>
    </el-dialog>

    <VipProfileDrawer :profile="vipProfile" :employees="employees" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Edit, Delete, View, CircleCheck, VideoPause, Switch, VideoPlay, Document, MagicStick } from '@element-plus/icons-vue'
import {
  getCrmDicts,
  listCrmRules,
  createCrmRule,
  updateCrmRule,
  deleteCrmRule,
  previewCrmRule,
  runCrmRule,
  listCrmTasks,
  getCrmTaskSummary,
  getCrmTask,
  createCrmTask,
  addCrmTaskAttempt,
  suggestCrmTaskTouch,
  completeCrmTask,
  updateCrmTaskStatus,
  listCrmTimeline,
  createCrmTimeline,
  updateCrmTimeline,
  deleteCrmTimeline,
} from '@/api/crm'
import { getVipList } from '@/api/vip'
import { getEmployeeList } from '@/api/common'
import { useAppStore } from '@/store/app'
import { useVipProfile } from '@/composables/useVipProfile'
import VipProfileDrawer from '@/components/VipProfileDrawer.vue'

const appStore = useAppStore()
const vipProfile = useVipProfile()
const activeTab = ref('tasks')

const dicts = reactive<Record<string, any>>({
  casetype: [],
  status: [],
  channel: [],
  outcome: [],
  rule_type: [],
  assignee_policy: [],
  lifecycle_segment: [],
})

const employees = ref<Array<{ ecode: string; ename: string }>>([])
const vipOptions = ref<Array<any>>([])

// ===== 回访工作台 =====
const tasks = ref<any[]>([])
const taskTotal = ref(0)
const taskPage = ref(1)
const taskPageSize = 20
const taskLoading = ref(false)
const taskFilters = reactive({
  scope: 'mine',
  status: '',
  rule_type: '',
  keyword: '',
  due_date: '',
  overdue: '',
  unassigned: '',
  source: '',
  ecode: '',
  storecode: '',
})
const taskSummary = ref<any>({})
const groupBy = ref('rule_type')
const currentGroup = ref<any>(null)
const statFilterActive = computed(() =>
  !!taskFilters.status || !!taskFilters.due_date || !!taskFilters.overdue || !!taskFilters.unassigned,
)
const statChips = [
  { key: 'total', label: '全部' },
  { key: 'today', label: '今日待办' },
  { key: 'overdue', label: '超期' },
  { key: 'in_progress', label: '进行中' },
  { key: 'completed', label: '已完成' },
  { key: 'unassigned', label: '未派单' },
]
const groupTypes = [
  { value: 'rule_type', label: '按规则类型' },
  { value: 'assignee', label: '按负责人' },
  { value: 'storecode', label: '按门店' },
]

const taskDrawerVisible = ref(false)
const currentTask = ref<any>(null)
const attempts = ref<any[]>([])
const attemptForm = reactive({ channel: '10', outcome: '20', detail: '', nextdate: '', nextecode: '' })
const attemptSaving = ref(false)
const completing = ref(false)
const suggesting = ref(false)
const suggestion = ref<any>(null)

const newTaskVisible = ref(false)
const savingTask = ref(false)
const newTaskForm = reactive({
  vipuuid: '',
  casetype: '10',
  planbegindate: '',
  planfinishdate: '',
  ecode: '',
  casedesc: '',
})

async function loadTasks() {
  taskLoading.value = true
  try {
    const params: Record<string, any> = {
      page: taskPage.value,
      page_size: taskPageSize,
      scope: taskFilters.scope || undefined,
      status: taskFilters.status || undefined,
      rule_type: taskFilters.rule_type || undefined,
      keyword: taskFilters.keyword || undefined,
      due_date: taskFilters.due_date || undefined,
      overdue: taskFilters.overdue || undefined,
      unassigned: taskFilters.unassigned || undefined,
      source: taskFilters.source || undefined,
      ecode: taskFilters.ecode || undefined,
      storecode: taskFilters.storecode || undefined,
    }
    const res = await listCrmTasks(params)
    const data = res.data?.data
    tasks.value = data?.items ?? []
    taskTotal.value = data?.total ?? 0
  } catch {
    tasks.value = []
    taskTotal.value = 0
  } finally {
    taskLoading.value = false
    loadTaskSummary()
  }
}

async function loadTaskSummary() {
  try {
    const res = await getCrmTaskSummary({
      scope: taskFilters.scope || undefined,
      keyword: taskFilters.keyword || undefined,
      rule_type: taskFilters.rule_type || undefined,
      source: taskFilters.source || undefined,
      ecode: taskFilters.ecode || undefined,
      storecode: taskFilters.storecode || undefined,
    })
    taskSummary.value = res.data?.data ?? {}
  } catch {
    taskSummary.value = {}
  }
}

function isStatActive(key: string): boolean {
  if (key === 'total') {
    return !taskFilters.status && !taskFilters.due_date && !taskFilters.overdue && !taskFilters.unassigned
  }
  if (key === 'today') return !!taskFilters.due_date
  if (key === 'overdue') return !!taskFilters.overdue
  if (key === 'unassigned') return !!taskFilters.unassigned
  if (key === 'in_progress') return taskFilters.status === '20'
  if (key === 'completed') return taskFilters.status === '30'
  return false
}

function setStatFilter(key: string) {
  taskFilters.status = ''
  taskFilters.due_date = ''
  taskFilters.overdue = ''
  taskFilters.unassigned = ''
  if (key === 'today') taskFilters.due_date = dayjs().format('YYYY-MM-DD')
  if (key === 'overdue') taskFilters.overdue = '1'
  if (key === 'in_progress') taskFilters.status = '20'
  if (key === 'completed') taskFilters.status = '30'
  if (key === 'unassigned') taskFilters.unassigned = '1'
  taskPage.value = 1
  loadTasks()
}

function onGroupByChange() {
  currentGroup.value = null
  taskFilters.ecode = ''
  taskFilters.source = ''
  taskFilters.storecode = ''
  taskPage.value = 1
  loadTasks()
}

function isGroupActive(key: string): boolean {
  return !!currentGroup.value && currentGroup.value.type === groupBy.value && currentGroup.value.key === key
}

function selectGroup(g: any) {
  currentGroup.value = { type: groupBy.value, key: g.key, label: g.label }
  taskFilters.ecode = ''
  taskFilters.source = ''
  taskFilters.storecode = ''
  if (groupBy.value === 'rule_type') {
    taskFilters.rule_type = g.key === 'manual' ? '' : g.key
    taskFilters.source = g.key === 'manual' ? 'manual' : ''
  } else if (groupBy.value === 'status') {
    taskFilters.status = g.key
  } else if (groupBy.value === 'assignee') {
    taskFilters.ecode = g.key === 'unassigned' ? '' : g.key
    taskFilters.unassigned = g.key === 'unassigned' ? '1' : ''
  } else if (groupBy.value === 'storecode') {
    taskFilters.storecode = g.key
  }
  taskPage.value = 1
  loadTasks()
}

function clearGroup() {
  currentGroup.value = null
  if (groupBy.value === 'rule_type') {
    taskFilters.rule_type = ''
    taskFilters.source = ''
  } else if (groupBy.value === 'status') {
    taskFilters.status = ''
  } else if (groupBy.value === 'assignee') {
    taskFilters.ecode = ''
    taskFilters.unassigned = ''
  } else if (groupBy.value === 'storecode') {
    taskFilters.storecode = ''
  }
  taskPage.value = 1
  loadTasks()
}

async function openTaskDetail(uuid: string) {
  taskDrawerVisible.value = true
  currentTask.value = null
  attempts.value = []
  suggestion.value = null
  Object.assign(attemptForm, { channel: '10', outcome: '20', detail: '', nextdate: '', nextecode: '' })
  try {
    const res = await getCrmTask(uuid)
    currentTask.value = res.data?.data ?? null
    attempts.value = currentTask.value?.attempts ?? []
  } catch {
    ElMessage.error('任务详情加载失败')
  }
}

function openVipProfile(row: any) {
  if (row.vip?.uuid) {
    vipProfile.showProfile(row.vip.uuid)
  }
}

async function saveAttempt() {
  if (!currentTask.value) return
  if (!attemptForm.detail.trim()) {
    ElMessage.warning('请填写触达内容')
    return
  }
  attemptSaving.value = true
  try {
    await addCrmTaskAttempt(currentTask.value.uuid, { ...attemptForm })
    ElMessage.success('触达记录已保存')
    await openTaskDetail(currentTask.value.uuid)
    loadTasks()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    attemptSaving.value = false
  }
}

async function requestSuggestion() {
  if (!currentTask.value) return
  suggesting.value = true
  suggestion.value = null
  try {
    const res = await suggestCrmTaskTouch(currentTask.value.uuid, {
      channel: attemptForm.channel,
      outcome: attemptForm.outcome,
      variants: 3,
    })
    suggestion.value = res.data?.data ?? null
    if (!suggestion.value?.opening) {
      ElMessage.warning('没有生成可用话术，请重试')
    }
  } catch {
    ElMessage.error('话术生成失败')
  } finally {
    suggesting.value = false
  }
}

function applySuggestion(text: string) {
  if (!text) return
  attemptForm.detail = attemptForm.detail.trim() ? `${attemptForm.detail.trim()}\n${text}` : text
}

async function handleComplete(row: any) {
  try {
    const { value } = await ElMessageBox.prompt('完成回访，可填写完成备注', '完成回访', {
      confirmButtonText: '完成',
      cancelButtonText: '取消',
      inputPlaceholder: '如：已电话确认到店时间',
    })
    await completeCrmTask(row.uuid, { note: value || '', outcome: '10' })
    ElMessage.success('回访已完成')
    if (currentTask.value?.uuid === row.uuid) await openTaskDetail(row.uuid)
    loadTasks()
  } catch {
    // 用户取消
  }
}

async function completeTask() {
  if (!currentTask.value) return
  completing.value = true
  try {
    await completeCrmTask(currentTask.value.uuid, { note: attemptForm.detail || '', outcome: attemptForm.outcome || '10', nextdate: attemptForm.nextdate, nextecode: attemptForm.nextecode })
    ElMessage.success('回访已完成')
    await openTaskDetail(currentTask.value.uuid)
    loadTasks()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    completing.value = false
  }
}

async function handlePause(row: any) {
  try {
    await updateCrmTaskStatus(row.uuid, { status: row.status === '40' ? '20' : '40' })
    ElMessage.success(row.status === '40' ? '已恢复任务' : '已暂停任务')
    loadTasks()
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleReassign(row: any) {
  try {
    const { value } = await ElMessageBox.prompt('输入新的负责人工号', '转派任务', {
      confirmButtonText: '转派',
      cancelButtonText: '取消',
      inputValue: row.ecode || '',
    })
    if (!value) return
    await updateCrmTaskStatus(row.uuid, { status: row.status || '10', ecode: value })
    ElMessage.success('已转派')
    loadTasks()
  } catch {
    // 取消
  }
}

function openNewTask() {
  Object.assign(newTaskForm, { vipuuid: '', casetype: '10', planbegindate: '', planfinishdate: '', ecode: '', casedesc: '' })
  newTaskVisible.value = true
}

async function saveNewTask() {
  if (!newTaskForm.vipuuid) {
    ElMessage.warning('请选择客户')
    return
  }
  savingTask.value = true
  try {
    await createCrmTask({ ...newTaskForm })
    ElMessage.success('任务已创建')
    newTaskVisible.value = false
    loadTasks()
  } catch {
    ElMessage.error('创建失败')
  } finally {
    savingTask.value = false
  }
}

// ===== 关怀规则 =====
const rules = ref<any[]>([])
const ruleLoading = ref(false)
const ruleDialogVisible = ref(false)
const savingRule = ref(false)
const ruleForm = reactive<any>({})
const previewVisible = ref(false)
const previewResult = ref<any>({})

async function loadRules() {
  ruleLoading.value = true
  try {
    const res = await listCrmRules()
    rules.value = res.data?.data ?? []
  } catch {
    rules.value = []
  } finally {
    ruleLoading.value = false
  }
}

function openRuleDialog(row?: any) {
  ruleForm.uuid = row?.uuid || ''
  ruleForm.rule_name = row?.rule_name || ''
  ruleForm.rule_type = row?.rule_type || 'birthday'
  ruleForm.casetype = row?.casetype || '10'
  ruleForm.days_offset = row?.days_offset ?? 7
  ruleForm.month_offset = row?.month_offset ?? 1
  ruleForm.ttype = row?.ttype || 'S'
  ruleForm.lifecycle_segment = row?.lifecycle_segment || 'at_risk'
  ruleForm.casedesc_template = row?.casedesc_template || ''
  ruleForm.assignee_policy = row?.assignee_policy || 'vip_ecode'
  ruleForm.fixed_ecode = row?.fixed_ecode || ''
  ruleForm.enabledFlag = (row?.enabled ?? 'Y') === 'Y'
  ruleDialogVisible.value = true
}

function onRuleTypeChange() {
  if (ruleForm.rule_type === 'transaction' && !ruleForm.days_offset) ruleForm.days_offset = 7
}

async function saveRule() {
  if (!ruleForm.rule_name) {
    ElMessage.warning('请填写规则名称')
    return
  }
  savingRule.value = true
  const payload = {
    rule_name: ruleForm.rule_name,
    rule_type: ruleForm.rule_type,
    casetype: ruleForm.casetype,
    days_offset: ruleForm.days_offset,
    month_offset: ruleForm.month_offset,
    ttype: ruleForm.ttype,
    lifecycle_segment: ruleForm.lifecycle_segment,
    casedesc_template: ruleForm.casedesc_template,
    assignee_policy: ruleForm.assignee_policy,
    fixed_ecode: ruleForm.fixed_ecode,
    enabled: ruleForm.enabledFlag ? 'Y' : 'N',
  }
  try {
    if (ruleForm.uuid) {
      await updateCrmRule(ruleForm.uuid, payload)
    } else {
      await createCrmRule(payload)
    }
    ElMessage.success('规则已保存')
    ruleDialogVisible.value = false
    loadRules()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingRule.value = false
  }
}

async function toggleRule(row: any, enabled: boolean) {
  try {
    await updateCrmRule(row.uuid, { enabled: enabled ? 'Y' : 'N' })
    row.enabled = enabled ? 'Y' : 'N'
  } catch {
    ElMessage.error('更新失败')
  }
}

async function previewRule(row: any) {
  try {
    const res = await previewCrmRule(row.uuid, { date: '', limit: 100 })
    previewResult.value = res.data?.data ?? {}
    previewVisible.value = true
  } catch {
    ElMessage.error('预览失败')
  }
}

async function runRule(row: any) {
  try {
    await ElMessageBox.confirm(`确认按规则「${row.rule_name}」立即生成任务？`, '执行规则', { type: 'warning' })
    const res = await runCrmRule(row.uuid, { date: '', limit: 5000 })
    previewResult.value = res.data?.data ?? {}
    previewVisible.value = true
    ElMessage.success(`已生成 ${previewResult.value.created} 条任务`)
    loadTasks()
    loadRules()
  } catch {
    // 取消
  }
}

async function deleteRule(row: any) {
  try {
    await ElMessageBox.confirm(`确定删除规则「${row.rule_name}」？`, '删除规则', { type: 'warning' })
    await deleteCrmRule(row.uuid)
    ElMessage.success('已删除')
    loadRules()
  } catch {
    // 取消
  }
}

// ===== 客户沟通档案 =====
const timelineVip = ref('')
const timeline = ref<any[]>([])
const timelineLoading = ref(false)
const logDialogVisible = ref(false)
const savingLog = ref(false)
const logForm = reactive<any>({})

async function loadTimeline() {
  if (!timelineVip.value) {
    ElMessage.warning('请先选择客户')
    return
  }
  timelineLoading.value = true
  try {
    const res = await listCrmTimeline({ vipuuid: timelineVip.value })
    timeline.value = res.data?.data ?? []
  } catch {
    timeline.value = []
  } finally {
    timelineLoading.value = false
  }
}

function openLogDialog(row?: any) {
  logForm.uuid = row?.uuid || ''
  logForm.vipuuid = row?.vipuuid || timelineVip.value
  logForm.casetype = row?.casetype || '10'
  logForm.detail = row?.detail || ''
  logForm.nextdate = row?.nextdate || ''
  logForm.nextecode = row?.nextecode || ''
  logDialogVisible.value = true
}

async function saveLog() {
  if (!logForm.detail.trim()) {
    ElMessage.warning('请填写记录内容')
    return
  }
  savingLog.value = true
  try {
    if (logForm.uuid) {
      await updateCrmTimeline(logForm.uuid, { detail: logForm.detail, casetype: logForm.casetype, nextdate: logForm.nextdate, nextecode: logForm.nextecode })
    } else {
      await createCrmTimeline({ vipuuid: logForm.vipuuid, detail: logForm.detail, casetype: logForm.casetype, nextdate: logForm.nextdate, nextecode: logForm.nextecode })
    }
    ElMessage.success('记录已保存')
    logDialogVisible.value = false
    loadTimeline()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingLog.value = false
  }
}

async function deleteLog(row: any) {
  try {
    await ElMessageBox.confirm('确定删除这条沟通记录？', '删除记录', { type: 'warning' })
    await deleteCrmTimeline(row.uuid)
    ElMessage.success('已删除')
    loadTimeline()
  } catch {
    // 取消
  }
}

// ===== 通用 =====
async function searchVipRemote(keyword: string) {
  if (!keyword) {
    vipOptions.value = []
    return
  }
  try {
    const res = await getVipList({ search: keyword, page_size: 20 })
    vipOptions.value = res.data?.results ?? []
  } catch {
    vipOptions.value = []
  }
}

async function loadEmployees() {
  try {
    const res = await getEmployeeList({ company: appStore.currentCompany })
    employees.value = (res.data?.results ?? []).map((e: any) => ({ ecode: e.ecode, ename: e.ename }))
  } catch {
    employees.value = []
  }
}

function maskPhone(phone: string): string {
  if (!phone) return '--'
  const s = phone.trim()
  if (s.length >= 11) return s.slice(0, 3) + '****' + s.slice(-4)
  if (s.length >= 7) return s.slice(0, 3) + '****' + s.slice(-3)
  return s
}

function statusTagType(status: string): any {
  const map: Record<string, string> = { '10': 'info', '20': 'warning', '30': 'success', '40': 'danger' }
  return map[status] || 'info'
}

function outcomeTagType(outcome: string): any {
  const map: Record<string, string> = { '10': 'success', '20': 'info', '30': 'warning', '40': 'danger', '50': 'primary' }
  return map[outcome] || 'info'
}

function ruleTriggerText(row: any): string {
  if (row.rule_type === 'birthday' || row.rule_type === 'anniversary') {
    return `月份偏移 ${row.month_offset}`
  }
  if (row.rule_type === 'transaction') {
    return `交易 ${row.ttype || 'S'} 后 ${row.days_offset} 天`
  }
  if (row.rule_type === 'lifecycle') {
    return `分段 ${row.lifecycle_segment || 'at_risk'}`
  }
  return `天数偏移 ${row.days_offset}`
}

onMounted(async () => {
  try {
    const res = await getCrmDicts()
    Object.assign(dicts, res.data?.data ?? {})
  } catch {
    // 字典加载失败不阻塞页面
  }
  await Promise.all([loadTasks(), loadRules(), loadEmployees()])
})
</script>

<style scoped>
.crm-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.page-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}
.crm-tabs :deep(.el-tabs__header) {
  margin-bottom: 6px;
}
.toolbar {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.stat-chips {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.stat-chip {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  padding: 3px 8px;
  border: 1px solid var(--g-color-border);
  border-radius: 4px;
  background: var(--g-color-surface);
  cursor: pointer;
  font-size: 12px;
  color: var(--g-color-text-muted);
  white-space: nowrap;
  transition: border-color 0.15s, background 0.15s;
}
.stat-chip.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}
.group-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.group-label {
  font-size: 12px;
  color: var(--g-color-text-muted);
}
.group-chip {
  cursor: pointer;
  font-size: 12px;
}
.group-chip.active {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.current-group {
  margin-left: 4px;
}
.data-table {
  width: 100%;
}
.pagination-bar {
  margin-top: 10px;
  justify-content: flex-end;
}
.cell-main {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  font-weight: 500;
}
.cell-main :deep(.el-button) {
  margin-left: 0;
}
.cell-sub {
  font-size: 12px;
  color: var(--g-color-text-muted);
}
.date-cell {
  font-size: 12px;
}
.task-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.hero-name {
  font-size: 16px;
  font-weight: 700;
}
.hero-sub {
  font-size: 12px;
  color: var(--g-color-text-muted);
}
.task-desc {
  margin-bottom: 16px;
}
.section-title {
  font-size: 13px;
  font-weight: 600;
  margin: 14px 0 8px;
}
.attempts-timeline {
  padding-left: 4px;
}
.attempt-row {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 4px;
}
.attempt-emp {
  font-size: 12px;
  color: var(--g-color-text-muted);
}
.attempt-detail {
  font-size: 13px;
}
.attempt-next {
  margin-top: 4px;
  font-size: 12px;
  color: var(--g-color-warning);
}
.drawer-actions {
  display: flex;
  gap: 8px;
}
.suggest-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.suggest-source {
  font-size: 12px;
  color: var(--g-color-text-muted);
}
.suggest-source.fallback {
  color: var(--el-color-warning);
}
.suggestion-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
  padding: 10px 12px;
  border: 1px solid var(--g-color-border);
  border-radius: 6px;
  background: var(--g-color-surface);
}
.variant-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  border: 1px solid var(--g-color-border);
  border-radius: 6px;
}
.variant-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}
.variant-title {
  font-size: 13px;
  font-weight: 700;
}
.sug-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sug-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-color-primary);
}
.sug-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.sug-text {
  flex: 1;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
}
.sug-avoid {
  font-size: 12px;
  color: var(--el-color-danger);
}
.preview-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
  font-size: 13px;
}
.error-text {
  color: var(--el-color-danger);
}
</style>
