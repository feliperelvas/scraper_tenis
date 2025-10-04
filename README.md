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

- Adicionar as consultas e envio para Telegram;
- Adicionar novas lojas e padronizar o scraping.

---

Feito com ❤️ para pessoas altas que sofrem para achar tênis grandes.