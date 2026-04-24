import pandas as pd
import re
import io

file_path = 'Checklist dos pisos(Planilha1).csv'

# Lendo com tratamento de encoding misto (UTF-8 e Latin-1)
clean_lines = []
with open(file_path, 'rb') as f:
    for line in f:
        try:
            decoded_line = line.decode('utf-8')
        except UnicodeDecodeError:
            decoded_line = line.decode('latin-1')
        clean_lines.append(decoded_line)

df = pd.read_csv(io.StringIO("".join(clean_lines)), on_bad_lines='skip')

# Limpar colunas
cols = {}
for col in df.columns:
    if 'Data' in col: cols[col] = 'Data'
    elif 'Piso' in col: cols[col] = 'Piso'
    elif 'Posi' in col: cols[col] = 'Posição'
    elif 'Observa' in col: cols[col] = 'Observação'
df.rename(columns=cols, inplace=True)

# Remover colunas vazias / não nomeadas
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Função de limpeza
def clean_obs(text):
    if pd.isna(text):
        return text
    text = str(text).strip()
    
    # Substituições Específicas
    text = re.sub(r'(?i)\bdeslacrada\b', 'Deslacrado', text)
    text = re.sub(r'(?i)\bdeslacrados\b', 'Deslacrado', text)
    text = re.sub(r'(?i)\bdeslacradas\b', 'Deslacrado', text)
    text = re.sub(r'(?i)\bdeslagracado\b', 'Deslacrado', text)
    
    text = re.sub(r'(?i)\bintelbraz\b', 'Intelbras', text)
    text = re.sub(r'(?i)\bintebras\b', 'Intelbras', text)
    text = re.sub(r'(?i)\bintelbra\b', 'Intelbras', text)
    
    text = re.sub(r'(?i)\bmaquina\b', 'máquina', text)
    text = re.sub(r'(?i)\bnao\b', 'não', text)
    
    # Capitalizar primeira letra
    if len(text) > 0:
        text = text[0].upper() + text[1:]
    return text

if 'Observação' in df.columns:
    df['Observação'] = df['Observação'].apply(clean_obs)
    
# Tratamento de Piso e Posicao
if 'Piso' in df.columns:
    df['Piso'] = df['Piso'].astype(str).str.strip().str.upper()
if 'Posição' in df.columns:
    df['Posição'] = df['Posição'].astype(str).str.strip().str.upper()

# Salvar com UTF-8-SIG para Excel ler corretamente sem bugar acentos
df.to_csv(file_path, index=False, encoding='utf-8-sig')
print("Dados limpos e salvos com sucesso!")
