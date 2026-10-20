import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import calendar
import os
import base64

# Imagem da Logo Vetorial da Chammas Engenharia Convertida em Base64 Embutida
LOGO_EMBEDDED_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAARUAAAC8CAYAAACiC1KkAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHkyc1urAAATm0lEQVR42u3de7DdV10H8O+5ufeR3CR33pA3eSRpSBoabS210I7aDkU6A1Mdi450Bsa2M/4RHR0f42vG4SodX1v/8I/O+MroOO34mI4IikynrS1S20JLS5s2SZo0Iblp8ia5ueee3/423Xvu3Ie953LO3fvx+cxkMsnNPfec3/ns/d3f7/fbd2aEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgghhBCibY3sApD8eutb3/r1m2666eeLxeL39fX1fX1S/6u6u/v39Pf339Tf3/3j3Xfddf4Xf/EXH3IqI+k2sglA4Xj00Uf/5PDhx2/p7i4+29vX+3xvb994b1/f2/r6eif6+vv29PT0p/Xf6f6d/j6tL13u2t3X90x3d+/2vv7C13/yJ3/6v9///vd//f/4/3/1q1/9yT333PNoR4e/J4i0E0I4G2/8zGf+eXx84ut9ff1ndXf3f6v/X39/f96p3R25fX8A3S6/f03/4f5f+/r7/u31r3vdk5e//OU/100S7/Mv/f2nfsO/I4i2x/098s/+/p5vTExMPNvX13da//vE4s9x8SffX+m4/13939//8X19vf/W3dP9O719vX911113PZpU3P11O3k/I033L//yL5955JFHruvt6flm3fS1O+vO9m63E4y49b1/XN7R84p6968f4I/rf1x+fG3v3/t/f+f1yUa30/r7vvfT/7T3XzN3q+/73s1U3/+1I/xO94f1E/m5/f19f18s/ufOnf3eN77x2M++/OUvX2s4JmE3oIu1m319fT+q/8mvd+31O/fF42H9vXG7f86t3S3G8q/Xp48f1v99O9/H2v/943v80O0c/kM73s/sdrwX+7+f0+t+4/m9f3+l//sf7e/v+329v33qT//0m395sSME3XnnneP33HP3kZ31H3p98I/E9sPq3vO3S/z/047/a3m9e2x3x4m4/f8/lR//S3m89X344qHffxze8bL/eCq3s9fbf2x4LrfzeHf3v99d19fX+yXdL53u7e39f323+/f5/LcfunvvvdcvE0L48vX/ySefvKWvL/v365S+/J93/P0N7532I/v/xN3u23/8uX1//z++4f/8431//rV3vD658fUfvu3d/3fE/f98x3u7m//4G9/f/mO0A/+x2194x6P+8f343t2/53j39o4v/v/y+P/++P/2H4f7f6+/c44ff3z//+z7j9v9O34Ivd3dfd+f348/92/+zT975eXPf/5qX/8QInS1N/pE8VevmB+sA2v/792/e4L/R++I31Lfvf3/v73r9Tf8/fKx4f/8H972eO2P0f5/eMf7fuvP2f9sN/3NfX8X/O/1XetvLpP//dC2u+66a3znzp0X63+/S/94e2v//r+/v9s//qf6eLd/n3d8p4/v9I93/Nf+yS7/8aV9eN3O121Xf/92t8tO/e6T3f2dd/3H7/G4tX/+/dvdLv/pTr/1x++yL10u233Xf34/Dvf///p3u8u7Xf7fA/x/42P3f0f7f4O4Xbbbf2z699kFf5z+cfl/b3a7v/e5+m73A/pE/A921d+4881vfvN5A4aO7IeL/G3e8M3y84M/jF73Tj/c9i2vD/oP+9j48bfz/s5+t2/fXv4L+f0d/j6A3r9/c4c/Hut3vB+/5/yv+5XfO/+w0f/63X2v/eI3v/kRwwO3/92/++2e/L3/3Pj/b2f/2X/o0y121fXvcf6x9Yc56L0vP83+v4vf59t//q6/O+k9vuv73/y9r/d/X/f5o0sP6A+8v2z88M1v/9v/u/9XfvXvL37xi1/3u/Tz7fT0/H1eL1eG+t+5eG3X/4dOqC3E4/fOxf9O/5N+t3b3/93yI+7f26nfl/3s45v+05/s1j/N6Z00t3NlT99//d1f/2LXX3zpS3//S1/60sX3ve994//4j/94Qv92aX9/X2p8vNjtXz82sT4Xf7Bf/7O//g5f5/L3vv7f+23/1v4vH9v5+9ve9tE9/bN9fD3X+4mXfvd3//gP//y/H45qXv6f+v+8f3+n/3/9Tf3P/v/o9n0L587d+Oabb77u4f9/aedPf/p3/v4r//p9v//7f/Azn/2v2x/++O83/v+vvft/fPv2L4X1+8d1fW3jS+939O2Xf/44vL+9233xO/+93z/1s45749fefetPv+HtvP3wbfX40/A+v/p+/9/6P2T8b+zveC+u8Qfev+P3e8Mfv3/Xv+O94+93/4/x+Lvdz3v1pbf/2K5v7v2/882e3v/e//3tU3vf+ebvff2pP3p660svvPDy3L/aX/2jT208+7FPv/a5f/j7f3v31+O6vvaE/4/O/R+/8z23d/p/21/P9fXF/29fXv//+u3u44vv/Pff+/5/e3P+tve1/7u//c3e//M3m44I/s63ffj3/++3/O4/3Pb6973eO77D38vH43T99+vO3v6a//0vf+j94/9f/Xvf+P7/8fXvP3mIe1/+m9//e7/471//nS/84ze/53b+32/+h22v+pvd3/vDkze9/P7/vP7/eO37X9s1f/c0H5/s6S+935N//D/e8faL3/mJ/+/jN7+vO4T5q3//u3/+e//yH4///S83XvyjP/z8Z7/8xS96/et3xZ3f/NZnPv3S//z2E//y93+1/63/6/L/feff3Pr69/v2L9/u233XN/7pT/70r/7f9/2x/29f+sV/fcfX/99f1I/15U+/ev1p3//iL3/2C1/sXjS5c2L8d//5e2v4qf+66Z1v+i6//+A/mX4I/Wv+fR3/+7/1x9f884fve30Yf2/++s+/5779p/3b/bX3feN1a18/e1s/v3t/d/z7r/n47A13vvz+W+O+v3G47+39733N+mN3f+0f/+4fPfbw3/7lX4qnn356q/6sXn9dG3fvnr7Y09O9f2f8xO1v/mKvv//v1e5fI9//8/vf/98e/uP3/dffedtbv/kH31/Z421v+/fef3z0X3/2m1f8D+/8e294+Xfe/o3f3fX9j/v86i+/5463f/c3Xv6Xf+A3vOHf/e/3v/13f//G/7iP/3S/P07vf2/a3v5I3Xf28bvvvXf/O+/e4e2/vPve28//7i233vr3f+0e73f0vXe83/G26O2M+f/63Xm/e+t/58s//X/e+G+/8yff+Y2f/Y0f+rUffO29/3v5//+f+/2Nf+ff/8fX83fLd//9b14f4/A89O7767/92bvf/o2v31j+mvd6X+3/0A+//fE7/bH/eK7S//7Wv//xze/9P9/x2l++/Xvfc+sbr7nr5v1vfeev/f937tzf8I959/3z+1f/r6s/evc3nv3/X/sff4/+/iH0f8Svf3p/n6+3+I95v4/+0xvu/Ivv3L5/rO9Ie2d/x49+9M79L23/5qff8eS3XvvQfS/v+x7s8Xfe9fA7L8bj+L9b3+m9f/+15/aO11/b3/veO/3i//+j/fXvf8/7bv/6N1+/3X33mO3q2P/64s/d85ffefKNP/G2z5//+Y4/+43feXz8pZe+1dPTvdA73L+343vf2f10d/mB2fC3+v137Lp3ftX38T2v2P4/3P/f4v7O3u/f8q4/2m393x/8I9/fP/6nef2m/a//5A/dO817vK4fP9y3e/x1Xy//2jvev3b/195/X3/nnT9392e/+fC33vO+933x3e/60GNP//2f/89fvv/X/+/sH8X+/pIu31zve2jvdP+O//f//e4/d3f78Xm/d98ffP/0H4f78/x++O/2l97f3v32L93+4a93++9x2u/f6fe//U//w2d4X7/26m4x+s+6/Svhv+l36Ivf5/N7+9//N3m/30vvffIbb/v6J5/qH5/79O5v/46f3I/T3m8/+3aI0Lp++L3fe0f+98q3f/Lw3/X/3//x4344v2t/y++P1L3n+74z2v35Xf373/3fO4a/+qvvf/W9X/f2334fH7v95963f4y+zvt95G5//v3+v37190f+/jvd5/2f/JnvO/aG07yvI//0xnv9x01f8n+/r6//691++v2P//h23//+463b7e71f/++9m/s7a+2v+F29/PZf3y73b/x/kO2/8f42m7vv337373f//jX2933L37xT9x94f+87Yf+8M27X/f/33X7l344t/53u3+P/99/3vEft/tz2f/jefT71e223/s3vv4u/3m/4+e1f0e2+/vYv//uN3i3f49v173b22/f3n82fvj2n3O3y07f3/9/v/2Pf/n+t/3P9x333/086e/veaK42/9oO91vf+/4vve4317+4++p47294x6P/y6e37vfb3ffv46P4f9+e3vfcfx/99f1Xf75m76/t30/I3b8ePzX35H3X/m3/vDtvf3m5fL4bvd3/z93f8e53X92u9v2fv/vX/30/f0sve5P3vI2/963//L/G4fne9+v3v+Jp7/59E/e9tMf/+Gf+oFf++xnP3tt09/XoUOH4syZM3Hp0qX483/1p/55qTf/u/mIvrT8y2/2yq/1f7L82N302vLj4e3+sfnf7Ovr/pvu43v7e3uX/vnevd3dH3x4X193eU198uA53/ve944d/Z8///Mnnnv+y3X/3UII0d15442v/vbd/3C3P9a6s73/60L6+/tvdH+X//zXj/UdL+/0eMf1sfrvj+Mbf4/H3//xRjffHj5++A6fG19X7sD6uI7t23X4S699z5v33//u31xYftz4x3/e+eBf/I0fvT4y6m+G+H8PHz4cp599/u3jY3vO3fLgLz5+u3v8/X1/6O+u/2Mev0aI0NrL239855vf/L73+Yd1/+/u+E7/vO7y1vI/Lz32fL28Xun364/V3+f4oNvf/ePtPxbH8f+S413+8m+v37+38XG210/2pG/k59/3z6/v49f39m74H2O62L/e3X02f37/s8ffuK/e3e/4Ift691y/uX/4S+/c39/38O7y3e36o3b7X/d/Xf/P+vvL+/vA+p8vvdv/eO6t6z/p63H5/D9b/+/79n1y43+/d+7c/t4XvvCF34zQ1XnzzTfH66/d++P/9X/88N92+1f+3pL83v3jXvKvdv728uO/3T+/2+P//Y93e+v2//e/e3s7Ptfj2/f/31e8v93teO/3n3u33fG9u+3/6L/++6t33XnHzvjInfe9049/23vf5A1i9J9m/5f448x33nF3PPyrt39vv/v/N79+68d2u/+/y30vvuS4138e/v12f4x/b8dLvfe5u9vb8aXf9zbfSbd7vL4/S4+3fV87X/ff33s33nb4u5/p6+/5q/29vX+34/j99/9199/i5/78z6/s85f+O3eOf/Nfvv61Xz4//A843S634e/+f3rve4f4/A83e3u8/3a6e9bfrd7tT/r3I11E731//Jb6/O7/m+/f0b6e4vX529s33u//bXdf9xvdX7d/fK27/b13S3c/9f7e53f193f5/eX53u9e992X3vH+991/x7vf8zNfefL7/s51/65v4G/fS59+8ltv+7k3vvu9b/v4x373V//Jrbfeevq3fu1/+O10+I++v7e0eE+fS1///Iu/+rI3/423f++bb3vD3fvufeCBO6+O0FXnL1269s/8L3ffc+edp44efeu5xsbG09XvGj1//vy3X//gL76k/K92x/veS9334x1X/+3f9sUvfPEX+/v7j/f29p3U/38yO3517LXXv36it+f6Yw8+ePz6++8fv3H4oX6L6/5A/9+d9bf+f6m4+f80Nzf/5Y8cOvTL7s/v+f1i8dP958/89f2/+5nP6m/5/m4X/T08mI+/X/Gbfm0333xz33333Xd3x0c/vG+2e1m4P7P1f5pAftIvf2X4m3f9yJ133/X4m//+2+946vHHf3vL34b1I/p03aT6vX8v9yN3q18/q8e134s/+O33vvT3v6X/qG287/1b/M9u/E+Xf9+a+t3+L//e3/3e970h+sf9T2+55aaLzz33y4O33/ng23d913/75j/7jZ+7a/z+/Tvv+8k3X/S//y/9O6i/l39pX5f/n3bS5S/0/49d945fO//m0e2/1L3/yE6/bX9/+8aX1n75C73Xfdfq45v+8eO7//b/4t323b7+d/sbd8uP/f1/u/23u316Lvf5/2397+r7+w//yZ/f+f/b15P+P732sYfv+sL3fP3f3fX5f/qjf/8//P/v/q1/q+18m7yX+nvl3q63r//428fI2f63uXlq4aGf+alX/uuv+Z/f8qsf2P3fG6X+v/R/r9/f+323f//S9/E/33/c2v+F//34e/T/I3e+/6Xbf+Mbfp++jS/f2d87e/zF664a7q+/pX5433q8o+//Pvd7b2xsvLj3/m9s/P0XXvji9S+/4e96G8m/39XfsfG//L/q4+O3f3v0zU0/mS6yL/3pP/79G/+u744bf83sL/3iR8euf8/brvt6f2fL2S6v43bfe0e+/96/2N7395e+r6vf0/zPjI4//8q//m0/2+e9e/S2X3tXf/f3fe2b/l03eefP73/35i6v++9829vfc9e//Gtf4jO3v9Xf0xfe/+C47j7yP354x3tfp/m146v9mIff+dZvf+N9m23u/r/e89p/6I/d7/0Xf338f2a6G9993U/feP4HvvvGv+i68S/1d/1j+/e9L/X2p9/Qff33+n44mN+/jU3f+d16/cbeI+s/u/7X9vH2j3X7r5P7O1v/4x3vvX3pveD+e3R/L/3074/c/f5/de6jL730248/8siv+3/t37/v1S6yq/yIe+I/fuvlO/3/683/+z3+I3H6t1xS1P7+a9/yXvd2u++O42t5vS/m9aG2+/b465t/57m346f0p+/L7eJvd7d/vX+/D3O3+1P/T/rf0z8+v/X+O7O/vfeO32+/Hq/7e9v/Ue4/iPvv/5vffm/2/f290bX+3d5u+5O65I/x8nbfv9Ofe9/++5x4/L3f8T9+3z3ef+/+sUu83sXj0iO//8AHP/C9776l7tXN4I03vvGOb//E0/fO3D447j9XmPvxR791a/39+v+/G2z5l//w5/49f7v4xS+3r6v+w9/fV7f3b/sP4U3v+K9v81/31b//qT/2nS9821vf1t33B+46uv/97s89Mfj/6X//5k///v4+a//v5b6vX/6x/2P8p+e53d39m9vv+eS1/f2d/t/+/v7tfrlrbx++v+3Xvvf6N6v9320e89Sjf/Wd/1376f4e6v8efX0T3b1f/68jLp/8b3f46f33tTf5vO4v63//Xp9vd//2xS/3j+e5d95//8H3fe5vvP8GvxS8H3N6002v33v34e8M7r2m139/7rzzl28d/CjN7fI33S998pG/6fI/1mO8+41/2P2G+/X41sH/+p//1uG0eS//m765+U/4j/aWv3vXm9/2Aze0/+/P32y77/vf2/2y42/97eW3D3e9/Lq38R/+3+z3vK+/H9bvdC33P3e4983v/O5vd/9m3f/0uO2+7+891v1/x9X/Pvx9eL+f/44v3/y9t/37aXf//G0/66X3fefbf+33ffz8+vL//O//feM9//yvftffGfvv2d6Sbrvttuduf8fbfjB103233/b2u7v8L//e3/v1N/jX/XfL65f2zreO0/7/6s8/5B++6Yl/X//+/mPz9Rvf6H/v3R3/j2e340Xv/mvef94f9S+pS/7vF6/v8/fXv//u5f9u/+9tL/9/N9/63e++6/10+91vfNvfP3/vS9/w5p/+vd++s3//f//vX3/tP9v7/3/I3W/3H8+9d/5f0f3H8+xO/2+8G08/+q/++k///S3D/3j0/y3P+e+vv3u23v/0pP8efjve/Xv9n4/vvS8/v3/4vXfbX3S/73vf4H66vve0//fG//x6d+/x/L+vf8e3v/385/u6f93feXvv/5tue3N33433/67//v4/dPf3D+f23r/1393v/Puv3e0u/7L/bS55vH03X/y+/G0YvP2zL/8x/vKz/9b9776f8Tf29+f1X//z0Hvv/319e/++p30pI/5D/H/3b3c33nv8ff1x9j/e//q1d/z2/e29pL9/+Mvd/3f82P33/fXb6S8P/0/3e/3Xbf/v+v7b4d3L+xG/t7t/u47XvfOvfveve18veX3/8O//+E//2e/c/O/9n39H/y95/Y8TffL23/9f/+Ffve/0dvdv/+N13v/e04fe7u6uOa/mF1/zLff9e4u5+S/+eI/D9z9p/89v7/i4+vH49/Xvfe+u6x3X5f3d4/9f33L//fH+2+1/mN718vve/93D3X6363+fe+/P3fP2L5/x/X+14vf/3e334+/2/Pz+3m9f++mP+j5fL/+G9u/13/t312+n/X35c91L/u+uX/9/75S//5m/f8fbfdff3b3e349++58fe/mN//t/f8bfDq345vLq/48S///L/e/Sdb3nnT544evSjL4w/I332y5/v3fOqG3p0k2/ev+2+/M2/33/+z5fU9u/423X//f+8++sXm2X33/214R1/d3n+S/f3A817fW3353v9sfn5x/6/3fe23d/h43+/7++83s3yfe2M233v+7XfG+5+0e3+6X/+fve3u38u0bH92O/q3x3/A9xud7/a/bftdnuv43q/dve8f331S1/+/C0bX198944Xm35x/Pj4s5f8/o4v1u3sPz4O/36e6O2X7e3/+5//p47/z37jG+m93//E47//fbd32/8f41s73neP+7+99X//99/S3/+/f343ft39M0mK99/9mI/f4wfu9H+fd/p3v/2v28U+/tIev3+/fX5/sL6P/j/eLfv3Ovev3XG323HvfUfP//e/v/+P+/4vvdf7296vfveo+O/2z7//22f5ePxe993+8fT1fXzvbf/7cXxv/3/p/d39feP93feXfvd++fW+4P3f/R+Pz/f/n8u/pvdP4/m98L/r3xnvP9/X/vX5uP++9+P02vf8e1v359s3ft/r//2M91vf53L7u170/t7xL/8/3e52/8f//X//9XfP1+3m3S539/336H/v3e2O3u0eP//+x//v3/+/eH/pXer+/e12t7vxm2/vv/36/T2xP//f/37f8f9Oft/vfPv3v//7X+mO//m59/v+G+p++/r3P9bd+/rA/31/530fv/e/vfz4ff//9vvef387Xne/feOf4u/e4+3v9Mv/A/w9fS3//wEGAE7bS09S22uMAAAAAElFTkSuQmCC"

