# pitching_simulator

3D baseball pitching simulator with gravity, drag, Magnus force, and customizable aerodynamic forces.

## 概要

`pitching_simulator` は、野球ボールの投球軌道を3次元空間で数値計算するための Python プログラムです。

ボールに働く力として、重力、空気抵抗、マグヌス力を考慮し、運動方程式を数値的に解くことで投球軌道を計算します。

また、シーム（縫い目）による空気力など、独自の力を追加できるようにプログラムを構成しています。

## 運動方程式

ボールの運動は、次の運動方程式によって計算します。

$$
m\frac{d\mathbf{v}}{dt}
=
\mathbf{F}_g
+
\mathbf{F}_D
+
\mathbf{F}_M
$$

ここで、

* $m$ : ボールの質量
* $\mathbf{v}$ : ボールの速度
* $\mathbf{F}_g$ : 重力
* $\mathbf{F}_D$ : 空気抵抗
* $\mathbf{F}_M$ : マグヌス力

です。

### 重力

重力は

$$
\mathbf{F}_g
=
\begin{pmatrix}
0 \\
0 \\
-mg
\end{pmatrix}
$$

とします。

### 空気抵抗

空気抵抗は

$$
\mathbf{F}_D
=
-\frac{1}{2}
\rho C_D A
|\mathbf{v}|
\mathbf{v}
$$

とします。

ここで、

* $\rho$ : 空気密度
* $C_D$ : 抗力係数
* $A$ : ボールの投影面積

です。

### マグヌス力

ボールの回転によるマグヌス力は

$$
\mathbf{F}_M
=
\frac{1}{2}
\rho C_L A
|\mathbf{v}|^2
\left(
\hat{\boldsymbol{\omega}}
\times
\hat{\mathbf{v}}
\right)
$$

とします。

ここで、

* $C_L$ : マグヌス力係数
* $\boldsymbol{\omega}$ : ボールの回転角速度ベクトル
* $\hat{\boldsymbol{\omega}}$ : 回転軸方向の単位ベクトル
* $\hat{\mathbf{v}}$ : 速度方向の単位ベクトル

です。

## 座標系

3次元座標は次のように定義します。

* $x$ 軸 : 投手から見た左右方向
* $y$ 軸 : 投手から捕手へ向かう方向
* $z$ 軸 : 鉛直上向き

したがって、ボールの位置と速度は

$$
\mathbf{r}
=
(x,y,z)
$$

$$
\mathbf{v}
=
(v_x,v_y,v_z)
$$

で表します。

## 数値計算

運動方程式は4次の Runge-Kutta 法（RK4）を用いて数値積分します。

各時刻について、

```text
t, x, y, z, v_x, v_y, v_z, a_x, a_y, a_z
```

を CSV ファイルに出力します。

## 可視化

計算された軌道から、次の図を作成します。

* x-y 平面の投球軌道
* x-z 平面の投球軌道
* y-z 平面の投球軌道

また、これら3つの投影図と3次元軌道をまとめた動画も作成します。

各グラフでは座標軸の縮尺をそろえ、1 m がどの方向でも同じ長さになるように表示します。

## ディレクトリ構成

```text
pitching_simulator/
├── pitching.sh
├── param/
│   └── parameter.ini
├── python/
│   ├── pitching.py
│   ├── image.py
│   └── movie.py
└── output/
    ├── csv/
    ├── image/
    └── movie/
```

## 実行方法

```bash
bash pitching.sh
```

を実行すると、

1. 投球軌道の数値計算
2. CSV ファイルの出力
3. 軌道画像の作成
4. 投球軌道動画の作成

を順番に実行します。
