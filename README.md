# BreachLab — Enterprise Pentesting Training Environment

BreachLab is a local, isolated, self-provisioned **Enterprise Cyber Range** simulating **Nexora Technologies** (`nexora.test`), a fictional enterprise with interconnected web applications, APIs, Linux servers, databases, network services, employees, customers, and corporate data.

> **Disclaimer**: BreachLab is designed exclusively for **local, authorized, and isolated** offensive security training and defensive remediation validation. Never expose BreachLab networks or containers to the internet or production networks.

---

## 1. Instalação Rápida

```bash
git clone git@github.com:notmarsim/breach-lab.git
cd breach-lab
chmod +x install.sh uninstall.sh
sudo ./install.sh
newgrp docker
```

*(O ambiente oficial recomendado é uma VM **Ubuntu Server 24.04 LTS** dedicada em rede isolada, mas o instalador também suporta Debian e Kali Rolling.)*

---

## 2. Comandos da CLI (`breachlab`)

### Diagnóstico e Validação
```bash
breachlab doctor            # Verifica Docker, redes, recursos do host e isolamento
breachlab validate          # Valida configs YAML, perfis, topologia e compose.yaml
breachlab isolation-check   # Verifica políticas fail-closed e regras nftables
```

### Ciclo de Vida do Laboratório
```bash
# Iniciar (na primeira vez use --build para construir as imagens locais)
breachlab start --profile balanced --build

# Outros perfis disponíveis:
# minimal | web | api | web-api | infrastructure | privesc | balanced | full
breachlab start --profile web --build
breachlab start --profile full --build

# Verificar containers ativos e logs
breachlab status
breachlab logs
breachlab logs --service corporate-website --tail 50

# Reiniciar ou parar
breachlab restart --profile balanced
breachlab stop
```

### Cenários Reproduzíveis (Scenario Engine)
```bash
# Criar novo cenário determinístico por seed
breachlab scenario new --seed 845921 --profile balanced --mode learning --difficulty medium

# Modos: learning | blackbox | graybox | whitebox | independent | enterprise | exam | hardened
breachlab scenario new --seed 845921 --mode blackbox

# Listar, salvar, carregar e inspecionar cenários
breachlab scenario list
breachlab scenario save meu-cenario
breachlab scenario load meu-cenario
breachlab scenario info
```

### Snapshots e Recuperação
```bash
breachlab snapshot create --name baseline
breachlab snapshot list
breachlab snapshot restore baseline

# Resetar apenas um alvo (preserva progresso) ou reset global
breachlab reset --target corporate-website
breachlab reset --preserve-progress
breachlab reset --clear-progress
```

---

## 3. Como Começar o Pentest

1. **Suba o ambiente com build inicial**:
   ```bash
   breachlab start --profile balanced --build
   breachlab status
   ```

2. **Configure a resolução local dos domínios `nexora.test`** no `/etc/hosts` da máquina onde está rodando o navegador/ferramentas (apontando para `127.0.0.1` via `lab-proxy` na porta `8080`, ou para o IP da VM Ubuntu caso esteja acessando de uma VM Kali separada):
   ```bash
   echo "127.0.0.1 www.nexora.test shop.nexora.test portal.nexora.test support.nexora.test intranet.nexora.test finance.nexora.test mail.nexora.test files.nexora.test legacy.nexora.test api.nexora.test api02.nexora.test soap.nexora.test ws.nexora.test" | sudo tee -a /etc/hosts
   ```

3. **Superfície de Ataque Disponível (via `http://<dominio>:8080`)**:
   - **Web Apps**:
     - `http://www.nexora.test:8080` — Corporate Website
     - `http://shop.nexora.test:8080` — E-commerce
     - `http://portal.nexora.test:8080` — Customer Portal
     - `http://support.nexora.test:8080` — Helpdesk
     - `http://intranet.nexora.test:8080` — Intranet
     - `http://mail.nexora.test:8080` — Webmail interno (`@nexora.test`)
     - *(No perfil `full`)*: `finance.nexora.test`, `files.nexora.test`, `legacy.nexora.test`
   - **APIs**:
     - `http://api.nexora.test:8080/docs` — REST API (`/api/v1/`, `/api/v2/`, `/api/v3/`, `/api/beta/`, `/api/legacy/`)
     - `http://api02.nexora.test:8080/graphql` — GraphQL
     - `http://soap.nexora.test:8080/soap?wsdl` — SOAP / XML
     - `ws://ws.nexora.test:8080/ws/events` — WebSocket
   - **Control Center (fora do escopo de pentest — apenas gerenciamento)**:
     - `http://127.0.0.1:8443/docs` (API do Control Center: Dashboard, Flags, Dicas, Anotações e Snapshots)

---

## Documentação Adicional

- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
- [Security & Isolation](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
