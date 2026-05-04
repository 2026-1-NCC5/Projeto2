# ============================================================
# Entrega 2 – Álgebra Linear, Vetores e Geometria Analítica
# Aplicação de Transformações Lineares em Imagens Digitais
# Projeto: Lideranças Empáticas – Scanner AI
# FECAP – 5º Semestre – 2026
# ============================================================
# Integrantes:
#   Antonio Petri de Moraes Soares de Moura e Oliveira
#   Leonardo Santos da Silva
#   Lucas de Lima Gutierrez
#   Vitor Kenzo Kanashiro
# ============================================================

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ============================================================
# 0. CARREGAMENTO DA IMAGEM BASE (mesma da Entrega 1)
# ============================================================

img_bgr = cv2.imread('Arroz.jpg')
if img_bgr is None:
    raise FileNotFoundError(
        "Imagem 'Arroz.jpg' não encontrada. "
        "Coloque-a na mesma pasta deste script."
    )

img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
h, w, _ = img_rgb.shape
print(f"Imagem carregada: {h}x{w} pixels")

# ============================================================
# 1. DEFINIÇÃO DAS MATRIZES DE TRANSFORMAÇÃO
# ============================================================
# Todas as transformações são aplicadas em coordenadas
# homogêneas [x, y, 1]^T usando matrizes 3x3, o que permite
# combinar transformações lineares e translações num único
# produto matricial.

# --- 1.1 Escalonamento (Scaling) ---
# Sx e Sy são os fatores de escala nos eixos X e Y.
# Sx=0.5 e Sy=0.5 reduz a imagem à metade.
#
#   M_escala = | Sx  0   0 |
#              |  0  Sy  0 |
#              |  0   0  1 |

Sx, Sy = 0.5, 0.5
M_escala = np.array([
    [Sx,  0,  0],
    [ 0, Sy,  0],
    [ 0,  0,  1]
], dtype=np.float64)

print("\nMatriz de Escalonamento (Sx=0.5, Sy=0.5):")
print(M_escala)

# --- 1.2 Rotação (Rotation) ---
# θ = 45° no sentido anti-horário.
# A matriz de rotação preserva distâncias e ângulos
# (transformação ortogonal / isometria).
#
#   M_rot = | cos θ  -sin θ   0 |
#           | sin θ   cos θ   0 |
#           |  0       0      1 |

theta = np.radians(45)
cos_t, sin_t = np.cos(theta), np.sin(theta)
M_rotacao = np.array([
    [ cos_t, -sin_t, 0],
    [ sin_t,  cos_t, 0],
    [  0,      0,    1]
], dtype=np.float64)

print("\nMatriz de Rotação (θ=45°):")
print(np.round(M_rotacao, 4))

# --- 1.3 Cisalhamento (Shear) ---
# Deforma a imagem ao longo do eixo X em função de Y.
# shx=0.5 desloca cada linha proporcionalmente à sua altura.
#
#   M_cis = | 1  shx  0 |
#           | 0   1   0 |
#           | 0   0   1 |

shx = 0.5
M_cisalhamento = np.array([
    [1, shx, 0],
    [0,  1,  0],
    [0,  0,  1]
], dtype=np.float64)

print("\nMatriz de Cisalhamento (shx=0.5):")
print(M_cisalhamento)

# --- 1.4 Reflexão Horizontal (Flip) ---
# Inverte o eixo X, criando um espelho horizontal.
# det(M) = -1 → transforma orientação (não preserva handedness).
#
#   M_refl = | -1  0  w-1 |
#            |  0  1   0  |
#            |  0  0   1  |

M_reflexao = np.array([
    [-1,  0, w - 1],
    [ 0,  1,  0   ],
    [ 0,  0,  1   ]
], dtype=np.float64)

print("\nMatriz de Reflexão Horizontal:")
print(M_reflexao)

# --- 1.5 Projeção / Colapso Dimensional ---
# Remove completamente o canal Y (projeta tudo na linha y=0).
# det(M) = 0 → transformação singular, perda de dimensão.
# Demonstra que nem toda transformação linear é invertível.
#
#   M_proj = | 1  0  0 |
#            | 0  0  0 |
#            | 0  0  1 |

M_projecao = np.array([
    [1, 0, 0],
    [0, 0, 0],
    [0, 0, 1]
], dtype=np.float64)

print("\nMatriz de Projeção (colapso dimensional):")
print(M_projecao)

# ============================================================
# 2. FUNÇÃO AUXILIAR PARA APLICAR TRANSFORMAÇÕES
# ============================================================
# Estratégia: mapeamento inverso (backward mapping).
# Para cada pixel (x_dst, y_dst) da imagem de destino,
# calcula-se a posição original usando a matriz inversa.
# Isso evita buracos na imagem resultante.

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

    # Verificar se a matriz é invertível (det != 0)
    det = np.linalg.det(M)
    if abs(det) < 1e-10:
        # Transformação singular: aplicar diretamente (colapso)
        img_out = np.zeros((dst_h, dst_w, 3), dtype=np.uint8)
        yy, xx = np.meshgrid(np.arange(src_h), np.arange(src_w), indexing='ij')
        coords_src = np.stack([xx.ravel(), yy.ravel(), np.ones(src_h * src_w)])
        coords_dst = M @ coords_src
        x_dst = np.round(coords_dst[0]).astype(int)
        y_dst = np.round(coords_dst[1]).astype(int)
        mask = (x_dst >= 0) & (x_dst < dst_w) & (y_dst >= 0) & (y_dst < dst_h)
        img_out[y_dst[mask], x_dst[mask]] = img[yy.ravel()[mask], xx.ravel()[mask]]
        return img_out

    # Mapeamento inverso para transformações invertíveis
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


