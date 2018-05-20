# Rigidbody-Bone
ボーンに剛体を設定する。  

Setup bones to rigidbody.

# 使い方 How to use
剛体を設定したいボーンを選択し、***最後に頭に相当するボーンを選択する***。次に Setup Rigidbody ボタンを押す。
最後に選択した頭に相当するボーンには剛体のメッシュが親子付けされる。  

Select the bones that you want to add rigidbody. ***Select a head bone LAST***. Push Setup Rigidbody. 
Rigidbody meshes are parented to the last selected head bone.

アニメーションを再生しながら頭に相当するボーンを動かすことで動作検証ができる。  

You can test it by moving the head bone during animation playback.  

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-how-to-use.gif">

# 制限 Restriction
頭に相当するボーンを除き、剛体を設定するボーンは子をひとつしか持てない制限がある。  

Bones that you want to add rigidbody have a ristriction that the bones only have one child except for a head bone.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/ramified-bones.jpg">
