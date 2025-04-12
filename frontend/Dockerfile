FROM node:20-alpine

WORKDIR /app

COPY . .

# 注入 API 地址（通过 build args）
ARG BASE_API_URL=http://localhost:8000
ENV VITE_BASE_API_URL=$BASE_API_URL

RUN npm install && npm run build
RUN npm install -g serve

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]