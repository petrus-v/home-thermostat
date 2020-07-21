module.exports = {
  devServer: {
    proxy: {
      "^/api/": {
        target: "http://backend:5000",
        changeOrigin: true,
      },
    },
  },
};
