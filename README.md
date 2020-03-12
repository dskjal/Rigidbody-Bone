# Rigidbody Bone
ボーンに剛体を設定する。サポートしている Blender のバージョンは 2.79 系列のみ。2.78 以前では動作しないと思われる。スクリプトへのリンクは<a href="https://raw.githubusercontent.com/dskjal/Rigidbody-Bone/master/rigidbody-bone.py">こちら</a>。   

2.80 用は<a href="https://raw.githubusercontent.com/dskjal/Rigidbody-Bone/master/rigidbody-bone-280.py">こちら</a>。  

Setup rigidbody to bones. Supported Blender version is only 2.79 series. <a href="https://raw.githubusercontent.com/dskjal/Rigidbody-Bone/master/rigidbody-bone.py">Direct link</a>.

Version 2.80 is <a href="https://raw.githubusercontent.com/dskjal/Rigidbody-Bone/master/rigidbody-bone-280.py">here</a>.  

# 使い方 How to use
剛体を設定したいボーンを選択し、***最後に頭に相当するボーンを選択する***。次に Setup Rigidbody ボタンを押す。
最後に選択した頭に相当するボーンには剛体のメッシュが親子付けされる。  

Select the bones that you want to add rigidbody. ***Select a head bone LAST***. Push Setup Rigidbody. 
Rigidbody meshes are parented to the last selected head bone.

アニメーションを ***先頭フレームから*** 再生しながら頭に相当するボーンを動かすことで動作検証ができる。Shift + ← で再生フレームを先頭に移動できる。  

You can test it by moving the head bone during animation playback. ***You must start from start frame(Shift + Left Arrow)*** .  

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-how-to-use.gif">

ばねをいい感じに設定すれば胸を揺らすのにも使える。  

You can bounce breasts by setting spring well.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-breast.gif">

# 制限 Restriction
頭に相当するボーンを除き、剛体を設定するボーンは子をひとつしか持てない制限がある。  

Bones that you want to add rigidbody have a ristriction that the bones only have one child except for a head bone.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/ramified-bones.jpg">

アーマチュアオブジェクトに移動・回転・拡縮が設定されている場合、正しく剛体メッシュを生成できないことがある。その場合は Ctrl + A で変更を適用してから剛体を生成する。  

A translated, rotated, scaled armature object may produce wrong rigidbody mesh. Check a armature object before setup or apply the change with Ctrl + A.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/armature-transform.jpg">

# Rigidbody Cache
デフォルトのキャッシュ値は 250 になっている。これを超えるフレーム数のアニメーションが必要な場合は必要なフレーム数を超える値をキャッシュに指定する。  

Default cache value is 250. If you want longer animation, raise this value.  

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-cache.jpg">

動作がおかしいときはキャッシュを削除するとうまく動作することがある。  

Free all bakes if rigidbody do not work well.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-free-all-bake.jpg">

# 障害物の追加 Add obstacles
メッシュに剛体を追加してアニメにチェックを入れる。  

Add a mesh, add rigidbody, check animated.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/set-obstacle.gif">

# アニメーションのベイク Bake animation
「ポーズ > アニメーション > アクションをベイク」でボーンアニメーションをベイクできる。その時にビジュアルキーイングにチェックを入れる必要がある。  

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-bake.png">  

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-visual-keying.png">

# 類似のアドオン
[rigid bodys generator（剛体ツール）](https://github.com/12funkeys/rigid_bodys_gen)
