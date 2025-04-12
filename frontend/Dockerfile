# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY . .
ARG BASE_API_URL
ENV REACT_APP_BASE_API_URL=$BASE_API_URL
RUN npm install && npm run build

# 部署阶段：用 nginx 托管构建产物
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 显式暴露端口（默认 80）
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]