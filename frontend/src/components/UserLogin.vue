<template>
  <el-row justify="center" style="margin-top: 100px;">
    <el-col :span="8">
      <el-card class="white-bg-card">
        <h2 style="text-align:center;">用户登录</h2>
        <el-form :model="form" @submit.prevent="login" label-width="80px" style="width:100%;">
          <el-form-item label="用户名" class="form-item-align">
            <el-input v-model="form.username" placeholder="请输入用户名" clearable class="full-width-input" />
          </el-form-item>
          <el-form-item label="密码" class="form-item-align">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" clearable class="full-width-input" />
          </el-form-item>
          <el-form-item label="人机验证">
            <el-button :type="sliderOk ? 'success' : 'primary'" @click="showCaptcha = true" plain>
              <template v-if="sliderOk">
                <el-icon><i-ep-success-filled /></el-icon> 验证通过
              </template>
              <template v-else>
                点击进行人机验证
              </template>
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button
              class="glass-btn"
              type="primary"
              @click="login"
              :disabled="!sliderOk"
              style="width:100%"
            >登录</el-button>
          </el-form-item>
          <el-form-item>
            <el-link class="glass-btn" type="primary" @click="$router.push('/user-register')">没有账号？去注册</el-link>
          </el-form-item>
          <el-alert v-if="error" :title="error" type="error" show-icon style="margin-top:10px;" />
        </el-form>
        <el-dialog v-model="showCaptcha" title="请完成人机验证" width="400px" :close-on-click-modal="false" :close-on-press-escape="false" append-to-body>
          <SlideCaptcha @success="onSliderSuccess" />
        </el-dialog>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElIcon } from 'element-plus';
import { SuccessFilled as IepSuccessFilled } from '@element-plus/icons-vue';
import SlideCaptcha from './SlideCaptcha.vue';

const router = useRouter();
const form = ref({ username: '', password: '' });
const error = ref('');
const sliderOk = ref(false);
const showCaptcha = ref(false);

const onSliderSuccess = () => {
  sliderOk.value = true;
  showCaptcha.value = false;
};

const login = async () => {
  error.value = '';
  if (!form.value.username || !form.value.password) {
    error.value = '用户名和密码不能为空';
    return;
  }
  if (!sliderOk.value) {
    error.value = '请完成人机验证';
    return;
  }
  try {
    const res = await fetch('/api/user/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.value.username,
        password: form.value.password
      })
    });
    if (res.ok) {
      localStorage.setItem('user', '1');
      localStorage.removeItem('admin');
      router.push('/user-purchase');
    } else {
      error.value = '用户名或密码错误';
      sliderOk.value = false;
    }
  } catch (e) {
    error.value = '网络错误，请重试';
  }
};
</script>

<style scoped>
.white-bg-card {
  background: rgba(255,255,255,0.95) !important;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.08);
  border-radius: 16px;
}
.form-item-align {
  margin-bottom: 18px;
}
.full-width-input >>> .el-input__wrapper {
  width: 100%;
}
.full-width-input {
  width: 100%;
}
</style>
