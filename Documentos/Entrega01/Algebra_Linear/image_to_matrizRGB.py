import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Carregar a imagem original
img = cv2.imread('Arroz.jpg')

if img is None:
    raise FileNotFoundError(
        "Não foi possível encontrar a imagem 'Arroz.jpg'. "
        "Deixe a imagem na mesma pasta deste script."
    )

# Converter de BGR para RGB
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Extrair dimensões
h, w, c = img_rgb.shape
print(f"Dimensões da imagem: {h}x{w} com {c} canais de cor.")

# Organizar os pixels em lista
dados_pixels = []

for y in range(h):
    for x in range(w):
        r, g, b = img_rgb[y, x]
        dados_pixels.append([y, x, int(r), int(g), int(b)])

# Criar DataFrame e exportar CSV
df = pd.DataFrame(
    dados_pixels,
    columns=['Linha_Y', 'Coluna_X', 'Red', 'Green', 'Blue']
)
df.to_csv('matriz_imagem_alimento.csv', index=False, encoding='utf-8')

print("Dados exportados para 'matriz_imagem_alimento.csv' com sucesso!")

# Reconstrução imediata para teste
img_reconstruida = np.zeros((h, w, 3), dtype=np.uint8)

for _, row in df.iterrows():
    y = int(row['Linha_Y'])
    x = int(row['Coluna_X'])
    r = int(row['Red'])
    g = int(row['Green'])
    b = int(row['Blue'])
    img_reconstruida[y, x] = [r, g, b]

# Exibir imagem reconstruída
plt.figure(figsize=(8, 10))
plt.imshow(img_reconstruida)
plt.title("Imagem Reconstruída via Matriz RGB")
plt.axis('off')
plt.show()