# ============================================================
# 3. APLICAÇÃO DAS TRANSFORMAÇÕES
# ============================================================

print("\nAplicando transformações...")

# 3.1 Escalonamento – imagem menor (50%)
img_escala = aplicar_transformacao(img_rgb, M_escala, novo_w=w//2, novo_h=h//2)
print("  ✔ Escalonamento concluído")

# 3.2 Rotação 45° – canvas maior para não cortar a imagem
diag = int(np.ceil(np.sqrt(w**2 + h**2)))
# Ajusta a matriz de rotação para centralizar no canvas
cx, cy = w / 2, h / 2
M_rot_centrada = np.array([
    [ cos_t, -sin_t, -cx * cos_t + cy * sin_t + diag / 2],
    [ sin_t,  cos_t, -cx * sin_t - cy * cos_t + diag / 2],
    [  0,      0,     1]
], dtype=np.float64)
img_rotacao = aplicar_transformacao(img_rgb, M_rot_centrada, novo_w=diag, novo_h=diag)
print("  ✔ Rotação concluída")

# 3.3 Cisalhamento – canvas maior para acomodar o deslocamento
extra = int(shx * h)
M_cis_adj = np.copy(M_cisalhamento)
img_cisalhamento = aplicar_transformacao(img_rgb, M_cis_adj, novo_w=w + extra, novo_h=h)
print("  ✔ Cisalhamento concluído")

# 3.4 Reflexão horizontal
img_reflexao = aplicar_transformacao(img_rgb, M_reflexao)
print("  ✔ Reflexão concluída")

# 3.5 Projeção / colapso dimensional
img_projecao = aplicar_transformacao(img_rgb, M_projecao, novo_w=w, novo_h=h)
print("  ✔ Projeção (colapso) concluída")

# ============================================================
# 4. VISUALIZAÇÃO COMPARATIVA
# ============================================================

fig = plt.figure(figsize=(18, 12))
fig.suptitle(
    "Entrega 2 – Transformações Lineares em Imagens Digitais\n"
    "Projeto Lideranças Empáticas (LE) – FECAP 2026",
    fontsize=15, fontweight='bold'
)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.3)

# Helper para exibir imagem + info
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

# ============================================================
# 5. ANÁLISE CONCEITUAL DAS TRANSFORMAÇÕES
# ============================================================

print("""
============================================================
ANÁLISE CONCEITUAL – TRANSFORMAÇÕES LINEARES
============================================================

1. ESCALONAMENTO (det = 0.25)
   - A matriz multiplica as coordenadas por fatores Sx e Sy.
   - det(M) = Sx × Sy = 0.25 → o espaço é comprimido a 25%
     da área original.
   - Preserva paralelismo e proporções internas da figura.
   - Autovalores: Sx e Sy (eixos x e y são autovetores).

2. ROTAÇÃO (det ≈ 1.0)
   - Matriz ortogonal: M^T = M^{-1}, logo det = ±1.
   - Preserva norma (distâncias) e produto interno (ângulos).
   - Não altera a forma da figura, apenas sua orientação.
   - Autovalores complexos: e^{±iθ} → sem direções fixas reais.

3. CISALHAMENTO (det = 1.0)
   - Desloca pontos paralelamente a um eixo em proporção
     à sua distância do outro eixo.
   - det = 1 → preserva área, mas altera forma e ângulos.
   - Converte retângulos em paralelogramos.
   - Autovalor duplo = 1, mas apenas 1 autovetor real.

4. REFLEXÃO (det = −1)
   - Inverte a orientação do espaço (troca "mão" da figura).
   - det = −1 indica inversão de orientação.
   - É uma isometria (preserva distâncias), tal como a rotação.
   - Autovalores: +1 (eixo fixo) e −1 (eixo invertido).

5. PROJEÇÃO / COLAPSO DIMENSIONAL (det = 0)
   - det(M) = 0 → matriz singular, não invertível.
   - O núcleo (kernel) tem dimensão 1: toda a linha y é
     mapeada para y = 0. Informação irrecuperável.
   - Reduz o espaço R² para R¹ (colapso dimensional).
   - Demonstra que transformações lineares podem ser
     destrutivas em termos de informação.

CONCLUSÃO
---------
A escolha da matriz determina completamente o comportamento
geométrico da imagem. Matrizes com det ≠ 0 são invertíveis
e preservam (ou escalam) o espaço. Quando det = 0, a
transformação é singular e provoca perda irreversível de
informação — o espaço "colapsa" para uma dimensão menor.
Álgebra Linear é a linguagem que formaliza essas operações
e sustenta toda a computação gráfica e o processamento
de imagens em IA e Visão Computacional.
============================================================
""")
