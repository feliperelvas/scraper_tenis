# Tenis Watcher

O **Tenis Watcher** é um projeto simples para monitorar tênis em diversas lojas (como Nike, Adidas, etc.) e avisar automaticamente quando:

1. Um modelo **voltar ao estoque** no seu tamanho;  
2. O tênis **entrar em promoção**.

A ideia surgiu porque, sendo uma pessoa alta e calçando **46–47**, é bem difícil encontrar tênis disponíveis nessas numerações — então resolvi automatizar essa busca.

## 🧠 Como funciona

- O sistema realiza **scraping** em sites de tênis selecionados e extrai informações como nome, preço, disponibilidade e tamanhos.
- Esses dados são armazenados em um **banco Supabase**, permitindo consultas e histórico de variações.
- Regras simples analisam os dados e identificam mudanças relevantes:
  - O produto voltou ao estoque;
  - O preço baixou.
- Quando alguma dessas condições é atendida, o sistema envia uma **mensagem automática via Telegram**.

## ⚙️ Tecnologias

- **Python** (scraper e lógica principal)
- **Supabase** (banco de dados)
- **Telegram Bot API** (envio de alertas)

## 🚀 Próximos passos

- Adicionar novas lojas;
- Adicionar a possibilidade de "conversar" com o bot do telegram (adicionar novos produtos).

## Observações

- Este projeto realiza scraping somente em sites que não aplicam proteções anti-bot. Sites que utilizam WAF/CDN, CAPTCHAs, bloqueios por IP ou outras defesas automatizadas (por exemplo: Nike, Adidas, Centauro) ficarão explicitamente fora do escopo — o fluxo ignora esses sites para garantir conformidade técnica e legal.

## 🕒 Execução automática

O Tenis Watcher utiliza **GitHub Actions** para executar os scrapers em intervalos regulares.

Para garantir que os workflows agendados continuem ativos, o repositório inclui um pequeno workflow de **manutenção automática**, que cria periodicamente um commit vazio. Isso evita que o GitHub desabilite execuções agendadas por inatividade do repositório.

---

Feito para aprimorar minhas skills em programação e solucionar um problema latente na vida de pessoas altas que sofrem para achar tênis grandes.
