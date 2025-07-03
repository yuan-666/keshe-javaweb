<template>
  <el-row justify="center" style="margin-top: 100px;">
    <el-col :span="20">
      <el-card>
        <h2>售票统计</h2>
        <el-select v-model="selectedClass" placeholder="请选择班次" @change="fetchTickets" class="glass-btn">
          <el-option v-for="c in classes" :key="c.id" :label="c.class_number + ' - ' + c.route_start + '→' + c.route_end" :value="c.id" />
        </el-select>
        <el-table v-if="tickets.length" :data="tickets" border stripe class="mt-3">
          <el-table-column prop="id" label="票ID" width="80" />
          <el-table-column prop="user_name" label="购票人" width="120" />
          <el-table-column prop="seat_type" label="座位类型" width="120" />
          <el-table-column prop="purchase_time" label="购票时间" width="180" />
        </el-table>
        <el-empty v-else description="请选择班次查看售票详情" />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const classes = ref([]);
const selectedClass = ref(null);
const tickets = ref([]);

const fetchClasses = async () => {
  const res = await fetch('/api/classes');
  classes.value = await res.json();
};
const fetchTickets = async () => {
  if (!selectedClass.value) return;
  const res = await fetch(`/api/tickets/class/${selectedClass.value}`);
  tickets.value = await res.json();
};
onMounted(fetchClasses);
</script>
