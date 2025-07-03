<template>
  <el-row justify="center" style="margin-top: 60px;">
    <el-col :span="16">
      <el-card class="white-bg-card">
        <h2 style="text-align:center;">退票</h2>
        <el-form inline>
          <el-form-item label="购票人">
            <el-input v-model="searchName" placeholder="输入购票人姓名" style="width:150px" />
          </el-form-item>
          <el-form-item label="班次">
            <el-select v-model="searchClass" placeholder="选择班次" style="width:180px">
              <el-option v-for="c in classes" :key="c.id" :label="c.class_number + ' - ' + c.route_start + '→' + c.route_end" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button class="glass-btn" type="primary" @click="searchTickets">查询</el-button>
            <el-button class="glass-btn" @click="reset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-table :data="tickets" border stripe class="mt-3">
          <el-table-column prop="id" label="票ID" width="80" />
          <el-table-column prop="user_name" label="购票人" width="120" />
          <el-table-column prop="purchase_time" label="购票时间" width="180" />
          <el-table-column prop="class_number" label="班次号" width="100" />
          <el-table-column prop="route_start" label="起点站" width="100" />
          <el-table-column prop="route_end" label="终点站" width="100" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button size="small" class="glass-btn" type="danger" @click="refund(scope.row.id)">退票</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const classes = ref([]);
const tickets = ref([]);
const searchName = ref('');
const searchClass = ref(null);

const fetchClasses = async () => {
  const res = await fetch('/api/classes');
  classes.value = await res.json();
};
const searchTickets = async () => {
  if (searchName.value) {
    const res = await fetch(`/api/tickets/user/${searchName.value}`);
    tickets.value = await res.json();
    return;
  }
  if (searchClass.value) {
    const res = await fetch(`/api/tickets/class/${searchClass.value}`);
    tickets.value = await res.json();
    return;
  }
  tickets.value = [];
};
const reset = () => {
  searchName.value = '';
  searchClass.value = null;
  tickets.value = [];
};
const refund = async (ticketId) => {
  // 获取票据详情，判断是否允许退票
  const ticket = tickets.value.find(t => t.id === ticketId);
  if (!ticket) return;
  // 获取班次出发时间
  let classId = ticket.class_id;
  let classInfo = null;
  try {
    const res = await fetch(`/api/classes`);
    const allClasses = await res.json();
    classInfo = allClasses.find(c => c.id === classId);
  } catch {}
  // 退票时间限制：用户在发车前1小时内不可退票，管理员可随时退票
  const isAdmin = localStorage.getItem('admin') === '1';
  if (!isAdmin && classInfo) {
    const dep = new Date(classInfo.departure_time);
    const now = new Date();
    if (dep - now <= 1 * 3600 * 1000) {
      window.ElMessage && window.ElMessage.error('发车前1小时内不可退票');
      return;
    }
  }
  const res = await fetch(`/api/tickets/refund/${ticketId}`, { method: 'DELETE' });
  if (res.ok) {
    window.ElMessage && window.ElMessage.success('退票成功');
  } else {
    let data = {};
    try {
      data = await res.json();
    } catch (e) {}
    window.ElMessage && window.ElMessage.error(data.status || '退票失败');
  }
  // 退票后自动刷新表格
  await searchTickets();
};
onMounted(fetchClasses);
</script>

<style scoped>
.white-bg-card {
  background: rgba(255,255,255,0.85) !important;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 32px 24px 24px 24px;
  backdrop-filter: blur(12px) saturate(160%);
  -webkit-backdrop-filter: blur(12px) saturate(160%);
}
.glass-btn {
  background: linear-gradient(90deg, rgba(64,158,255,0.18) 0%, rgba(255,255,255,0.35) 100%) !important;
  color: #409EFF !important;
  border: none !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px 0 rgba(64,158,255,0.08) !important;
  transition: background 0.2s, color 0.2s;
}
.glass-btn:hover {
  background: linear-gradient(90deg, rgba(64,158,255,0.32) 0%, rgba(255,255,255,0.5) 100%) !important;
  color: #1765ad !important;
}
</style>
