<template>
  <el-dialog
    :model-value="modelValue"
    :title="multi ? '选择项目（可多选）' : '选择项目'"
    width="760px"
    top="6vh"
    append-to-body
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <div class="picker-toolbar">
      <el-radio-group v-model="activeType" size="small">
        <el-radio-button value="S">服务</el-radio-button>
        <el-radio-button value="G">商品</el-radio-button>
        <el-radio-button value="C">售卡</el-radio-button>
      </el-radio-group>
      <el-input
        v-model="keyword"
        placeholder="搜索编号 / 名称"
        clearable
        size="small"
        style="width:220px"
      />
      <span class="picker-count">{{ filteredItems.length }} 项</span>
    </div>

    <div class="picker-body">
      <div class="picker-cats" v-if="categoryList.length">
        <div class="cat-item" :class="{ active: activeCategory === '' }" @click="activeCategory = ''">全部</div>
        <div
          v-for="cat in categoryList"
          :key="cat.code"
          class="cat-item"
          :class="{ active: activeCategory === cat.code }"
          @click="activeCategory = cat.code"
        >{{ cat.name }}</div>
      </div>

      <div class="picker-list" v-loading="loading">
        <el-table
          :data="filteredItems"
          size="small"
          height="360"
          border
          @selection-change="onSelectionChange"
        >
          <el-table-column v-if="multi" type="selection" width="42" align="center" />
          <el-table-column label="编号" prop="code" width="130" show-overflow-tooltip />
          <el-table-column label="名称" prop="name" min-width="180" show-overflow-tooltip />
          <el-table-column label="价格" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column v-if="!multi" label="操作" width="90" align="center">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="chooseSingle(row)">选择</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && !filteredItems.length" description="无匹配项目" />
      </div>
    </div>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button v-if="multi" type="primary" :disabled="!selection.length" @click="confirmMulti">
        添加所选（{{ selection.length }}）
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getCategorizedItems } from '@/api/cashier'

const props = defineProps<{ modelValue: boolean; multi?: boolean }>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'confirm', items: Array<{ ttype: string; code: string; name: string; price: number }>): void
}>()

const activeType = ref<'S' | 'G' | 'C'>('S')
const keyword = ref('')
const activeCategory = ref('')
const loading = ref(false)
const selection = ref<any[]>([])
const cache = ref<Record<string, { categories: any[]; items: any[] }>>({})

const categoryList = computed(() => cache.value[activeType.value]?.categories || [])

const filteredItems = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  const catCodes = activeCategory.value ? collectCategoryCodes(categoryList.value, activeCategory.value) : []
  const items = cache.value[activeType.value]?.items || []
  return items.filter((it: any) => {
    if (catCodes.length && !catCodes.includes(it.category || '')) return false
    if (kw) {
      const code = String(it.code || '').toLowerCase()
      const name = String(it.name || '').toLowerCase()
      if (!code.includes(kw) && !name.includes(kw)) return false
    }
    return true
  })
})

watch(() => props.modelValue, async (v) => {
  if (v) {
    keyword.value = ''
    activeCategory.value = ''
    selection.value = []
    await loadType(activeType.value)
  }
})

watch(activeType, async () => {
  keyword.value = ''
  activeCategory.value = ''
  selection.value = []
  await loadType(activeType.value)
})

async function loadType(type: string) {
  if (cache.value[type]) return
  loading.value = true
  try {
    const res = await getCategorizedItems(type)
    const data = res.data || {}
    cache.value[type] = {
      categories: data.categories || [],
      items: (data.items || []).map((it: any) => ({
        code: it.code || '',
        name: it.name || it.code || '',
        price: Number(it.price || 0),
        ttype: type,
        category: it.category || '',
      })),
    }
  } catch {
    cache.value[type] = { categories: [], items: [] }
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows: any[]) {
  selection.value = rows
}

function chooseSingle(row: any) {
  emit('confirm', [toPicked(row)])
  emit('update:modelValue', false)
}

function confirmMulti() {
  emit('confirm', selection.value.map(toPicked))
  emit('update:modelValue', false)
}

function toPicked(row: any) {
  return { ttype: row.ttype || activeType.value, code: row.code, name: row.name, price: row.price }
}

function collectCategoryCodes(nodes: any[], targetCode: string): string[] {
  const result = [targetCode]
  const walk = (list: any[]) => {
    for (const n of list) {
      if (n.code === targetCode && n.children?.length) {
        for (const child of n.children) {
          result.push(child.code)
          if (child.children?.length) {
            for (const gc of child.children) result.push(gc.code)
          }
        }
      }
      if (n.children?.length) walk(n.children)
    }
  }
  walk(nodes)
  return result
}
</script>

<style scoped>
.picker-toolbar { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.picker-count { font-size: 12px; color: var(--g-color-text-muted); }
.picker-body { display: flex; gap: 10px; min-height: 360px; }
.picker-cats { width: 160px; flex-shrink: 0; overflow-y: auto; max-height: 360px; border: 1px solid var(--g-color-border); border-radius: var(--g-radius); padding: 6px; }
.cat-item { padding: 6px 10px; font-size: 13px; border-radius: var(--g-radius-sm); cursor: pointer; color: var(--g-color-text-secondary); }
.cat-item:hover { background: var(--g-color-primary-soft); color: var(--g-color-primary); }
.cat-item.active { background: var(--g-color-primary); color: #fff; font-weight: 600; }
.picker-list { flex: 1; min-width: 0; }
</style>
