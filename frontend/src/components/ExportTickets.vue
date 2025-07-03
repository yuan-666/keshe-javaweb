<template>
  <el-row justify="center" style="margin-top: 60px;">
    <el-col :span="16">
      <el-card class="white-bg-card">
        <h2 style="text-align:center;">导入/导出数据</h2>
        <div style="display:flex;gap:16px;align-items:center;justify-content:center;">
          <el-upload
            class="glass-btn"
            :show-file-list="false"
            :before-upload="beforeUpload"
            :http-request="uploadCsv"
            accept=".csv"
          >
            <el-button class="glass-btn" type="primary">导入班次CSV</el-button>
          </el-upload>
          <el-button class="glass-btn" type="primary" @click="exportTickets">导出购票CSV</el-button>
        </div>
        <el-table :data="tickets" border stripe class="mt-3" v-if="tickets.length">
          <el-table-column prop="id" label="票ID" width="80" />
          <el-table-column prop="user_name" label="购票人" width="120" />
          <el-table-column prop="seat_type" label="座位类型" width="120" />
          <el-table-column prop="class_id" label="班次ID" width="100" />
          <el-table-column prop="purchase_time" label="购票时间" width="180" />
        </el-table>
        <el-empty v-else description="暂无购票数据" />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

const tickets = ref([]);

const fetchTickets = async () => {
  const res = await fetch('/api/tickets/export');
  tickets.value = await res.json();
};

const exportTickets = () => {
  window.location.href = '/api/tickets/export';
};

const beforeUpload = (file) => {
  if (!file.name.endsWith('.csv')) {
    ElMessage.error('只支持CSV文件');
    return false;
  }
  return true;
};

const uploadCsv = async (option) => {
  const formData = new FormData();
  formData.append('file', option.file);
  const res = await fetch('/api/classes/import-csv', {
    method: 'POST',
    body: formData
  });
  if (res.ok) {
    ElMessage.success('导入成功');
  } else {
    ElMessage.error('导入失败');
  }
};

onMounted(fetchTickets);
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
</style>