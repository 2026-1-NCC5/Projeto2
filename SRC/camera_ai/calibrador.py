"""
Utilitário de calibração de câmera — gera pontos para classificação por tamanho.
Posicione um quadrado/retângulo de medida conhecida na esteira e execute este script.
Os pontos gerados devem ser adicionados ao campo "calibracao" do camera_config.json.
"""

import cv2
import json
import os
import numpy as np

pontos_clicados = []
imagem_exibicao = None


def capturar_clique(evento, x, y, flags, param):
    global pontos_clicados, imagem_exibicao
    if evento == cv2.EVENT_LBUTTONDOWN:
        if len(pontos_clicados) < 4:
            pontos_clicados.append([x, y])
            numero = len(pontos_clicados)
            print(f"Ponto {numero} registrado: (X: {x}, Y: {y})")
            cv2.circle(imagem_exibicao, (x, y), 6, (0, 0, 255), -1)
            cv2.putText(imagem_exibicao, str(numero), (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Calibrador de Camera", imagem_exibicao)


def executar_calibracao(indice_camera: int = 0, tamanho_cm: float = 50.0):
    global imagem_exibicao

    print(f"Acessando câmera (Índice {indice_camera})... Aguarde.")
    camera = cv2.VideoCapture(indice_camera)

    for _ in range(10):
        sucesso, frame = camera.read()

    camera.release()

    if not sucesso:
        print("ERRO: Não foi possível capturar imagem da câmera.")
        return None

    imagem_exibicao = frame.copy()

    print("\n" + "=" * 55)
    print("INSTRUÇÕES DE CALIBRAÇÃO:")
    print(f"  Referência: quadrado de {tamanho_cm}cm x {tamanho_cm}cm")
    print("  Clique nos 4 cantos na ordem:")
    print("    1º Canto Superior Esquerdo")
    print("    2º Canto Superior Direito")
    print("    3º Canto Inferior Direito")
    print("    4º Canto Inferior Esquerdo")
    print("  Após 4 cliques pressione ENTER ou ESPAÇO para finalizar.")
    print("=" * 55 + "\n")

    cv2.imshow("Calibrador de Camera", imagem_exibicao)
    cv2.setMouseCallback("Calibrador de Camera", capturar_clique)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return pontos_clicados


def main():
    INDICE_CAMERA = 0
    TAMANHO_CM = 30.0

    pontos = executar_calibracao(indice_camera=INDICE_CAMERA, tamanho_cm=TAMANHO_CM)

    print("\n" + "=" * 55)
    print("RESULTADO DA CALIBRAÇÃO")
    print("=" * 55)

    if not pontos or len(pontos) != 4:
        print("[ERRO] Calibração incompleta — clique exatamente em 4 pontos.")
        return

    pontos_cm = [
        [0, 0],
        [TAMANHO_CM, 0],
        [TAMANHO_CM, TAMANHO_CM],
        [0, TAMANHO_CM],
    ]

    calibracao = {
        "pontos_pixel": pontos,
        "pontos_cm": pontos_cm,
    }

    print(f"\nPontos pixel:  {pontos}")
    print(f"Pontos cm:     {pontos_cm}")

    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_config.json")
    try:
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["calibracao"] = calibracao
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        print(f"\n[✓] Calibração salva em: {cfg_path}")
    except Exception as e:
        print(f"\n[!] Não foi possível salvar no config: {e}")
        print("Cole manualmente no camera_config.json:")
        print(json.dumps({"calibracao": calibracao}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
