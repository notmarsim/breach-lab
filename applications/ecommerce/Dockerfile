FROM node:20-alpine

WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY server.js .

RUN adduser -D nexora_shop && chown -R nexora_shop:nexora_shop /app
USER nexora_shop

EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD wget -qO- http://127.0.0.1:3000/health >/dev/null 2>&1 || exit 1
CMD ["node", "server.js"]
