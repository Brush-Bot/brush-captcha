FROM node:18 AS builder
WORKDIR /app
COPY . .
ARG BASE_API_URL
ENV REACT_APP_BASE_API_URL=$BASE_API_URL
RUN npm install && npm run build

# 用 nginx 作为生产环境服务器
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY ../nginx/default.conf /etc/nginx/conf.d/default.conf