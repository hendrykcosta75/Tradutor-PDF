# Tradutor de PDF para Português (Layout Preservado)

Este projeto é uma ferramenta para traduzir arquivos PDF inteiros para o Português (PT-BR), tentando preservar ao máximo o layout, imagens e formatação original.

## Funcionalidades

- **Preservação de Layout**: Utiliza `PyMuPDF` para substituir o texto original pelo traduzido no mesmo local, mantendo imagens e fundos.
- **Interface Gráfica Moderna**: Utiliza `ttkbootstrap`.
- **Tradução Automática**: Google Translate (via `deep-translator`).
- **Suporte a Multithreading**: UI responsiva.

## Como Usar

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Configuração de IA (Opcional)

Para obter traduções de melhor qualidade, você pode usar chaves de API do Google Gemini, OpenAI ou Anthropic.

1. Renomeie o arquivo `.env.example` para `.env`.
2. Abra o arquivo `.env` e insira suas chaves:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   OPENAI_API_KEY=sua_chave_aqui
   ANTHROPIC_API_KEY=sua_chave_aqui
   ```
3. O programa detectará automaticamente se há chaves configuradas e dará prioridade para: Gemini > OpenAI > Anthropic.
4. Se nenhuma chave for encontrada, o **Google Translate (Grátis)** será utilizado.

### Executando

Rode o arquivo principal:
```bash
python main.py
```

1. Clique em "Buscar PDF".
2. Clique em "Iniciar Tradução".
3. O arquivo gerado terá o sufixo `_PT-BR.pdf` e tentará manter a aparência do original.

## Limitações

- **PDFs Digitalizados (Scans)**: Não funcionará bem, pois não há texto selecionável para extrair e substituir. O programa não faz OCR.
- **Ajuste de Texto**: O texto traduzido pode ser maior que o espaço original, o que pode causar sobreposição ou redução da fonte.
- **Formatação de Texto**: Negrito, itálico e fontes específicas podem ser perdidos na substituição (padronizado para Helvetica).
