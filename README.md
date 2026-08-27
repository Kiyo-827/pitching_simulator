# pitching_simulator

3D baseball pitching simulator with gravity, drag, Magnus force, and customizable aerodynamic forces.

## 概要

`pitching_simulator` は、野球ボールの投球軌道を3次元空間で数値計算するための Python プログラムです。

ボールに働く力として、重力、空気抵抗、マグヌス力を考慮し、運動方程式を数値的に解くことで投球軌道を計算します。

また、シーム（縫い目）による空気力など、独自の力を追加できるようにプログラムを構成しています。

## 運動方程式

ボールの運動は、次の運動方程式によって計算します。

```math
m\frac{d\mathbf{v}}{dt}
=
\mathbf{F}_g
+
\mathbf{F}_D
+
\mathbf{F}_M
+
\mathbf{F}_{original}
```

ここで、

* $m$ : ボールの質量
* $\mathbf{v}$ : ボールの速度
* $\mathbf{F}_g$ : 重力
* $\mathbf{F}_D$ : 空気抵抗
* $\mathbf{F}_M$ : マグヌス力
* $\mathbf{F}_{original}$ : 独自に追加する空気力

です。

## 重力

重力は、

```math
\mathbf{F}_g
=
\begin{pmatrix}
0 \\
0 \\
-mg
\end{pmatrix}
```

とします。

ここで、

* $g$ : 重力加速度

です。

## 空気抵抗

空気抵抗は、

```math
\mathbf{F}_D
=
-\frac{1}{2}
\rho C_D A
|\mathbf{v}|
\mathbf{v}
```

とします。

ここで、

* $\rho$ : 空気密度
* $C_D$ : 抗力係数
* $A$ : ボールの投影面積
* $\mathbf{v}$ : ボールの速度ベクトル
* $|\mathbf{v}|$ : ボールの速さ

です。

空気抵抗は、ボールの進行方向と反対向きに働きます。

## マグヌス力

ボールの回転によるマグヌス力は、

```math
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
```

とします。

ここで、

* $C_L$ : マグヌス力係数
* $\boldsymbol{\omega}$ : ボールの回転角速度ベクトル
* $\hat{\boldsymbol{\omega}}$ : 回転軸方向の単位ベクトル
* $\hat{\mathbf{v}}$ : 速度方向の単位ベクトル

です。

単位ベクトルは、

```math
\hat{\boldsymbol{\omega}}
=
\frac{\boldsymbol{\omega}}
{|\boldsymbol{\omega}|}
```

```math
\hat{\mathbf{v}}
=
\frac{\mathbf{v}}
{|\mathbf{v}|}
```

と定義します。

外積

```math
\hat{\boldsymbol{\omega}}
\times
\hat{\mathbf{v}}
```

によって、回転軸と進行方向の両方に垂直なマグヌス力の方向が決まります。

## オリジナルの空気力

このプログラムでは、重力、空気抵抗、マグヌス力以外の力を追加できるようにしています。

特に、低回転の野球ボールについて、シームの向きによって生じる空気力をモデル化し、

```math
\mathbf{F}_{original}
=
\mathbf{F}_{seam}
```

として運動方程式に追加することを想定しています。

この項の具体的なモデルは、研究内容に応じて変更できます。

## 座標系

3次元座標は次のように定義します。

* $x$ 軸 : 投手から見た左右方向
* $y$ 軸 : 投手から捕手へ向かう方向
* $z$ 軸 : 鉛直上向き

ボールの位置ベクトルは、

```math
\mathbf{r}
=
\begin{pmatrix}
x \\
y \\
z
\end{pmatrix}
```

速度ベクトルは、

```math
\mathbf{v}
=
\begin{pmatrix}
v_x \\
v_y \\
v_z
\end{pmatrix}
```

加速度ベクトルは、

```math
\mathbf{a}
=
\begin{pmatrix}
a_x \\
a_y \\
a_z
\end{pmatrix}
```

で表します。

## 回転角速度

ボールの回転角速度は、

```math
\boldsymbol{\omega}
=
\begin{pmatrix}
\omega_x \\
\omega_y \\
\omega_z
\end{pmatrix}
```

で指定します。

`parameter.ini` では、

```ini
angular_velocity = [omega_x, omega_y, omega_z]
```

の形式で設定します。

単位は `rad/s` です。

## 数値計算

運動方程式は、4次の Runge-Kutta 法（RK4）を用いて数値積分します。

計算で使用する状態ベクトルは、

```math
\mathbf{q}
=
\begin{pmatrix}
x \\
y \\
z \\
v_x \\
v_y \\
v_z
\end{pmatrix}
```

です。

その時間微分は、

```math
\frac{d\mathbf{q}}{dt}
=
\begin{pmatrix}
v_x \\
v_y \\
v_z \\
a_x \\
a_y \\
a_z
\end{pmatrix}
```

となります。

各時刻について、次の10列を CSV ファイルに出力します。

```text
t,x,y,z,v_x,v_y,v_z,a_x,a_y,a_z
```

## パラメータ

計算条件は、

```text
./param/parameter.ini
```

で設定します。

主なパラメータは次の通りです。

* `gravity` : 重力加速度
* `air_density` : 空気密度
* `ball_density` : ボールの密度
* `ball_sizes_mm` : ボールの直径
* `drag_coefficient` : 抗力係数
* `magnus_coefficient` : マグヌス力係数
* `initial_position` : 初期位置
* `initial_speed` : 初速度の大きさを指定するベクトル
* `initial_direction` : 初速度の方向
* `angular_velocity` : 回転角速度ベクトル
* `dt` : 時間刻み
* `max_time` : 最大計算時間
* `target_y` : ホームベース位置

## 可視化

計算された軌道から、次の3つの画像を作成します。

* x-y 平面の投球軌道
* x-z 平面の投球軌道
* y-z 平面の投球軌道

また、

* x-y 平面
* x-z 平面
* y-z 平面
* 3次元軌道

を同時に表示する動画を作成します。

各グラフでは、座標軸の縮尺をそろえ、1 m がどの方向でも同じ長さになるように表示します。

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
    │   └── pitching.csv
    ├── image/
    │   ├── trajectory_xy.png
    │   ├── trajectory_xz.png
    │   └── trajectory_yz.png
    └── movie/
        └── pitching.mp4
```

## 実行方法

リポジトリのトップディレクトリで、

```bash
bash pitching.sh
```

を実行します。

`pitching.sh` は、次の処理を順番に実行します。

1. Python 仮想環境の作成・有効化
2. 投球軌道の数値計算
3. CSV ファイルの出力
4. 軌道画像の作成
5. 投球軌道動画の作成

計算結果は、

```text
./output/
```

以下に保存されます。

## 今後の拡張

このプログラムでは、各力を独立した関数として定義しています。

```python
force_gravity()
force_drag()
force_magnus()
force_original()
```

そのため、空気力のモデルを変更したり、新しい力を追加したりして、その力が投球軌道に与える影響を調べることができます。

特に、低回転の野球ボールにおけるシームの影響をモデル化し、通常のマグヌス効果だけでは説明できない軌道変化について調べることを想定しています。
