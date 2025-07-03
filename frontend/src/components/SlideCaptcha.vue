<template>
  <div class="slide_box">
    <slide-verify
        ref="block"
        class="slide_box"
        :slider-text="text"
        :accuracy="accuracy"
        :imgs="imgs"
        :block-y="blockY"
        :block-size="blockSize"
        :block-shadow="false"
        @again="onAgain"
        @success="onSuccess"
        @fail="onFail"
        @refresh="onRefresh"
    />
    <el-button class="glass-btn mt-2" @click="handleClick">刷新拼图</el-button>
    <div class="mt-2">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref, defineEmits, onMounted } from 'vue';
import SlideVerify from 'vue3-slide-verify';
import 'vue3-slide-verify/dist/style.css';

const emits = defineEmits(['success']);
const msg = ref('');
const block = ref();
const text = '向右滑动完成拼图';
const accuracy = 1;
// 只在组件挂载时获取一次图片，避免每次刷新都请求新图片
const imgs = ref([]);
const photoCount = 10;
function getRandomImgUrl() {
  // 生成一个 1~10 的随机数
  const idx = Math.floor(Math.random() * photoCount) + 1;
  return `/photos/photo${idx}.jpeg`;
}
function refreshImg() {
  // 每次都随机一张，避免缓存
  const url = getRandomImgUrl() + `?t=${Date.now()}`;
  imgs.value = [url, url, url, url];
}
onMounted(refreshImg);

// 控制拼图块和缺口的垂直位置。
// 可以修改这个值来调整它们在图片上的高度。
const blockY = 70;
const blockSize = 42;

const onAgain = () => {
  msg.value = '检测到非人为操作，请重试';
  block.value?.refresh();
};
const onSuccess = (times) => {
  msg.value = `验证通过，耗时${(times / 1000).toFixed(1)}s`;
  emits('success');
};
const onFail = () => {
  msg.value = '验证不通过，请重试';
};
const onRefresh = () => {
  msg.value = '已刷新拼图';
};
const handleClick = () => {
  refreshImg();
  msg.value = '';
};
</script>

<style>
.slide_box {
  margin: 0 auto;
  width: 340px;
  padding: 10px 0 0 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
  background: none;
}

/* 控制图片尺寸 */
:deep(.slide-verify-img-panel img) {
  height: 180px !important;
  width: 320px !important;
  object-fit: cover;
  display: block;
}

/*
  移除强制设置 'top' 的样式！
  让组件通过 'blockY' prop 来控制拼图块和缺口的垂直位置。
  保留其他不冲突的样式。
*/
:deep(.slide-verify-block),
:deep(.slide-verify-block-piece) {
  /* top: 75px !important; <-- 删掉这一行！ */
  margin: 0 !important;
  padding: 0 !important;
  box-shadow: none !important;
  border: none !important;
}

/* 隐藏所有刷新按钮 */
:deep(.slide-verify-refresh),
:deep(.slide-verify-img-refresh),
:deep(.slide-verify-img-panel .slide-verify-refresh),
:deep(.slide-verify-img-panel .slide-verify-img-refresh) {
  display: none !important;
}
</style>