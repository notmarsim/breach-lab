FROM node:20-alpine
WORKDIR /app
RUN npm init -y >/dev/null 2>&1 && npm install express@^4.19.2 --omit=dev
COPY server.js .
RUN adduser -D nexora_adm && chown -R nexora_adm:nexora_adm /app
USER nexora_adm
EXPOSE 3001
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD wget -qO- http://127.0.0.1:3001/health >/dev/null 2>&1 || exit 1
CMD ["node", "server.js"]
