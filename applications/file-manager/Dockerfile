FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY main.go .
RUN go build -o /filemanager main.go

FROM alpine:3.20
RUN adduser -D nexora_files
USER nexora_files
WORKDIR /home/nexora_files
COPY --from=builder /filemanager /usr/local/bin/filemanager
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD wget -qO- http://127.0.0.1:8080/health >/dev/null 2>&1 || exit 1
CMD ["filemanager"]
