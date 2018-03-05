#!/usr/bin/env bash

DEBUG=false

cmd=slicer_package_manager_client
auth='--username admin --password adminadmin'

app1Name="App1"
app2Name="App2"
releaseName="Release1"

ext1Name="ext1"
ext2Name="ext2"
ext3Name="ext3"
ext4Name="ext4"
ext5Name="ext5"

app_rev3="0001"
os3="macosx"
arch3="amd64"
rev3="0.0.1"

function check {
    if eval $1 >/dev/null 2>&1; then
        echo -n " ... OK"
    else
        echo " ...FAIL"
        exit 1
    fi
}

function checkDiff {
    if [ "$?" -eq "0" ]; then
        echo " ... OK"
    else
        echo " ... FAIL"
        exit 1
    fi
}

echo
echo "########### CLEAN UP ###########"

rm -rf dwn dwn2 >/dev/null 2>&1 || true
rm *.txt >/dev/null 2>&1 || true

$cmd $auth app delete $app1Name >/dev/null 2>&1 || true
$cmd $auth app delete $app2Name >/dev/null 2>&1 || true

echo
echo "########### APPLICATION ###########"
echo
echo -n "Create applications $app1Name "
check "$cmd $auth app create $app1Name --desc \"This is a description for $app1Name\""
echo -n "  $app2Name"
check "$cmd $auth app create $app2Name --desc \"This is a description for $app2Name\""
echo
echo -n "Try to create an existing application should fail"
($cmd $auth app create $app2Name >/dev/null 2>&1 && exit 1) || echo " ... OK"
echo
echo -n "List applications"
check "$cmd $auth app list"
echo
echo
echo "------ TEST APPLICATION ... OK ------"

echo
echo "########### CREATE RELEASE ###########"
echo
echo -n "Create release $releaseName"
check "$cmd $auth release create $app1Name --name $releaseName --revision 0001 --desc \"This is a description for $releaseName\""
echo
echo -n "List release from 'App1'"
check "$cmd $auth release list $app1Name"
echo
echo
echo "------ TEST RELEASE ... OK ------"

echo
echo "########### UPLOAD NEW EXTENSIONS ###########"
echo
echo 'Content of the extension 1' > file1.txt
echo 'Content of the extension 2' > file2.txt
echo 'Content of the extension 3' > file3.txt
echo 'Content of the extension 4' > file4.txt
echo 'Content of the extension 5' > file5.txt

cat file*.txt > contents.txt

echo -n "UPLOAD $ext1Name"
check "$cmd $auth extension upload $app1Name ./file1.txt --ext_os win --arch i386 --name $ext1Name --app_revision 0000 --desc \"Description for ex1\" > _output1.txt"
echo
echo -n "UPLOAD $ext2Name"
check "$cmd $auth extension upload $app1Name ./file2.txt --ext_os linux --arch i386 --name $ext2Name --app_revision 0002 --desc \"Description for ex2\" > _output2.txt"
echo
echo -n "UPLOAD $ext3Name"
check "$cmd $auth extension upload $app1Name ./file3.txt --ext_os $os3 --arch $arch3 --name $ext3Name --app_revision $app_rev3 --revision $rev3 > _output3.txt"
echo
echo -n "UPLOAD $ext4Name"
check "$cmd $auth extension upload $app1Name ./file4.txt --ext_os linux --arch amd64 --name $ext4Name --app_revision 0000 > _output4.txt"
echo
echo -n "UPLOAD $ext5Name"
check "$cmd $auth extension upload $app1Name ./file5.txt --ext_os macosx --arch amd64 --name $ext5Name --app_revision 0000 > _output5.txt"
echo
echo
echo "------ UPLOAD ... OK ------"

echo
echo "########### LIST EXTENSIONS ###########"
echo
echo -n "List all the extension in the default release"
check "$cmd $auth extension list $app1Name"
echo
echo -n "List all the extension in the $releaseName"
check "$cmd $auth extension list $app1Name --release $releaseName"
echo
echo -n "List all the extension in $app1Name"
check "$cmd $auth extension list $app1Name --all >/dev/null 2>&1"
echo
echo "########### DOWNLOAD EXTENSIONS ###########"
echo
echo "By ID"
id1=$(python extractID.py _output1.txt)
id2=$(python extractID.py _output2.txt)
id4=$(python extractID.py _output4.txt)
id5=$(python extractID.py _output5.txt)

echo -n "DOWNLOAD $ext1Name"
check "$cmd $auth extension download $app1Name \"$id1\" --dir_path ./dwn"
echo
echo -n "DOWNLOAD $ext2Name"
check "$cmd $auth extension download $app1Name \"$id2\" --dir_path ./dwn"
echo
echo -n "DOWNLOAD $ext4Name"
check "$cmd $auth extension download $app1Name \"$id4\" --dir_path ./dwn"
echo
echo -n "DOWNLOAD $ext5Name"
check "$cmd $auth extension download $app1Name \"$id5\" --dir_path ./dwn"

echo
echo "By NAME"
name3="${ext3Name}_${os3}_${arch3}_${rev3}"
echo -n "DOWNLOAD $ext3Name"
check "$cmd $auth extension download $app1Name $name3 --dir_path ./dwn"
echo
echo
echo "########### COMPARE DOWNLOADED FILES ###########"
echo
cat dwn/*ext1* >> contents_d.txt
cat dwn/*ext2* >> contents_d.txt
cat dwn/*ext3* >> contents_d.txt
cat dwn/*ext4* >> contents_d.txt
cat dwn/*ext5* >> contents_d.txt


echo -n "Compare content between uploaded files and downloaded files"
check "diff contents.txt contents_d.txt"
echo
echo
### Update extension  ###
echo -n "UPDATE $ext5Name with same revision"
check "$cmd $auth extension upload $app1Name ./file1.txt --ext_os macosx --arch amd64 --name $ext5Name --app_revision 0000"
echo
echo -n "DOWNLOAD $ext5Name"
check "$cmd $auth extension download $app1Name \"$id5\" --dir_path ./dwn2"
echo
echo -n "The file shouldn't be updated"
diff dwn/*ext5* dwn2/*ext*
checkDiff
echo
rm -rf dwn2
echo -n "UPDATE $ext5Name with different revision"
check "$cmd $auth extension upload $app1Name ./file1.txt --ext_os macosx --arch amd64 --name $ext5Name --app_revision 0000 --revision 1111"
echo
echo -n "DOWNLOAD $ext5Name"
check "$cmd $auth extension download $app1Name \"$id5\" --dir_path ./dwn2"
echo
echo -n "The file should have change"
diff dwn/*ext1* dwn2/*ext*
checkDiff
echo
echo "------ TEST EXTENSION ... OK ------"

if ! $DEBUG; then
    echo
    echo "########### DELETE ###########"
    echo
    echo -n "Delete Extension by ID"
    check "$cmd $auth extension delete $app1Name $id1"
    echo
    echo -n "Delete Extension by name"
    check "$cmd $auth extension delete $app1Name $name3"
    echo
    echo -n "Delete release"
    check "$cmd $auth release delete $app1Name $releaseName"
    echo
    echo -n "Delete application  $app1Name"
    check "$cmd $auth app delete $app1Name"
    echo -n "  $app2Name"
    check "$cmd $auth app delete $app2Name"
    echo
fi
echo
echo "---------------------- TEST COMPLETE : SUCCESS ----------------------"
echo
rm -rf dwn dwn2
rm *.txt
