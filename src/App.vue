<template>
  <div id="app-root">

    <!-- ═══ 首页 ═══ -->
    <div v-if="page === 'home'" class="page">
      <header class="header">
        <h1>🪞 试妆助手</h1>
        <p class="subtitle">选一款妆容或上传参考图，看看你化完妆的样子</p>
      </header>

      <!-- 快捷入口 -->
      <div class="quick-actions">
        <div class="action-card custom" @click="startCustomRef">
          <span class="action-icon">📷</span>
          <div>
            <div class="action-title">自备参考妆容图</div>
            <div class="action-desc">上传你喜欢的妆容照片，AI 复刻到你脸上</div>
          </div>
          <span class="action-arrow">→</span>
        </div>
      </div>

      <!-- 分类标签 -->
      <div class="section-title">或选择内置妆容模板</div>
      <div class="categories">
        <button v-for="cat in categories" :key="cat"
          :class="['cat-btn', { active: activeCat === cat }]"
          @click="activeCat = cat; loadTemplates()">{{ cat }}</button>
      </div>

      <!-- 模板卡片 -->
      <div v-if="loading" class="center">加载中...</div>
      <div v-else-if="templates.length === 0" class="center empty">
        <p>暂无模板</p>
      </div>
      <div v-else class="template-grid">
        <div v-for="t in templates" :key="t.id" class="card" @click="selectTemplate(t)">
          <div class="card-img" :style="{ background: cardColor(t.color_tone) }">
            <img v-if="t.thumbnail_url" :src="t.thumbnail_url" :alt="t.name" />
            <span v-else class="card-placeholder">💄</span>
          </div>
          <div class="card-info">
            <div class="card-name">{{ t.name }}</div>
            <div class="card-meta">{{ t.makeup_style }} · {{ t.color_tone }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ 自备参考图·上传 ═══ -->
    <div v-if="page === 'customRef'" class="page">
      <header class="header">
        <button class="back-btn" @click="resetAll">← 返回</button>
        <h2>上传参考妆容</h2>
      </header>

      <label for="ref-file-input" class="upload-box">
        <div v-if="refPhotoUrl" class="upload-preview">
          <img :src="refPhotoUrl" alt="参考妆容" />
          <span class="upload-change" @click.prevent.stop="refPhotoUrl='';refPhotoFile=null">换一张</span>
        </div>
        <div v-else class="upload-placeholder">
          <span class="upload-icon">📸</span>
          <p>点击上传参考妆容照片</p>
          <p class="hint">你喜欢的妆容效果图、明星妆容、小红书截图均可</p>
        </div>
      </label>
      <input id="ref-file-input" type="file" accept="image/*" style="display:none" @change="onRefPhotoSelected" />

      <div v-if="refPhotoUrl">
        <label for="face-file-input" class="btn-primary" style="display:block;text-align:center">下一步：上传素颜照</label>
      </div>
    </div>

    <!-- ═══ 模板详情 ═══ -->
    <div v-if="page === 'detail'" class="page">
      <header class="header">
        <button class="back-btn" @click="page = 'home'">← 返回</button>
        <h2>{{ selected?.name }}</h2>
      </header>

      <div class="detail-preview">
        <img v-if="selected?.image_url" :src="selected.image_url" :alt="selected.name" />
        <div v-else class="detail-placeholder">💄</div>
      </div>

      <div class="detail-info">
        <p class="detail-desc">{{ selected?.description || '点击下方按钮上传照片开始试妆' }}</p>
        <div class="detail-tags">
          <span class="tag">{{ selected?.makeup_style }}</span>
          <span class="tag">{{ selected?.color_tone }}</span>
          <span class="tag">{{ selected?.category }}</span>
        </div>
      </div>

      <label for="face-file-input" class="btn-primary" style="display:block;text-align:center">📷 上传照片试妆</label>
    </div>

    <!-- ═══ 照片预览+生成 ═══ -->
    <div v-if="page === 'preview'" class="page">
      <header class="header">
        <button class="back-btn" @click="resetAll">← 重选</button>
        <h2>照片预览</h2>
      </header>

      <div class="preview-container">
        <img :src="photoUrl" alt="你的照片" class="preview-img" />
      </div>

      <div v-if="customMode && refPhotoUrl" class="ref-preview-mini">
        <span>参考妆容：</span>
        <img :src="refPhotoUrl" alt="参考" />
      </div>

      <div v-if="generating" class="center generating">
        <div class="spinner"></div>
        <p>AI 正在生成妆容...</p>
        <p class="hint">约需 10-15 秒</p>
      </div>

      <div v-if="!generating">
        <!-- 🎚 妆容参数 -->
        <div class="params-card">
          <!-- 出图质量 -->
          <div class="param-row">
            <span class="param-label">🖼 出图质量</span>
            <div class="toggle-group">
              <button :class="['toggle-btn', { active: modelParams.size === '1024x1024' }]"
                @click="modelParams.size = '1024x1024'">标清</button>
              <button :class="['toggle-btn', { active: modelParams.size === '2K' }]"
                @click="modelParams.size = '2K'">高清 2K</button>
            </div>
          </div>

          <!-- 妆容浓度 -->
          <div class="param-row">
            <span class="param-label">💄 妆容浓度</span>
            <span class="slider-val">{{ INTENSITY_LABELS[modelParams.intensity] }}</span>
          </div>
          <input type="range" v-model="modelParams.intensity" min="0" max="4" step="1" class="slider" />
          <div style="display:flex;justify-content:space-between;font-size:10px;color:#bbb;padding:0 2px">
            <span>淡</span><span>自然</span><span>标准</span><span>浓</span><span>精致浓</span></div>
        </div>

        <button class="btn-primary" @click="doGenerate">✨ 生成试妆</button>
        <label class="refine-toggle">
          <input type="checkbox" v-model="doRefine" />
          精修优化（+0.2元）
        </label>
      </div>
    </div>

    <!-- ═══ 结果展示 ═══ -->
    <div v-if="page === 'result'" class="page">
      <header class="header">
        <button class="back-btn" @click="resetAll">← 再试一次</button>
        <h2>试妆结果</h2>
      </header>

      <div class="result-container">
        <!-- 多变体导航 -->
        <div v-if="resultUrls.length > 1" class="variant-nav">
          <button v-for="(url, i) in resultUrls" :key="i"
            :class="['variant-dot', { active: resultIdx === i }]"
            @click="resultIdx = i; resultUrl = url">{{ i + 1 }}</button>
        </div>
        <div v-if="compareMode" class="compare-view">
          <div class="compare-half">
            <div class="compare-label">素颜</div>
            <img :src="photoUrl" alt="素颜" />
          </div>
          <div class="compare-divider"></div>
          <div class="compare-half">
            <div class="compare-label">试妆</div>
            <img :src="resultUrl" alt="试妆效果" />
          </div>
        </div>
        <img v-else :src="resultUrl" alt="试妆效果" class="result-img" />
      </div>

      <div class="result-actions">
        <button class="btn-compare" @click="compareMode = !compareMode">
          {{ compareMode ? '只看结果' : '前后对比' }}
        </button>
        <button class="btn-primary" @click="saveImage">💾 保存到相册</button>
      </div>

      <div class="share-hint">
        <p>长按图片保存到相册</p>
        <p class="hint">发朋友圈带上工作室二维码，帮你裂变引流</p>
      </div>

      <div class="lead-form">
        <h3>满意吗？预约到店</h3>
        <input v-model="leadPhone" type="tel" placeholder="手机号（必填）" class="input" />
        <input v-model="leadWechat" type="text" placeholder="微信号" class="input" />
        <button class="btn-primary" @click="submitLead" :disabled="leadSubmitting">
          {{ leadSubmitting ? '提交中...' : '📩 提交预约' }}
        </button>
      </div>
    </div>

    <!-- ═══ 文件选择器 ═══ -->
    <input id="face-file-input" type="file" accept="image/*"
      style="display:none" @change="onFileSelected" />

    <div v-if="toast" class="toast">{{ toast }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const page = ref('home')
const templates = ref([])
const categories = ['全部', '日常妆', '新娘妆', '晚宴妆', '其他']
const activeCat = ref('全部')
const loading = ref(false)
const generating = ref(false)
const selected = ref(null)
const customMode = ref(false)
const doRefine = ref(false)
const compareMode = ref(false)
const photoUrl = ref('')
const photoFile = ref(null)
const refPhotoUrl = ref('')
const refPhotoFile = ref(null)
const customPrompt = ref('')
const resultUrl = ref('')
const resultUrls = ref([])
const resultIdx = ref(0)
const toast = ref('')
const leadPhone = ref('')
const leadWechat = ref('')
const leadSubmitting = ref(false)

// ── 模型参数 ──
const INTENSITY_LEVELS = ['淡妆', '自然妆', '标准妆', '浓妆', '精致浓妆']
const INTENSITY_LABELS = ['淡妆', '自然', '标准', '浓妆', '精致浓妆']

const modelParams = ref({
  size: '1024x1024',
  intensity: 2,  // 默认标准妆
})

function intensityKey() {
  return INTENSITY_LEVELS[modelParams.value.intensity] || '标准妆'
}

const API = '/api'

async function loadTemplates() {
  loading.value = true
  try {
    const cat = activeCat.value === '全部' ? '' : activeCat.value
    const r = await fetch(`${API}/templates${cat ? '?category=' + encodeURIComponent(cat) : ''}`)
    templates.value = await r.json()
  } catch (e) {
    showToast('加载失败')
  }
  loading.value = false
}

// ── 自备参考图流程 ──
function startCustomRef() {
  customMode.value = true
  page.value = 'customRef'
}

function onRefPhotoSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  refPhotoFile.value = file
  refPhotoUrl.value = URL.createObjectURL(file)
}

// ── 模板流程 ──
function selectTemplate(t) {
  customMode.value = false
  selected.value = t
  page.value = 'detail'
}

function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  photoFile.value = file
  photoUrl.value = URL.createObjectURL(file)
  page.value = 'preview'
}

