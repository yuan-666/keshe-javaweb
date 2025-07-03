<template>
  <div class="menu-nav">
    <div class="menu-title">车票管理系统</div>
    <el-menu
      :default-active="$route.path"
      class="el-menu-vertical-demo glass-btn"
      background-color="rgba(255,255,255,0.55)"
      text-color="#333"
      active-text-color="#409EFF"
      router
      @select="onMenuSelect"
    >
      <el-menu-item index="/user-purchase" v-if="isUser" class="glass-btn">
        <i class="el-icon-tickets"></i>
        <span>购票</span>
      </el-menu-item>
      <el-menu-item index="/user-refund" v-if="isUser" class="glass-btn">
        <i class="el-icon-refresh"></i>
        <span>退票</span>
      </el-menu-item>
      <el-menu-item index="/classes" v-if="isAdmin" class="glass-btn">
        <i class="el-icon-s-operation"></i>
        <span>班次管理</span>
      </el-menu-item>
      <el-menu-item index="/stats" v-if="isAdmin" class="glass-btn">
        <i class="el-icon-data-analysis"></i>
        <span>售票统计</span>
      </el-menu-item>
      <el-menu-item index="/purchase" v-if="isAdmin" class="glass-btn">
        <i class="el-icon-tickets"></i>
        <span>售票</span>
      </el-menu-item>
      <el-menu-item index="/refund" v-if="isAdmin" class="glass-btn">
        <i class="el-icon-refresh"></i>
        <span>退票</span>
      </el-menu-item>
      <el-menu-item index="/import-export" v-if="isAdmin" class="glass-btn">
        <i class="el-icon-upload2"></i>
        <span>导入导出</span>
      </el-menu-item>
      <el-menu-item index="#logout" class="glass-btn">
        <i class="el-icon-switch-button"></i>
        <span @click="logout">退出登录</span>
      </el-menu-item>
    </el-menu>
    <div class="menu-user" v-if="currentUser">当前用户：{{ currentUser }}</div>
  </div>
  <div class="container mt-4 app-bg-fix">
    <router-view v-slot="{ Component, route }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="route.fullPath" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const isAdmin = ref(localStorage.getItem('admin') === '1');
const isUser = ref(localStorage.getItem('user') === '1');
const router = useRouter();
const route = useRoute();

const currentUser = ref(localStorage.getItem('username') || '');

const logout = () => {
  localStorage.removeItem('admin');
  localStorage.removeItem('user');
  localStorage.removeItem('username');
  router.push('/login');
};

const onMenuSelect = (index) => {
  if (index === '#logout') {
    logout();
    setTimeout(() => window.location.reload(), 0);
  } else {
    router.push(index);
  }
};

watch(route, () => {
  isAdmin.value = localStorage.getItem('admin') === '1';
  isUser.value = localStorage.getItem('user') === '1';
  currentUser.value = localStorage.getItem('username') || '';
});
</script>

<style>
body {
  min-height: 100vh;
  min-width: 100vw;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  background: url('https://bing.img.run/1920x1080.php') no-repeat center center fixed !important;
  background-size: cover !important;
}
.menu-nav {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 200px;
  background: rgba(255,255,255,0.35);
  box-shadow: 2px 0 16px 0 rgba(0,0,0,0.08);
  z-index: 10;
  padding-top: 0;
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-right: 1.5px solid rgba(255,255,255,0.18);
  display: flex;
  flex-direction: column;
}
.menu-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #409EFF;
  text-align: center;
  padding: 24px 0 12px 0;
  letter-spacing: 2px;
  background: none;
}
.menu-user {
  margin-top: auto;
  padding: 18px 0 16px 0;
  text-align: center;
  color: #666;
  font-size: 1rem;
  background: none;
}
.container.app-bg-fix {
  margin-left: 220px;
  position: relative;
  z-index: 2;
  min-height: 100vh;
}
.main-title {
  display: none;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s cubic-bezier(.55,0,.1,1);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
