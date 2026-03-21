import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Ler o CSV gerado anteriormente
df_lido = pd.read_csv('matriz_imagem_alimento.csv')

# Descobrir dimensões da imagem
altura = int(df_lido['Linha_Y'].max()) + 1
largura = int(df_lido['Coluna_X'].max()) + 1

print(f"Reconstruindo imagem de dimensões: {altura}x{largura}")

# Criar matriz vazia
img_reconstruida = np.zeros((altura, largura, 3), dtype=np.uint8)

# Preencher com os dados do CSV
for _, linha in df_lido.iterrows():
    y = int(linha['Linha_Y'])
    x = int(linha['Coluna_X'])
    r = int(linha['Red'])
    g = int(linha['Green'])
    b = int(linha['Blue'])

    img_reconstruida[y, x] = [r, g, b]

# Mostrar imagem final
plt.figure(figsize=(8, 10))
plt.imshow(img_reconstruida)
plt.title("Imagem Reconstruída a partir da Representação Matricial")
plt.axis('off')
plt.show()

# Salvar a imagem reconstruída
cv2.imwrite(
    'imagem_reconstruida_final.png',
    cv2.cvtColor(img_reconstruida, cv2.COLOR_RGB2BGR)
)

print("Imagem reconstruída salva como 'imagem_reconstruida_final.png'")
