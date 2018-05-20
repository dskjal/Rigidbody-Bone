# Rigidbody-Bone
ボーンに剛体を設定する。  

Setup bones to rigidbody.

# 使い方 How to use
剛体を設定したいボーンを選択し、***最後に頭に相当するボーンを選択する***。次に Setup Rigidbody ボタンを押す。
最後に選択した頭に相当するボーンには剛体のメッシュが親子付けされる。  

Select the bones that you want to add rigidbody. ***Select a head bone LAST***. Push Setup Rigidbody. 
Rigidbody meshes are parented to the last selected head bone.

アニメーションを ***先頭フレームから*** 再生しながら頭に相当するボーンを動かすことで動作検証ができる。Shift + ← で再生フレームを先頭に移動できる。  

You can test it by moving the head bone during animation playback. You must start from start frame(Shift + Left Arrow).  

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/rigidbody-bone-how-to-use.gif">

# 制限 Restriction
頭に相当するボーンを除き、剛体を設定するボーンは子をひとつしか持てない制限がある。  

Bones that you want to add rigidbody have a ristriction that the bones only have one child except for a head bone.

<img src="https://github.com/dskjal/Rigidbody-Bone/blob/master/ramified-bones.jpg">

アーマチュアオブジェクトに移動・回転・拡縮が設定されている場合、正しく剛体メッシュを生成できないことがある。その場合は Ctrl + A で変更を適用してから剛体を生成する。  

A translated, rotated, scaled armature object may produce wrong rigidbody mesh. Check a armature object before setup or apply the change with Ctrl + A.