# Configuração da página
st.set_page_config(
    page_title="Chammas Engenharia - Gestão de Recursos SSMA",
    page_icon="data:image/png;base64," + LOGO_EMBEDDED_BASE64,
    layout="wide"
)

# Estilização CSS Personalizada sem tom cinza no fundo e Cards com Bordas Customizadas
st.markdown("""
<style>
    :root {
        --chammas-burgundy: #5C061C;
        --chammas-orange: #E65100;
        --chammas-bg: #FFFFFF;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Banner do Cabeçalho */
    .main-header {
        background: linear-gradient(135deg, #5C061C 0%, #3D0412 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 10px;
        margin-bottom: 25px;
        border-bottom: 5px solid #E65100;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
        gap: 20px;
    }

    /* Cards de Indicadores com Design Executivo e Bordas Institucionais */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #5C061C;
        border-bottom: 3px solid #E65100;
        border-radius: 10px;
        padding: 18px 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(92, 6, 28, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(92, 6, 28, 0.12);
    }

    .metric-title {
        color: #5C061C;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #E65100;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
    }

    /* Tabela da Matriz Diária */
    .gantt-matrix-container {
        overflow-x: auto;
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    .gantt-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 11px;
        font-family: Arial, sans-serif;
    }

    .gantt-table th, .gantt-table td {
        border: 1px solid #DDD;
        text-align: center;
        padding: 5px 3px;
        white-space: nowrap;
    }

    .gantt-table th.header-month {
        background-color: #5C061C;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-transform: uppercase;
    }

    .gantt-table th.header-day {
        background-color: #FAFAFA;
        color: #333;
        font-weight: bold;
        min-width: 24px;
    }

    .gantt-table td.col-info {
        text-align: left;
        padding-left: 8px;
        padding-right: 8px;
        font-weight: bold;
        background-color: #FFFFFF;
    }

    /* Cores das Células da Matriz */
    .cell-allocated {
        background-color: #2E7D32 !important; /* VERDE (Titular) */
        color: white !important;
        font-weight: bold;
    }

    .cell-substitution {
        background-color: #FBC02D !important; /* AMARELO (Substituto) */
        color: #212121 !important;
        font-weight: bold;
    }

    .cell-vacation {
        background-color: #C62828 !important; /* VERMELHO (Férias) */
        color: white !important;
        font-weight: bold;
    }

    .stButton>button {
        background-color: #E65100;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #BF360C;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS tsts (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS veiculos (id INTEGER PRIMARY KEY AUTOINCREMENT, placa TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS etilometros (id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS projetos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS alocacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projeto TEXT,
                    tst TEXT,
                    veiculo TEXT,
                    etilometro TEXT,
                    data_inicio DATE,
                    data_fim DATE,
                    is_substituicao INTEGER,
                    observacao TEXT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS ferias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tst TEXT,
                    substituto TEXT,
                    data_inicio DATE,
                    data_fim DATE
                )''')
    
    c.execute("SELECT COUNT(*) FROM tsts")
    if c.fetchone()[0] == 0:
        tsts_iniciais = [
            'Aline Alcantara Linhares', 'Cristiano Henrique Resende', 'Daniela Valesca Martins Silva',
            'Deise Cristina Santos Moreira', 'Gustavo Brito Lopes da Silva', 'Helber Alves Silva',
            'James Marques Lacerda', 'João Vitor de Souza', 'Natália Guimarães', 'Pedro Henrique Ferreira Santos',
            'Richardson Bernardo Fernandes', 'Sérgio Felix de Souza', 'Weryks Martins da Silva',
            'Aline Cristina Souza Ferreira', 'Jacqueline Cristina Pinto Barbosa', 'Marcirene Sales Ferreira',
            'Manoel Tagino dos Santos Junior', 'Charles Franklin de Faria', 'Jessica Arlene Beato',
            'Ricardo Duarte Batista', 'Fernanda de Oliveira Santos', 'Wania Marcia De Rezende',
            'Janaina Aparecida dos Santos', 'Vinicius Pinheiro de Oliveira'
        ]
        c.executemany("INSERT INTO tsts (nome) VALUES (?)", [(t,) for t in tsts_iniciais])

    c.execute("SELECT COUNT(*) FROM veiculos")
    if c.fetchone()[0] == 0:
        veiculos_iniciais = [
            'SIB7B06','RUA5H43','SJI8H13','SYJ0J36','TCO9C94','TXY3F21','QMZ1D81','RTF6B55','RUW6A70','TCG3B90',
            'TDT9H59','TDU3E72','TDU3E73','TDU3E74','TDU3E75','TEE4C20','TEE4C33','UDG1J25','TEC6E42','TEE4B95',
            'TEE4C11','TEE4C28','TEE6B91','TXL6B90','TXY7G94','TZF9D38','TEI7D22','TEI7D35','TEI7D36','TES7B26',
            'SYR2J90','TDV9A59','TDW1J44','TEE4C05','TEI7D06','TEI7D18','TEI7D31','TEW0G98','TCK4J56','TDV9A61',
            'TEE4C15','SIX0C67','TDV9A53','TEE4C06','TXS0G24','TEE4C27','TXO0J84','RVT4E66','TDV9A52','TEI7D17',
            'RUT6I73','TDO8H14','TDV9A51','TEI7D34','TEO4G56','TEO4G58','TEO4G59','TXO5I56','SIR0G95','TEE6B90',
            'SYS3J92','TEI7D11','TEI7D20','TEI7D21','TEI7D26','TCE7H36','TCE8G30','TDV9A56','PZA0492','RNT6B86',
            'RUW6B08','RVU9F50','SIF7D10','SYV9F52','TCI8J28','TCT3J87','TDU8I87','TDU8I88','TDU8I89','TDU8I90',
            'TDV9A54','TDV9A57','TDV9A58','TDV9A60','TDW5A05','TEB4C38','TEI7D38','TYV5I62','TZW6H02','UVS4I29'
        ]
        c.executemany("INSERT INTO veiculos (placa) VALUES (?)", [(v,) for v in veiculos_iniciais])

    c.execute("SELECT COUNT(*) FROM etilometros")
    if c.fetchone()[0] == 0:
        etilometros_iniciais = ['18302', '18303', '18304', '18305', '18306', '18307', '19407', '19408']
        c.executemany("INSERT INTO etilometros (codigo) VALUES (?)", [(e,) for e in etilometros_iniciais])

    c.execute("SELECT COUNT(*) FROM projetos")
    if c.fetchone()[0] == 0:
        projetos_iniciais = [
            'Gerdau - 5955', 'Vale Brucutu - 5930', 'Gerdau - 5919', 'Vale Norte - 5426', 
            'St. George - 6874', 'Jaguar - 6132', 'Vale - 6300', 'Vale Itabira - 5907', 
            'Kinross - 5852', 'Vale Água Limpa - 5930', 'CBMM - 6150', 'Gerdau - 6677'
        ]
        c.executemany("INSERT INTO projetos (nome) VALUES (?)", [(p,) for p in projetos_iniciais])

    conn.commit()
    conn.close()

init_db()

def run_query(query):
    conn = sqlite3.connect('chammas_gestao.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def execute_db(query, params=()):
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def verificar_disponibilidade_tst(tst_nome, dt_inicio_str, dt_fim_str):
    conn = sqlite3.connect('chammas_gestao.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT COUNT(*) FROM ferias 
        WHERE tst = ? AND (
            (data_inicio <= ? AND data_fim >= ?) OR
            (data_inicio <= ? AND data_fim >= ?) OR
            (? <= data_inicio AND ? >= data_fim)
        )
    """, (tst_nome, dt_inicio_str, dt_inicio_str, dt_fim_str, dt_fim_str, dt_inicio_str, dt_fim_str))
    em_ferias = c.fetchone()[0] > 0

    c.execute("""
        SELECT COUNT(*) FROM alocacoes 
        WHERE tst = ? AND (
            (data_inicio <= ? AND data_fim >= ?) OR
            (data_inicio <= ? AND data_fim >= ?) OR
            (? <= data_inicio AND ? >= data_fim)
        )
    """, (tst_nome, dt_inicio_str, dt_inicio_str, dt_fim_str, dt_fim_str, dt_inicio_str, dt_fim_str))
    em_alocacao = c.fetchone()[0] > 0

    conn.close()
    return not (em_ferias or em_alocacao)

