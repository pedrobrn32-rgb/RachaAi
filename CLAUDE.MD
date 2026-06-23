# Claude Code Project Rules

## Cost Optimization (CRITICAL)
- NEVER run broad searches (like grep) across the whole repo if the file path is known.
- Do not re-read files unless they were modified.
- Keep responses short, concise, and direct. Do not explain code unless asked.

## Tech Stack & Code Style
- Project: Job Filler v3 (Python/Selenium/Ollama)
- Comments and variable names: ALWAYS in English.
- Explanations to the user: ALWAYS in Portuguese.
- Never use markdown code blocks inside code strings.
- Never use non-breaking spaces (U+00A0). Use common spaces (U+0020).

## [CRITICAL COST OPTIMIZATION]
- Seja extremamente conciso, direto e minimalista.
- NUNCA reescreva o código inteiro se apenas algumas linhas mudaram. 
- Forneça APENAS as linhas modificadas ou o bloco específico que precisa de correção.
- Não gaste tokens explicando o que o código faz, a menos que eu peça explicitamente.
- Responda em português, mas mantenha nomes de variáveis e comentários em inglês.