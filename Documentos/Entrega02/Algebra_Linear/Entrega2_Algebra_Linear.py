
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


img_bgr = cv2.imread('Arroz.jpg')
if img_bgr is None:
    raise FileNotFoundError(
        "Imagem 'Arroz.jpg' não encontrada. "
        "Coloque-a na mesma pasta deste script."
    )

img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
h, w, _ = img_rgb.shape
print(f"Imagem carregada: {h}x{w} pixels")


Sx, Sy = 0.5, 0.5
M_escala = np.array([
    [Sx,  0,  0],
    [ 0, Sy,  0],
    [ 0,  0,  1]
], dtype=np.float64)

print("\nMatriz de Escalonamento (Sx=0.5, Sy=0.5):")
print(M_escala)


theta = np.radians(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
M_rotacao = np.array([
    [ cos_t, -sin_t, 0],
    [ sin_t,  cos_t, 0],
    [  0,      0,    1]
], dtype=np.float64)

print("\nMatriz de Rotação (θ=45°):")
print(np.round(M_rotacao, 4))


shx = 0.5
M_cisalhamento = np.array([
    [1, shx, 0],
    [0,  1,  0],
    [0,  0,  1]
], dtype=np.float64)

print("\nMatriz de Cisalhamento (shx=0.5):")
print(M_cisalhamento)


M_reflexao = np.array([
    [-1,  0, w - 1],
    [ 0,  1,  0   ],
    [ 0,  0,  1   ]
], dtype=np.float64)

print("\nMatriz de Reflexão Horizontal:")
print(M_reflexao)


M_projecao = np.array([
    [1, 0, 0],
    [0, 0, 0],
    [0, 0, 1]
], dtype=np.float64)

print("\nMatriz de Projeção (colapso dimensional):")
print(M_projecao)


def aplicar_transformacao(img, M, novo_w=None, novo_h=None):
    """
    Aplica uma transformação linear 3x3 (coordenadas homogêneas)
    a uma imagem usando mapeamento inverso.

    Parâmetros
    ----------
    img   : ndarray (H, W, 3) – imagem RGB de entrada
    M     : ndarray (3, 3)    – matriz de transformação
    novo_w, novo_h : dimensões da imagem de saída (opcional)

    Retorna
    -------
    img_out : ndarray – imagem transformada
    """
    src_h, src_w = img.shape[:2]
    dst_h = novo_h if novo_h else src_h
    dst_w = novo_w if novo_w else src_w

    
    det = np.linalg.det(M)
    if abs(det) < 1e-10:
        img_out = np.zeros((dst_h, dst_w, 3), dtype=np.uint8)
        yy, xx = np.meshgrid(np.arange(src_h), np.arange(src_w), indexing='ij')
        coords_src = np.stack([xx.ravel(), yy.ravel(), np.ones(src_h * src_w)])
        coords_dst = M @ coords_src
        x_dst = np.round(coords_dst[0]).astype(int)
        y_dst = np.round(coords_dst[1]).astype(int)
        mask = (x_dst >= 0) & (x_dst < dst_w) & (y_dst >= 0) & (y_dst < dst_h)
        img_out[y_dst[mask], x_dst[mask]] = img[yy.ravel()[mask], xx.ravel()[mask]]
        return img_out

    
    M_inv = np.linalg.inv(M)
    img_out = np.zeros((dst_h, dst_w, 3), dtype=np.uint8)

    yy_dst, xx_dst = np.meshgrid(np.arange(dst_h), np.arange(dst_w), indexing='ij')
    coords_dst = np.stack([xx_dst.ravel(), yy_dst.ravel(), np.ones(dst_h * dst_w)])

    coords_src = M_inv @ coords_dst
    x_src = np.round(coords_src[0]).astype(int)
    y_src = np.round(coords_src[1]).astype(int)

    mask = (x_src >= 0) & (x_src < src_w) & (y_src >= 0) & (y_src < src_h)
    img_out[yy_dst.ravel()[mask], xx_dst.ravel()[mask]] = img[y_src[mask], x_src[mask]]
    return img_out




print("\nAplicando transformações...")

img_escala = aplicar_transformacao(img_rgb, M_escala, novo_w=w//2, novo_h=h//2)
print("  ✔ Escalonamento concluído")

diag = int(np.ceil(np.sqrt(w**2 + h**2)))
cx, cy = w / 2, h / 2
M_rot_centrada = np.array([
    [ cos_t, -sin_t, -cx * cos_t + cy * sin_t + diag / 2],
    [ sin_t,  cos_t, -cx * sin_t - cy * cos_t + diag / 2],
    [  0,      0,     1]
], dtype=np.float64)
img_rotacao = aplicar_transformacao(img_rgb, M_rot_centrada, novo_w=diag, novo_h=diag)
print("  ✔ Rotação concluída")

extra = int(shx * h)
M_cis_adj = np.copy(M_cisalhamento)
img_cisalhamento = aplicar_transformacao(img_rgb, M_cis_adj, novo_w=w + extra, novo_h=h)
print("  ✔ Cisalhamento concluído")

img_reflexao = aplicar_transformacao(img_rgb, M_reflexao)
print("  ✔ Reflexão concluída")

img_projecao = aplicar_transformacao(img_rgb, M_projecao, novo_w=w, novo_h=h)
print("  ✔ Projeção (colapso) concluída")


fig = plt.figure(figsize=(18, 12))
fig.suptitle(
    "Entrega 2 – Transformações Lineares em Imagens Digitais\n"
    "Projeto Lideranças Empáticas (LE) – FECAP 2026",
    fontsize=15, fontweight='bold'
)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.3)

def plot_img(ax, img, titulo, subtitulo, det=None):
    ax.imshow(img)
    ax.set_title(titulo, fontsize=11, fontweight='bold')
    det_str = f"\ndet(M) = {det:.4f}" if det is not None else ""
    ax.set_xlabel(subtitulo + det_str, fontsize=8)
    ax.set_xticks([])
    ax.set_yticks([])

ax0 = fig.add_subplot(gs[0, 0])
plot_img(ax0, img_rgb, "Original",
         f"Dimensões: {h}×{w} px")

ax1 = fig.add_subplot(gs[0, 1])
plot_img(ax1, img_escala, "1. Escalonamento (50%)",
         "Sx=0.5, Sy=0.5\nReduz coordenadas à metade",
         det=np.linalg.det(M_escala))

ax2 = fig.add_subplot(gs[0, 2])
plot_img(ax2, img_rotacao, "2. Rotação (45°)",
         "θ=45° anti-horário\nPreserva distâncias e ângulos",
         det=np.linalg.det(M_rotacao))

ax3 = fig.add_subplot(gs[1, 0])
plot_img(ax3, img_cisalhamento, "3. Cisalhamento (shx=0.5)",
         "Desloca colunas proporcionalmente à linha\nDeforma sem alterar área",
         det=np.linalg.det(M_cisalhamento))

ax4 = fig.add_subplot(gs[1, 1])
plot_img(ax4, img_reflexao, "4. Reflexão Horizontal",
         "Espelha em torno do eixo vertical central\ndet(M) = −1",
         det=np.linalg.det(M_reflexao))

ax5 = fig.add_subplot(gs[1, 2])
plot_img(ax5, img_projecao, "5. Projeção – Colapso Dimensional",
         "Projeta todos os pixels em y=0\ndet(M) = 0 → não invertível",
         det=np.linalg.det(M_projecao))

plt.savefig('transformacoes_lineares_comparativo.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nFigura salva como 'transformacoes_lineares_comparativo.png'")

