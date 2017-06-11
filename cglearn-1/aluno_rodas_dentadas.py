from math import sin, cos, pi, sqrt
from OpenGL.GL import *
from OpenGL.GLUT import *

# Aqui voce deve definir o corpo desta funcao de modo a incluir as
# transofmacoes, repeticoes, condicionais, etc. necessarias para concluir
# os exercicios.
#
# Pequena referencia rapida das funcoes mais usadas:
#
# - Translacao: glTranslate(dx, dy, dz)
#
# - Rotacao: glRotate(angle, axis_x, axis_y, axis_z)
#
# - Escala: glScale(sx, sy, sz)
#
# - Espelhamento: Usar escala com fator de -1.0 no eixo em relacao ao qual a
#   escala deve ocorrer
#
# - Salvar transformacao atual: glPushMatrix()
#
# - Recuperar ultima transformacao salva: glPopMatrix()

tempo_anterior = 0
tempo_agora = 0
dt = 0

rotacao_verde = 0.0
rotacao_laranja = 0.0
rotacao_vermelha = 0.0
rotacao_azul = 0.0

velocidade_verde = 0.0
velocidade_laranja = 0.0
velocidade_vermelha = 0.0
velocidade_azul = 0.0


def processar_teclado(key):
    global velocidade_azul
    if key == b'a':
        velocidade_azul += 10.0
    elif key == b'd':
        velocidade_azul -= 10.0
    elif key == b' ':
        velocidade_azul = 0.0


def compor_cena(c):
    global tempo_anterior
    global tempo_agora
    global dt

    global rotacao_verde
    global rotacao_laranja
    global rotacao_vermelha
    global rotacao_azul

    global velocidade_verde
    global velocidade_laranja
    global velocidade_vermelha
    global velocidade_azul

    velocidade_laranja = velocidade_azul
    velocidade_vermelha = velocidade_azul * 0.5
    velocidade_verde = velocidade_laranja * 3.0

    tempo_agora = glutGet(GLUT_ELAPSED_TIME)/1000
    dt = (tempo_agora - tempo_anterior)
    tempo_anterior = tempo_agora

    rotacao_azul = rotacao_azul + dt * velocidade_azul
    rotacao_laranja = rotacao_laranja + dt * velocidade_laranja
    rotacao_vermelha = rotacao_vermelha + dt * velocidade_vermelha
    rotacao_verde = rotacao_verde + dt * velocidade_verde




    #Peça r1-12 (azul) é a peça-guia;
    glPushMatrix()
    glRotate(rotacao_azul, 0, 0, 1)
    glRotate(15, 0, 0, 1)
    c.draw("r1-12")
    glPopMatrix()

    #Peça r2-24 (vermelha) conectada a 60° com r1-12 (azul);
    glPushMatrix()
    glTranslate(3 * cos(60 * pi / 180), 3 * sin(60 * pi / 180), 0)
    glRotate(-rotacao_vermelha, 0, 0, 1)
    c.draw("r2-24")
    glPopMatrix()
    
    
    #Peça r1-20 (verde) conectada a 150° com r3-60 (laranja).
    glPushMatrix()
    glTranslate(4 * cos(150 * pi / 180), 4 * sin(150 * pi / 180), 0)
    glRotate(-rotacao_verde, 0, 0, 1)
    glRotate(6, 0, 0, 1)
    c.draw("r1-20")
    glPopMatrix()


    #Peça r3-60 (laranja) rodando junto com r1-12 (azul);
    glPushMatrix()
    glRotate(rotacao_laranja, 0, 0, 1)
    glRotate(3, 0, 0, 1)
    c.draw("r3-60")
    glPopMatrix()
