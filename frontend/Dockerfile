# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY . .

RUN npm install && npm run build

# 部署阶段：用 nginx 托管构建产物
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]