async function doGenerate() {
  if (!photoFile.value) return
  generating.value = true

  try {
    const form = new FormData()
    form.append('image', photoFile.value)

    form.append('intensity', intensityKey())
    if (customMode.value && customPrompt.value) {
      form.append('extra', customPrompt.value)
    }

    // 参考图：自备参考图模式用上传的图，模板模式用模板效果图
    if (customMode.value && refPhotoFile.value) {
      form.append('ref_image', refPhotoFile.value)
    }
    if (!customMode.value && selected.value?.id) {
      form.append('template_id', String(selected.value.id))
      if (selected.value?.image_url) {
        form.append('ref_image_url', selected.value.image_url)
      }
    }

    form.append('refine', doRefine.value ? '1' : '0')
    form.append('size', modelParams.value.size)

    const r = await fetch(`${API}/try-on`, { method: 'POST', body: form })
    const data = await r.json()

    if (r.ok) {
      resultUrl.value = data.refined_url || data.generated_url || ''
      resultUrls.value = data.generated_urls || []
      resultIdx.value = 0
      page.value = 'result'
    } else {
      showToast(data.error?.message || '生成失败，请重试')
    }
  } catch (e) {
    showToast('网络错误，请重试')
  }
  generating.value = false
}

async function saveImage() {
  if (!resultUrl.value) return
  try {
    const r = await fetch(resultUrl.value)
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = '试妆效果.png'; a.click()
    URL.revokeObjectURL(url)
    showToast('✅ 已保存')
  } catch (e) {
    showToast('长按图片即可保存到相册')
  }
}

