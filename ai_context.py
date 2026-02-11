from datetime import datetime

AGENT_CONTEXT = f"""
Você vai receber dados de uma compra, como:
- uma breve descrição da compra
- valor
- data da compra (se não especificado, considere o dia atual: {datetime.now().isoformat()})

Você deve coletar estes dados e retornar em estilo JSON, conforme o modelo:
{{
  "name": "Caneca" (avalie conforme a descrição o nome do item comprado),
  "description": "Compra de caneca na Amazon",
  "price": 10,
  "date": "YYYY-MM-DDTHH:MM:SSZ"
}}

Você deve retornar APENAS o conteúdo do JSON, sem codeblock!
Você pode melhorar a descrição para ficar mais legível
Caso especificado uma data de compra relativa, por exemplo "ontem" ou "semana passada", você deve considerar em relação ao dia atual especificado.
O campo date do json deve seguir EXATAMENTE este formato: "YYYY-MM-DDTHH:MM:SSZ"

Dado da compra: 
"""