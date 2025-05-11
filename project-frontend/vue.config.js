const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': { // 当请求路径以 /api 开头时，代理到 Django 后端
        target: 'http://127.0.0.1:8000', // 你的 Django 服务器地址
        changeOrigin: true, // 是否改变源地址
        // pathRewrite: { '^/api': '' } // 如果 Django API 没有 /api 前缀，可能需要重写路径
      }
    }
  }
})