async function submitLead() {
  if (!leadPhone.value.trim()) { showToast('请填写手机号'); return }
  leadSubmitting.value = true
  try {
    await fetch(`${API}/leads`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: leadPhone.value, wechat: leadWechat.value, template_id: selected.value?.id })
    })
    showToast('✅ 预约已提交，我们会联系你')
    leadPhone.value = ''; leadWechat.value = ''
  } catch (e) { showToast('提交失败，请重试') }
  leadSubmitting.value = false
}

function resetAll() {
  page.value = 'home'; photoUrl.value = ''; photoFile.value = null
  resultUrl.value = ''; resultUrls.value = []; resultIdx.value = 0
  compareMode.value = false; selected.value = null
  refPhotoUrl.value = ''; refPhotoFile.value = null; customPrompt.value = ''
  customMode.value = false
}

function showToast(msg) {
  toast.value = msg; setTimeout(() => toast.value = '', 2500)
}

function cardColor(tone) {
  return { '暖调': '#fef3e4', '冷调': '#eaf2fb', '中性': '#f5f0eb' }[tone] || '#f5f5f5'
}

onMounted(loadTemplates)
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #fafafa; color: #333; -webkit-tap-highlight-color: transparent; }
#app-root { max-width: 480px; margin: 0 auto; min-height: 100vh; background: #fff; position: relative; }
.page { padding: 16px 16px 40px; }