# Cabeçalho com Logo Vetorial Embutido em Base64
col_header1, col_header2 = st.columns([1, 4])
with col_header1:
    st.markdown(f'<img src="data:image/png;base64,{LOGO_EMBEDDED_BASE64}" style="height: 85px; width: auto; object-fit: contain;">', unsafe_allow_html=True)

with col_header2:
    st.markdown("""
        <div class="main-header">
            <div>
                <h2 style="margin:0; font-size: 1.7rem; font-weight: 800; letter-spacing: 1px;">CHAMMAS ENGENHARIA</h2>
                <p style="margin:0; font-size: 0.95rem; opacity: 0.9; font-weight: 600;">Gestão de Recursos SSMA</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

df_tsts = run_query("SELECT id, nome FROM tsts")['nome'].tolist()
df_veiculos = run_query("SELECT id, placa FROM veiculos")['placa'].tolist()
df_etilometros = run_query("SELECT id, codigo FROM etilometros")['codigo'].tolist()
df_projetos = run_query("SELECT id, nome FROM projetos")['nome'].tolist()

df_alocacoes = run_query("SELECT * FROM alocacoes")
df_ferias = run_query("SELECT * FROM ferias")

# Indicadores em Cards Executivos
col1, col2, col3, col4, col5 = st.columns(5)
total_tsts = len(df_tsts)
tsts_alocados = df_alocacoes['tst'].nunique() if not df_alocacoes.empty else 0
tsts_ferias = df_ferias['tst'].nunique() if not df_ferias.empty else 0
tsts_livres = max(0, total_tsts - (tsts_alocados + tsts_ferias))
tsts_com_veiculo = df_alocacoes[df_alocacoes['veiculo'].notnull() & (df_alocacoes['veiculo'] != '') & (df_alocacoes['veiculo'] != 'Nenhum')]['tst'].nunique() if not df_alocacoes.empty else 0

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total TSTs</div><div class="metric-value">{total_tsts}</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Alocados em Projetos</div><div class="metric-value">{tsts_alocados}</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Em Férias</div><div class="metric-value">{tsts_ferias}</div></div>', unsafe_allow_html=True)

with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sem Alocação</div><div class="metric-value">{tsts_livres}</div></div>', unsafe_allow_html=True)

with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Com Veículo</div><div class="metric-value">{tsts_com_veiculo}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

menu = st.tabs(["📊 Visão Sistêmica", "➕ Nova Alocação", "🌴 Gestão de Férias", "⚙️ Cadastros Base", "📥 Exportar para Power BI"])

# TAB 1: VISÃO SISTÊMICA (GESTÃO DIÁRIA DE RECURSOS HUMANOS)
with menu[0]:
    st.subheader("Gestão diária de Recursos Humanos")
    
    col_d1, col_d2 = st.columns(2)
    dt_inicio_vis = col_d1.date_input("Visualizar Período de:", date.today().replace(day=1))
    dt_fim_vis = col_d2.date_input("Até:", date.today().replace(day=1) + timedelta(days=60))
    
    if dt_inicio_vis <= dt_fim_vis:
        datas_lista = pd.date_range(start=dt_inicio_vis, end=dt_fim_vis)
        
        meses_grupos = {}
        for d in datas_lista:
            chave_mes = d.strftime("%b/%Y").upper()
            meses_grupos[chave_mes] = meses_grupos.get(chave_mes, 0) + 1
            
        html_lines = []
        html_lines.append('<div class="gantt-matrix-container"><table class="gantt-table">')
        
        # Linha 1: Meses
        html_lines.append('<thead><tr><th rowspan="2">Nº</th><th rowspan="2">Colaborador (TST)</th><th rowspan="2">Projeto Atual</th>')
        for m_nome, count_dias in meses_grupos.items():
            html_lines.append(f'<th colspan="{count_dias}" class="header-month">{m_nome}</th>')
        html_lines.append('</tr><tr>')
        
        # Linha 2: Dias
        for d in datas_lista:
            html_lines.append(f'<th class="header-day">{d.day}</th>')
        html_lines.append('</tr></thead><tbody>')
        
        # Preenchimento das Linhas
        for idx, tst_nome in enumerate(df_tsts, start=1):
            aloc_tst = df_alocacoes[df_alocacoes['tst'] == tst_nome] if not df_alocacoes.empty else pd.DataFrame()
            unidade_nome = aloc_tst['projeto'].iloc[-1] if not aloc_tst.empty else "-"
            
            html_lines.append(f'<tr><td>{idx}</td><td class="col-info">{tst_nome}</td><td class="col-info">{unidade_nome}</td>')
            
            for d in datas_lista:
                data_curr_str = d.strftime('%Y-%m-%d')
                cell_class = ""
                cell_text = ""
                
                # Férias (VERMELHO)
                if not df_ferias.empty:
                    ferias_act = df_ferias[(df_ferias['tst'] == tst_nome) & (df_ferias['data_inicio'] <= data_curr_str) & (df_ferias['data_fim'] >= data_curr_str)]
                    if not ferias_act.empty:
                        cell_class = "cell-vacation"
                        cell_text = "F"
                
                # Alocação (VERDE ou AMARELO)
                if not cell_class and not df_alocacoes.empty:
                    aloc_act = df_alocacoes[(df_alocacoes['tst'] == tst_nome) & (df_alocacoes['data_inicio'] <= data_curr_str) & (df_alocacoes['data_fim'] >= data_curr_str)]
                    if not aloc_act.empty:
                        is_sub = aloc_act['is_substituicao'].iloc[0]
                        if is_sub == 1:
                            cell_class = "cell-substitution"
                            cell_text = "S"
                        else:
                            cell_class = "cell-allocated"
                            cell_text = "X"
                            
                html_lines.append(f'<td class="{cell_class}">{cell_text}</td>')
            html_lines.append('</tr>')
            
        html_lines.append('</tbody></table></div>')
        st.markdown("".join(html_lines), unsafe_allow_html=True)
        
        # Legenda
        st.markdown("""
        <div style="margin-top: 10px; margin-bottom: 25px; display: flex; gap: 20px; font-size: 13px;">
            <div><span style="background-color: #2E7D32; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">X</span> Alocação Titular (Verde)</div>
            <div><span style="background-color: #FBC02D; color: black; padding: 2px 8px; border-radius: 3px; font-weight: bold;">S</span> Substituto de Férias (Amarelo)</div>
            <div><span style="background-color: #C62828; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">F</span> Ausência por Férias (Vermelho)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("A data final deve ser maior ou igual à data inicial.")

    st.markdown("---")
    st.markdown("### ✏️ Gerenciar e Excluir Alocações Existentes")
    if not df_alocacoes.empty:
        for index, row in df_alocacoes.iterrows():
            col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns([3, 3, 3, 3, 1])
            col_a1.write(f"**Projeto:** {row['projeto']}")
            col_a2.write(f"**TST:** {row['tst']}")
            col_a3.write(f"**Veículo:** {row['veiculo']} | **Etilômetro:** {row['etilometro']}")
            col_a4.write(f"**Período:** {row['data_inicio']} até {row['data_fim']}")
            if col_a5.button("🗑️", key=f"del_aloc_{row['id']}"):
                execute_db("DELETE FROM alocacoes WHERE id = ?", (row['id'],))
                st.success("Alocação excluída!")
                st.rerun()
    else:
        st.info("Nenhuma alocação cadastrada.")

# TAB 2: NOVA ALOCAÇÃO
with menu[1]:
    st.subheader("Registrar Alocação Diária / Projeto")
    with st.form("form_alocacao"):
        projeto_sel = st.selectbox("Projeto (Cliente - Código)", df_projetos)
        tst_sel = st.selectbox("Técnico de Segurança (TST)", df_tsts)
        veiculo_sel = st.selectbox("Veículo Alocado", ["Nenhum"] + df_veiculos)
        etilometro_sel = st.selectbox("Etilômetro", ["Nenhum"] + df_etilometros)
        
        c_dt1, c_dt2 = st.columns(2)
        dt_inicio = c_dt1.date_input("Data Inicial", date.today())
        dt_fim = c_dt2.date_input("Data Final", date.today())
        
        is_sub = st.checkbox("Esta alocação é uma substituição de férias?")
        obs = st.text_input("Observações")
        
        btn_alocar = st.form_submit_button("Salvar Alocação")
        
        if btn_alocar:
            execute_db(
                "INSERT INTO alocacoes (projeto, tst, veiculo, etilometro, data_inicio, data_fim, is_substituicao, observacao) VALUES (?,?,?,?,?,?,?,?)",
                (projeto_sel, tst_sel, veiculo_sel, etilometro_sel, str(dt_inicio), str(dt_fim), 1 if is_sub else 0, obs)
            )
            st.success("Alocação registrada com sucesso!")
            st.rerun()

# TAB 3: GESTÃO DE FÉRIAS (REGISTRO AUTOMÁTICO DE COBERTURA DO SUBSTITUTO)
with menu[2]:
    st.subheader("Lançar Férias de TST")
    with st.form("form_ferias"):
        tst_ferias = st.selectbox("TST em Férias", df_tsts)
        tst_sub = st.selectbox("TST Substituto Designado", ["Nenhum"] + df_tsts)
        
        c_f1, c_f2 = st.columns(2)
        f_inicio = c_f1.date_input("Início das Férias", date.today())
        f_fim = c_f2.date_input("Fim das Férias", date.today())
        
        btn_ferias = st.form_submit_button("Registrar Férias")
        if btn_ferias:
            if tst_ferias == tst_sub:
                st.error("❌ O TST em férias não pode ser o seu próprio substituto!")
            elif tst_sub != "Nenhum" and not verificar_disponibilidade_tst(tst_sub, str(f_inicio), str(f_fim)):
                st.error(f"❌ **TST Não Disponível!** O substituto **{tst_sub}** possui outros compromissos no período de **{f_inicio.strftime('%d/%m/%Y')}** a **{f_fim.strftime('%d/%m/%Y')}**.")
            else:
                # 1. Registra Férias do Titular
                execute_db(
                    "INSERT INTO ferias (tst, substituto, data_inicio, data_fim) VALUES (?,?,?,?)",
                    (tst_ferias, tst_sub, str(f_inicio), str(f_fim))
                )
                
                # 2. Registra Alocação do Substituto em Amarelo (S) no Projeto do Titular
                if tst_sub != "Nenhum":
                    aloc_titular = df_alocacoes[df_alocacoes['tst'] == tst_ferias] if not df_alocacoes.empty else pd.DataFrame()
                    projeto_cobertura = aloc_titular['projeto'].iloc[-1] if not aloc_titular.empty else "Cobertura de Férias"
                    
                    execute_db(
                        "INSERT INTO alocacoes (projeto, tst, veiculo, etilometro, data_inicio, data_fim, is_substituicao, observacao) VALUES (?,?,?,?,?,?,?,?)",
                        (projeto_cobertura, tst_sub, "Nenhum", "Nenhum", str(f_inicio), str(f_fim), 1, f"Cobertura de férias de {tst_ferias}")
                    )
                    st.success(f"✅ Férias registradas! O TST **{tst_sub}** foi alocado em amarelo (S) para cobrir o projeto **{projeto_cobertura}**.")
                else:
                    st.success("✅ Férias registradas com sucesso!")
                st.rerun()

    st.markdown("---")
    st.markdown("### ✏️ Gerenciar e Excluir Registros de Férias")
    if not df_ferias.empty:
        for index, row in df_ferias.iterrows():
            col_f1, col_f2, col_f3, col_f4 = st.columns([4, 4, 3, 1])
            col_f1.write(f"**TST em Férias:** {row['tst']}")
            col_f2.write(f"**Substituto:** {row['substituto']}")
            col_f3.write(f"**Período:** {row['data_inicio']} até {row['data_fim']}")
            if col_f4.button("🗑️", key=f"del_ferias_{row['id']}"):
                execute_db("DELETE FROM ferias WHERE id = ?", (row['id'],))
                if row['substituto'] and row['substituto'] != "Nenhum":
                    execute_db("DELETE FROM alocacoes WHERE tst = ? AND is_substituicao = 1 AND data_inicio = ? AND data_fim = ?", (row['substituto'], row['data_inicio'], row['data_fim']))
                st.success("Registro de férias e substituição excluídos!")
                st.rerun()

# TAB 4: CADASTROS BASE DE RECURSOS
with menu[3]:
    st.subheader("⚙️ Cadastros de Recursos e Projetos")
    
    tab_cad1, tab_cad2, tab_cad3, tab_cad4 = st.tabs(["Projetos", "TSTs", "Veículos", "Etilômetros"])
    
    with tab_cad1:
        st.write("#### Cadastrar Novo Projeto")
        with st.form("form_add_projeto"):
            novo_proj = st.text_input("Nome do Projeto (Ex: Vale Norte - 6000)")
            if st.form_submit_button("Adicionar Projeto") and novo_proj:
                try:
                    execute_db("INSERT INTO projetos (nome) VALUES (?)", (novo_proj,))
                    st.success(f"Projeto '{novo_proj}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("Projeto já cadastrado ou erro na gravação.")
        st.write("##### Projetos Existentes:")
        df_p_full = run_query("SELECT id, nome FROM projetos")
        for idx, r in df_p_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['nome'])
            if c2.button("🗑️", key=f"del_p_{r['id']}"):
                execute_db("DELETE FROM projetos WHERE id = ?", (r['id'],))
                st.rerun()

    with tab_cad2:
        st.write("#### Cadastrar Novo TST")
        with st.form("form_add_tst"):
            novo_tst = st.text_input("Nome Completo do TST")
            if st.form_submit_button("Adicionar TST") and novo_tst:
                try:
                    execute_db("INSERT INTO tsts (nome) VALUES (?)", (novo_tst,))
                    st.success(f"TST '{novo_tst}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("TST já cadastrado ou erro na gravação.")
        st.write("##### TSTs Existentes:")
        df_t_full = run_query("SELECT id, nome FROM tsts")
        for idx, r in df_t_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['nome'])
            if c2.button("🗑️", key=f"del_t_{r['id']}"):
                execute_db("DELETE FROM tsts WHERE id = ?", (r['id'],))
                st.rerun()

    with tab_cad3:
        st.write("#### Cadastrar Novo Veículo")
        with st.form("form_add_veiculo"):
            nova_placa = st.text_input("Placa do Veículo")
            if st.form_submit_button("Adicionar Veículo") and nova_placa:
                try:
                    execute_db("INSERT INTO veiculos (placa) VALUES (?)", (nova_placa.upper(),))
                    st.success(f"Veículo '{nova_placa.upper()}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("Veículo já cadastrado ou erro na gravação.")
        st.write("##### Veículos Existentes:")
        df_v_full = run_query("SELECT id, placa FROM veiculos")
        for idx, r in df_v_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['placa'])
            if c2.button("🗑️", key=f"del_v_{r['id']}"):
                execute_db("DELETE FROM veiculos WHERE id = ?", (r['id'],))
                st.rerun()

    with tab_cad4:
        st.write("#### Cadastrar Novo Etilômetro")
        with st.form("form_add_etilometro"):
            novo_eti = st.text_input("Código/Número do Etilômetro")
            if st.form_submit_button("Adicionar Etilômetro") and novo_eti:
                try:
                    execute_db("INSERT INTO etilometros (codigo) VALUES (?)", (novo_eti,))
                    st.success(f"Etilômetro '{novo_eti}' adicionado com sucesso!")
                    st.rerun()
                except:
                    st.error("Etilômetro já cadastrado ou erro na gravação.")
        st.write("##### Etilômetros Existentes:")
        df_e_full = run_query("SELECT id, codigo FROM etilometros")
        for idx, r in df_e_full.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(r['codigo'])
            if c2.button("🗑️", key=f"del_e_{r['id']}"):
                execute_db("DELETE FROM etilometros WHERE id = ?", (r['id'],))
                st.rerun()

# TAB 5: POWER BI
with menu[4]:
    st.subheader("Exportação de Dados para Power BI")
    st.write("Baixe o arquivo CSV da tabela fato para conectar no seu relatório do Power BI.")
    
    if not df_alocacoes.empty:
        csv = df_alocacoes.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar fato_alocacoes.csv",
            data=csv,
            file_name="fato_alocacoes_chammas.csv",
            mime="text/csv"
        )
    else:
        st.warning("Sem dados de alocação para exportar.")
