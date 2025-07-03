<template>
  <el-row justify="center" style="margin-top: 100px;">
    <el-col :span="20">
      <el-card class="white-bg-card">
        <h2>班次信息</h2>
        <el-table :data="classes" border stripe style="width: 100%">
          <el-table-column prop="class_number" label="班次号" width="80" />
          <el-table-column prop="departure_time" label="出发时间" width="180">
            <template #default="scope">{{ formatDate(scope.row.departure_time) }}</template>
          </el-table-column>
          <el-table-column prop="route_start" label="起点站" width="100" />
          <el-table-column prop="route_end" label="终点站" width="100" />
          <el-table-column prop="travel_time" label="行车时间(min)" width="120" />
          <el-table-column prop="capacity" label="额定载客量" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="new Date(scope.row.departure_time) < new Date()" type="info">已发出</el-tag>
              <el-tag v-else type="success">待发车</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="scope">
              <el-button size="small" class="glass-btn" type="primary" @click="editClass(scope.row)">编辑</el-button>
              <el-button size="small" class="refund-glass-btn" type="danger" @click="deleteClass(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-divider>新增班次</el-divider>
        <el-form :model="form" inline @submit.prevent="addClass">
          <el-form-item label="班次号"><el-input v-model="form.class_number" type="number" /></el-form-item>
          <el-form-item label="出发时间"><el-date-picker v-model="form.departure_time" type="datetime" value-format="YYYY-MM-DDTHH:mm" /></el-form-item>
          <el-form-item label="起点站"><el-input v-model="form.route_start" /></el-form-item>
          <el-form-item label="终点站"><el-input v-model="form.route_end" /></el-form-item>
          <el-form-item label="行车时间"><el-input v-model="form.travel_time" type="number" /></el-form-item>
          <el-form-item label="额定载客量"><el-input v-model="form.capacity" type="number" /></el-form-item>
          <el-form-item><el-button class="glass-btn" type="success" @click="addClass">新增</el-button></el-form-item>
        </el-form>

        <el-dialog v-model="editDialog" title="编辑班次" width="400px">
          <el-form :model="editForm">
            <el-form-item label="班次号"><el-input v-model="editForm.class_number" type="number" /></el-form-item>
            <el-form-item label="出发时间"><el-date-picker v-model="editForm.departure_time" type="datetime" value-format="YYYY-MM-DDTHH:mm" /></el-form-item>
            <el-form-item label="起点站"><el-input v-model="editForm.route_start" /></el-form-item>
            <el-form-item label="终点站"><el-input v-model="editForm.route_end" /></el-form-item>
            <el-form-item label="行车时间"><el-input v-model="editForm.travel_time" type="number" /></el-form-item>
            <el-form-item label="额定载客量"><el-input v-model="editForm.capacity" type="number" /></el-form-item>
          </el-form>
          <template #footer>
            <el-button class="glass-btn" @click="editDialog=false">取消</el-button>
            <el-button class="glass-btn" type="primary" @click="updateClass">保存</el-button>
          </template>
        </el-dialog>

        <el-divider>筛选班次</el-divider>
        <el-input v-model="filterNumber" placeholder="按班次号" style="width:150px;display:inline-block;" />
        <el-input v-model="filterDest" placeholder="按终点站" style="width:150px;display:inline-block;margin-left:10px;" />
        <el-button class="glass-btn" type="primary" @click="filterClasses" style="margin-left:10px;">查询</el-button>
        <el-button class="glass-btn" @click="resetFilter" style="margin-left:10px;">重置</el-button>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const classes = ref([]);
const form = ref({
  class_number: '',
  departure_time: '',
  route_start: '',
  route_end: '',
  travel_time: '',
  capacity: ''
});
const editDialog = ref(false);
const editForm = ref({});
const filterNumber = ref('');
const filterDest = ref('');

const fetchClasses = async () => {
  const res = await fetch('/api/classes');
  classes.value = await res.json();
};

const formatDate = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleString();
};

const addClass = async () => {
  await fetch('/api/classes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  });
  form.value = { class_number: '', departure_time: '', route_start: '', route_end: '', travel_time: '', capacity: '' };
  fetchClasses();
};

const deleteClass = async (classId) => {
  await fetch(`/api/classes/${classId}`, { method: 'DELETE' });
  fetchClasses();
};

const editClass = (c) => {
  editForm.value = { ...c };
  editForm.value.departure_time = c.departure_time.slice(0, 16);
  editDialog.value = true;
};

const updateClass = async () => {
  await fetch(`/api/classes/${editForm.value.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(editForm.value)
  });
  editDialog.value = false;
  fetchClasses();
};

const filterClasses = async () => {
  if (filterNumber.value) {
    const res = await fetch(`/api/classes/number/${filterNumber.value}`);
    const data = await res.json();
    classes.value = data ? [data] : [];
    return;
  }
  if (filterDest.value) {
    const res = await fetch(`/api/classes/destination/${filterDest.value}`);
    classes.value = await res.json();
    return;
  }
  fetchClasses();
};
const resetFilter = () => {
  filterNumber.value = '';
  filterDest.value = '';
  fetchClasses();
};

onMounted(() => {
  fetchClasses();
});
</script>