.header { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid #eee; margin-bottom: 16px; }
.header h1 { font-size: 22px; }
.header h2 { font-size: 18px; flex: 1; }
.subtitle { font-size: 13px; color: #999; margin-top: 4px; }
.section-title { font-size: 14px; color: #999; margin: 16px 0 8px; }

/* 自备参考图入口 */
.quick-actions { margin: 12px 0; }
.action-card { display: flex; align-items: center; gap: 12px; padding: 16px; border-radius: 12px; cursor: pointer; margin: 8px 0; }
.action-card.custom { background: linear-gradient(135deg, #fef5f6, #fff5f0); border: 2px dashed #e8788a; }
.action-card:active { opacity: 0.8; }
.action-icon { font-size: 36px; }
.action-title { font-size: 16px; font-weight: 600; }
.action-desc { font-size: 12px; color: #999; margin-top: 2px; }
.action-arrow { color: #e8788a; font-size: 20px; margin-left: auto; }

/* 上传框 */
.upload-box { border: 2px dashed #ddd; border-radius: 12px; padding: 40px; text-align: center; cursor: pointer; margin: 12px 0; }
.upload-placeholder .upload-icon { font-size: 48px; display: block; margin-bottom: 8px; }
.upload-preview { position: relative; }
.upload-preview img { width: 100%; max-height: 300px; object-fit: contain; border-radius: 8px; }
.upload-change { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.7); color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-size: 13px; cursor: pointer; }

/* 表单 */
.form-group { margin: 12px 0; }
.form-label { font-size: 14px; color: #666; display: block; margin-bottom: 4px; }
.textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; resize: vertical; font-family: inherit; }

/* 参考图缩略 */
.ref-preview-mini { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #fafafa; border-radius: 8px; margin: 8px 0; font-size: 13px; color: #666; }
.ref-preview-mini img { width: 40px; height: 40px; object-fit: cover; border-radius: 4px; }

/* 按钮 */
.btn-primary { display: block; width: 100%; padding: 14px; background: linear-gradient(135deg, #e8788a, #d4627a); color: #fff; border: none; border-radius: 12px; font-size: 17px; cursor: pointer; margin: 12px 0; }
.btn-primary:active { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.5; }
.back-btn { background: none; border: none; font-size: 16px; color: #666; cursor: pointer; padding: 4px 8px; }
.btn-compare { display: block; width: 100%; padding: 12px; background: #f0f0f0; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; margin: 8px 0; }

/* 分类 */
.categories { display: flex; gap: 8px; overflow-x: auto; padding: 4px 0 12px; }
.cat-btn { padding: 8px 16px; border: 1px solid #ddd; border-radius: 20px; background: #fff; font-size: 14px; white-space: nowrap; cursor: pointer; }
.cat-btn.active { background: #e8788a; color: #fff; border-color: #e8788a; }

/* 卡片 */
.template-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.card { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); cursor: pointer; }
.card:active { transform: scale(0.98); }
.card-img { height: 160px; display: flex; align-items: center; justify-content: center; }
.card-img img { width: 100%; height: 100%; object-fit: cover; }
.card-placeholder { font-size: 48px; }
.card-info { padding: 8px 12px; }
.card-name { font-size: 15px; font-weight: 600; }
.card-meta { font-size: 12px; color: #999; }

/* 详情 */
.detail-preview { width: 100%; height: 300px; display: flex; align-items: center; justify-content: center; background: #fef5f6; border-radius: 12px; margin: 12px 0; }
.detail-preview img { width: 100%; height: 100%; object-fit: cover; border-radius: 12px; }
.detail-placeholder { font-size: 72px; }
.detail-info { margin: 12px 0; }
.detail-desc { font-size: 14px; color: #666; line-height: 1.6; }
.detail-tags { display: flex; gap: 8px; margin-top: 8px; }
.tag { padding: 4px 12px; background: #fef0f2; border-radius: 12px; font-size: 12px; color: #d4627a; }

/* 预览 */
.preview-container { width: 100%; border-radius: 12px; overflow: hidden; margin: 12px 0; }
.preview-img { width: 100%; display: block; }
.refine-toggle { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #666; padding: 8px 0; }

/* 模型参数 */
.params-card { background: #fef9fa; border-radius: 12px; padding: 16px; margin: 12px 0; }
.param-row { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
.param-label { font-size: 14px; color: #555; }
.param-hint { font-size: 11px; color: #bbb; margin-top: 2px; }
.toggle-group { display: flex; gap: 4px; }
.toggle-btn { padding: 6px 14px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; cursor: pointer; background: #fff; }
.toggle-btn.active { background: #e8788a; color: #fff; border-color: #e8788a; }
.slider { width: 100%; margin: 2px 0 8px; -webkit-appearance: none; height: 6px; border-radius: 3px; background: linear-gradient(to right, #fdd4dc, #e8788a); outline: none; }
.slider::-webkit-slider-thumb { -webkit-appearance: none; width: 26px; height: 26px; border-radius: 50%; background: #fff; border: 2px solid #e8788a; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.15); }

/* 生成 */
.generating { padding: 40px 0; text-align: center; }
.spinner { width: 40px; height: 40px; border: 3px solid #f0f0f0; border-top-color: #e8788a; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 结果 */
.result-container { margin: 12px 0; }
.result-img { width: 100%; border-radius: 12px; display: block; }
.compare-view { display: flex; border-radius: 12px; overflow: hidden; }
.compare-half { flex: 1; position: relative; }
.compare-half img { width: 100%; display: block; }
.compare-label { position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.6); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.compare-divider { width: 2px; background: #fff; }
.variant-nav { display: flex; gap: 8px; justify-content: center; margin-bottom: 12px; }
.variant-dot { width: 36px; height: 36px; border-radius: 50%; border: 2px solid #ddd; background: #fff; font-size: 14px; cursor: pointer; }
.variant-dot.active { border-color: #e8788a; background: #e8788a; color: #fff; }

.lead-form { background: #fafafa; border-radius: 12px; padding: 16px; margin: 16px 0; }
.lead-form h3 { font-size: 16px; margin-bottom: 12px; }
.input { display: block; width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; margin: 8px 0; }
.share-hint { text-align: center; padding: 12px; font-size: 13px; color: #999; }
.hint { font-size: 12px; color: #bbb; margin-top: 4px; }
.center { text-align: center; padding: 32px 0; }
.empty { color: #999; }
.toast { position: fixed; bottom: 40px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: #fff; padding: 10px 24px; border-radius: 8px; font-size: 14px; z-index: 999; }
</style>
