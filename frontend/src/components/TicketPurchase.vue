<template>
  <el-row justify="center" style="margin-top: 60px;">
    <el-col :span="12">
      <el-card class="white-bg-card">
        <h2 style="text-align:center;">购票</h2>
        <div class="mb-3">
          <label class="form-label">姓名</label>
          <input type="text" class="form-control" v-model="userName" />
        </div>
        <div class="mb-3">
          <label class="form-label">选择班次</label>
          <select class="form-select" v-model="selectedClassId">
            <option v-for="c in classes" :key="c.id" :value="c.id">
              {{ c.class_number }} - {{ c.route_start }} → {{ c.route_end }} ｜ {{ formatDate(c.departure_time) }} ｜ 剩余{{ c.capacity - (c.sold || 0) }}张
            </option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">座位类型</label>
          <div class="d-flex" style="gap: 16px;">
            <select class="form-select" v-model="seatWindow" style="width: 120px;">
              <option v-for="option in seatWindowOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <select class="form-select" v-model="seatPosition" style="width: 120px;">
              <option v-for="option in seatPositionOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
        <el-button class="glass-btn btn btn-primary" type="primary" @click="purchaseTicket">确认购票</el-button>
        <el-button class="glass-btn btn btn-success" type="success" style="margin-left: 16px;" @click="exportMyTickets">导出我的购票信息</el-button>
        <el-divider />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const classes = ref([]);
const userName = ref('');
const selectedClassId = ref('');
const seatWindow = ref('window');
const seatPosition = ref('front');
const seatWindowOptions = [
  { label: '靠窗', value: 'window' },
  { label: '靠过道', value: 'aisle' }
];
const seatPositionOptions = [
  { label: '靠前', value: 'front' },
  { label: '靠后', value: 'back' }
];
const route = useRoute();

const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleString();
};

const fetchClasses = async () => {
  const res = await fetch('/api/classes');
  let data = await res.json();
  // 获取每个班次已售票数
  for (let c of data) {
    const ticketRes = await fetch(`/api/tickets/class/${c.id}`);
    const tickets = await ticketRes.json();
    c.sold = tickets.length;
  }
  classes.value = data;
};

onMounted(() => {
  fetchClasses();
});

// 监听路由变化，切换菜单时自动刷新数据
watch(route, () => {
  fetchClasses();
});

const purchaseTicket = async () => {
  if (!userName.value || !selectedClassId.value) {
    alert('请输入姓名并选择班次');
    return;
  }
  const seat_type = seatWindow.value + '-' + seatPosition.value;
  const res = await fetch('/api/tickets/purchase', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      class_id: selectedClassId.value,
      user_name: userName.value,
      seat_type
    })
  });
  if (res.ok) {
    alert('购票成功');
    userName.value = '';
    selectedClassId.value = '';
    seatWindow.value = 'window';
    seatPosition.value = 'front';
    fetchClasses();
  } else {
    let data = {};
    try {
      data = await res.json();
    } catch (e) {}
    alert(data.status || '购票失败，可能已无余票或已重复购票');
  }
};

const exportMyTickets = async () => {
  if (!userName.value) {
    alert('请输入姓名后再导出');
    return;
  }
  const url = `/api/tickets/export?user_name=${encodeURIComponent(userName.value)}`;
  const res = await fetch(url, { credentials: 'include' });
  if (!res.ok) {
    alert('导出失败');
    return;
  }
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = window.URL.createObjectURL(blob);
  a.download = 'tickets.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(a.href);
};
</script>

<style scoped>
.white-bg-card {
  background: rgba(255,255,255,0.95) !important;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 32px 24px 24px 24px;
}
</style>
