import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

print("Carregando CSV...")
df = pd.read_csv('matriz_imagem_alimento.csv')

altura  = int(df['Linha_Y'].max()) + 1
largura = int(df['Coluna_X'].max()) + 1
print(f"Dimensões reconstruídas: {altura}×{largura} pixels")

img_rgb = np.zeros((altura, largura, 3), dtype=np.uint8)
img_rgb[df['Linha_Y'].values,
        df['Coluna_X'].values] = df[['Red', 'Green', 'Blue']].values

print("Imagem reconstruída com sucesso!")
h, w = altura, largura

M_escala = np.array([[0.5,  0,  0],
                     [ 0,  0.5, 0],
                     [ 0,   0,  1]], dtype=np.float64)

theta = np.radians(45)
c, s  = np.cos(theta), np.sin(theta)
diag  = int(np.ceil(np.sqrt(w**2 + h**2)))
cx, cy = w / 2, h / 2
M_rotacao = np.array([
    [ c, -s, -cx*c + cy*s + diag/2],
    [ s,  c, -cx*s - cy*c + diag/2],
    [ 0,  0,  1]
], dtype=np.float64)

M_cisalhamento = np.array([[1, 0.5, 0],
                            [0,  1,  0],
                            [0,  0,  1]], dtype=np.float64)

M_reflexao = np.array([[-1,  0, w-1],
                        [ 0,  1,  0 ],
                        [ 0,  0,  1 ]], dtype=np.float64)

M_projecao = np.array([[1, 0, 0],
                        [0, 0, 0],
                        [0, 0, 1]], dtype=np.float64)

def aplicar_transformacao(img, M, novo_w=None, novo_h=None):
    src_h, src_w = img.shape[:2]
    dst_h = novo_h if novo_h else src_h
    dst_w = novo_w if novo_w else src_w
    img_out = np.zeros((dst_h, dst_w, 3), dtype=np.uint8)

    if abs(np.linalg.det(M)) < 1e-10:
        yy, xx = np.meshgrid(np.arange(src_h), np.arange(src_w), indexing='ij')
        coords = np.stack([xx.ravel(), yy.ravel(), np.ones(src_h * src_w)])
        dst = M @ coords
        xd = np.round(dst[0]).astype(int)
        yd = np.round(dst[1]).astype(int)
        mask = (xd >= 0) & (xd < dst_w) & (yd >= 0) & (yd < dst_h)
        img_out[yd[mask], xd[mask]] = img[yy.ravel()[mask], xx.ravel()[mask]]
    else:
        M_inv = np.linalg.inv(M)
        yy, xx = np.meshgrid(np.arange(dst_h), np.arange(dst_w), indexing='ij')
        coords = np.stack([xx.ravel(), yy.ravel(), np.ones(dst_h * dst_w)])
        src = M_inv @ coords
        xs = np.round(src[0]).astype(int)
        ys = np.round(src[1]).astype(int)
        mask = (xs >= 0) & (xs < src_w) & (ys >= 0) & (ys < src_h)
        img_out[yy.ravel()[mask], xx.ravel()[mask]] = img[ys[mask], xs[mask]]

    return img_out

print("Aplicando transformações...")

img_escala       = aplicar_transformacao(img_rgb, M_escala, novo_w=w//2, novo_h=h//2)
img_rotacao      = aplicar_transformacao(img_rgb, M_rotacao, novo_w=diag, novo_h=diag)
img_cisalhamento = aplicar_transformacao(img_rgb, M_cisalhamento, novo_w=w + int(0.5*h), novo_h=h)
img_reflexao     = aplicar_transformacao(img_rgb, M_reflexao)
img_projecao     = aplicar_transformacao(img_rgb, M_projecao, novo_w=w, novo_h=h)

print("Gerando figura...")

fig = plt.figure(figsize=(16, 9), facecolor='white')
fig.suptitle(
    "Transformações Lineares em Imagens Digitais – Entrega 2\n"
    "Fonte: matriz_imagem_alimento.csv (Entrega 1)",
    fontsize=13, fontweight='bold'
)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.25)

def plot_img(ax, img, titulo, info, det=None):
    ax.imshow(img)
    ax.set_title(titulo, fontsize=10, fontweight='bold', pad=4)
    det_str = f"  |  det = {det:.2f}" if det is not None else ""
    ax.set_xlabel(info + det_str, fontsize=8, color='#333333')
    ax.set_xticks([])
    ax.set_yticks([])

plot_img(fig.add_subplot(gs[0, 0]), img_rgb,
         "Original (do CSV)", f"{h}×{w} px")
plot_img(fig.add_subplot(gs[0, 1]), img_escala,
         "1. Escalonamento (50%)", "Sx = Sy = 0.5",
         det=np.linalg.det(M_escala))
plot_img(fig.add_subplot(gs[0, 2]), img_rotacao,
         "2. Rotação (45°)", "θ = 45° anti-horário",
         det=np.linalg.det(np.array([[c,-s,0],[s,c,0],[0,0,1]])))
plot_img(fig.add_subplot(gs[1, 0]), img_cisalhamento,
         "3. Cisalhamento (shx=0.5)", "Deforma em paralelogramo",
         det=np.linalg.det(M_cisalhamento))
plot_img(fig.add_subplot(gs[1, 1]), img_reflexao,
         "4. Reflexão Horizontal", "Espelho vertical",
         det=np.linalg.det(M_reflexao))
plot_img(fig.add_subplot(gs[1, 2]), img_projecao,
         "5. Projeção – Colapso Dimensional", "det = 0 → singular",
         det=np.linalg.det(M_projecao))

plt.savefig('transformacoes_lineares.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.show()
print("Figura salva como 'transformacoes_lineares.png'")

