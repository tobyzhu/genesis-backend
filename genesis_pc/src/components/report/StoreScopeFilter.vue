<template>
  <div class="store-scope-filter">
    <span class="scope-label">门店：</span>

    <el-popover
      v-model:visible="panelOpen"
      placement="bottom-start"
      :width="300"
      trigger="click"
      popper-class="store-scope-popper"
    >
      <template #reference>
        <button type="button" class="scope-trigger" :class="{ open: panelOpen }">
          <el-tooltip
            :disabled="!summaryTooltip"
            :content="summaryTooltip"
            placement="top"
            :show-after="400"
          >
            <span class="trigger-text">{{ summaryText }}</span>
          </el-tooltip>
          <span class="trigger-caret" aria-hidden="true">▾</span>
        </button>
      </template>

      <div class="scope-panel">
        <div class="panel-presets">
          <button type="button" class="preset-btn" :class="{ active: isAllSelected }" @click="selectAll">
            我的全部
          </button>
          <button
            type="button"
            class="preset-btn"
            :class="{ active: isCurrentOnly }"
            :disabled="!currentStorecode"
            @click="selectCurrent"
          >
            当前店
          </button>
          <button
            v-if="!isAllSelected && selectedCodes.length"
            type="button"
            class="preset-btn ghost"
            @click="selectAll"
          >
            全选
          </button>
          <button
            v-if="selectedCodes.length"
            type="button"
            class="preset-btn ghost"
            @click="clearSelection"
          >
            清空
          </button>
        </div>

        <el-input
          v-model="keyword"
          size="small"
          clearable
          placeholder="搜索门店名称 / 店号"
          class="panel-search"
        />

        <div class="panel-list" role="listbox" aria-multiselectable="true">
          <label
            v-for="s in filteredStores"
            :key="s.storecode"
            class="store-option"
            :class="{ checked: selectedSet.has(s.storecode) }"
          >
            <el-checkbox
              :model-value="selectedSet.has(s.storecode)"
              @change="(v: CheckboxValueType) => toggleStore(s.storecode, !!v)"
            />
            <span class="opt-name">{{ s.storename || s.storecode }}</span>
            <span class="opt-code">{{ s.storecode }}</span>
          </label>
          <div v-if="!filteredStores.length" class="panel-empty">无匹配门店</div>
        </div>

        <div class="panel-footer">
          <span class="footer-count">已选 {{ selectedCodes.length }} / {{ stores.length }}</span>
          <el-button size="small" type="primary" @click="panelOpen = false">完成</el-button>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import type { CheckboxValueType } from 'element-plus'

const props = withDefaults(defineProps<{
  stores: Array<{ storecode: string; storename: string }>
  currentStorecode?: string
}>(), {
  currentStorecode: '',
})

const emit = defineEmits<{
  change: [storecodes: string[]]
}>()

const panelOpen = ref(false)
const keyword = ref('')
const selectedCodes = ref<string[]>([])

const selectedSet = computed(() => new Set(selectedCodes.value))

const storeMap = computed(() => {
  const map = new Map<string, { storecode: string; storename: string }>()
  for (const s of props.stores) {
    if (s.storecode) map.set(s.storecode, s)
  }
  return map
})

const selectedStores = computed(() =>
  selectedCodes.value.map(code => {
    const s = storeMap.value.get(code)
    return s || { storecode: code, storename: code }
  }),
)

const filteredStores = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return props.stores
  return props.stores.filter((s) => {
    const name = (s.storename || '').toLowerCase()
    const code = (s.storecode || '').toLowerCase()
    return name.includes(q) || code.includes(q)
  })
})

const isAllSelected = computed(() => {
  const total = props.stores.length
  return total > 0 && selectedCodes.value.length === total
})

const isCurrentOnly = computed(() => {
  const cur = props.currentStorecode
  return !!cur
    && selectedCodes.value.length === 1
    && selectedCodes.value[0] === cur
})

function displayName(s: { storecode: string; storename: string }) {
  return (s.storename || s.storecode || '').trim() || s.storecode
}

/** 触发器摘要：1 家全名；2–3 家顿号连接；更多则「A、B 等 N 家」 */
const summaryText = computed(() => {
  const list = selectedStores.value
  const n = list.length
  if (!n) return '请选择门店'
  if (isAllSelected.value) return `我的全部（${n} 家）`
  if (n === 1) return displayName(list[0])
  const names = list.map(displayName)
  if (n <= 3) return names.join('、')
  return `${names[0]}、${names[1]} 等 ${n} 家`
})

/** 超过 3 家时悬停展示完整名单 */
const summaryTooltip = computed(() => {
  if (selectedStores.value.length <= 3) return ''
  return selectedStores.value.map(displayName).join('、')
})

function emitScope() {
  emit('change', [...selectedCodes.value])
}

function setCodes(codes: string[]) {
  const allowed = new Set(props.stores.map(s => s.storecode))
  selectedCodes.value = codes.filter(c => allowed.has(c))
  emitScope()
}

function selectAll() {
  setCodes(props.stores.map(s => s.storecode).filter(Boolean))
}

function selectCurrent() {
  if (!props.currentStorecode) return
  setCodes([props.currentStorecode])
}

function clearSelection() {
  setCodes([])
}

function toggleStore(code: string, checked: boolean) {
  const next = new Set(selectedCodes.value)
  if (checked) next.add(code)
  else next.delete(code)
  setCodes([...next])
}

function syncDefault() {
  if (!props.stores.length) {
    selectedCodes.value = []
    emitScope()
    return
  }
  // 首次 / 门店列表变化且当前选择为空：默认我的全部
  if (!selectedCodes.value.length) {
    selectAll()
    return
  }
  // 裁剪已失效的店号
  const allowed = new Set(props.stores.map(s => s.storecode))
  const next = selectedCodes.value.filter(c => allowed.has(c))
  if (next.length !== selectedCodes.value.length) {
    setCodes(next.length ? next : props.stores.map(s => s.storecode))
  }
}

watch(() => props.stores, () => syncDefault(), { deep: true })

onMounted(() => syncDefault())
</script>

<style scoped>
.store-scope-filter {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.scope-label {
  font-size: 13px;
  color: var(--g-color-text-secondary);
  white-space: nowrap;
}
.scope-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 280px;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid var(--g-color-border);
  border-radius: var(--g-radius-sm, 4px);
  background: var(--g-color-surface);
  color: var(--g-color-text);
  font-size: 13px;
  line-height: 1.3;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.scope-trigger:hover,
.scope-trigger.open {
  border-color: var(--g-color-primary);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--g-color-primary) 25%, transparent);
}
.trigger-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
.trigger-caret {
  flex-shrink: 0;
  font-size: 10px;
  color: var(--g-color-text-muted);
  transform: translateY(-1px);
}
.scope-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.panel-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.preset-btn {
  padding: 2px 8px;
  border: 1px solid var(--g-color-border);
  border-radius: var(--g-radius-sm, 4px);
  background: var(--g-color-surface);
  color: var(--g-color-text-secondary);
  font-size: 12px;
  line-height: 20px;
  cursor: pointer;
}
.preset-btn:hover:not(:disabled) {
  border-color: var(--g-color-primary-border);
  color: var(--g-color-primary);
}
.preset-btn.active {
  border-color: var(--g-color-primary-border);
  background: var(--g-color-primary-soft);
  color: var(--g-color-primary);
  font-weight: 500;
}
.preset-btn.ghost {
  border-color: transparent;
  background: transparent;
  color: var(--g-color-text-muted);
}
.preset-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.panel-search { width: 100%; }
.panel-list {
  max-height: 240px;
  overflow: auto;
  margin: 0 -4px;
  padding: 0 4px;
}
.store-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: var(--g-radius-sm, 4px);
  cursor: pointer;
}
.store-option:hover,
.store-option.checked {
  background: var(--g-color-primary-soft);
}
.opt-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: var(--g-color-text);
}
.opt-code {
  flex-shrink: 0;
  font-size: 11px;
  color: var(--g-color-text-muted);
  font-variant-numeric: tabular-nums;
}
.panel-empty {
  padding: 20px 8px;
  text-align: center;
  font-size: 12px;
  color: var(--g-color-text-muted);
}
.panel-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 4px;
  border-top: 1px solid var(--g-color-border);
}
.footer-count {
  font-size: 12px;
  color: var(--g-color-text-muted);
}
</style>
