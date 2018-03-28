#!/usr/bin/env bash

DEBUG=false

cli=slicer_package_manager_client
auth='--username admin --password adminadmin'

collName="Coll1"

app1Name="App1"
app2Name="App2"
app3Name="App3"
releaseName="Release1"

ext1Name="ext1"
ext2Name="ext2"
ext3Name="ext3"
ext4Name="ext4"
ext5Name="ext5"

pkg1Name="pkg1"
pkg2Name="pkg2"
pkg3Name="pkg3"

app_rev3="0001"
os3="macosx"
arch3="amd64"
rev3="0.0.1"

function assert_eval {
    eval $1 >/dev/null 2>&1
    if [ $? -eq "$2" ]; then
        echo " ... OK"
    else
        echo " ...FAIL"
        rm -rf dwn dwn2 >/dev/null 2>&1 || true
        rm *.txt >/dev/null 2>&1 || true
        exit 1
    fi
}

function assert {
    if [ "$1" -eq "$2" ]; then
        echo " ... OK"
    else
        echo " ... FAIL"
        #rm -rf dwn dwn2 >/dev/null 2>&1 || true
        #rm *.txt >/dev/null 2>&1 || true
        exit 1
    fi
}

# Need to delete manually the new collection "Coll1"
echo "########### CLEAN UP ###########"
rm -rf dwn dwn2 >/dev/null 2>&1 || true
rm *.txt >/dev/null 2>&1 || true
$cli $auth app delete $app1Name >/dev/null 2>&1 || true
#$cli $auth app delete $app2Name --coll_id $ID >/dev/null 2>&1 || true
#$cli $auth app delete $app3Name --coll_id $ID >/dev/null 2>&1 || true
echo

echo "########### APPLICATION ###########"
echo
echo "Create applications"
echo -n ">  $app1Name "
assert_eval "$cli $auth app create $app1Name --desc \"This is a description for $app1Name\"" 0
echo -n ">  $app2Name "
assert_eval "$cli $auth app create $app2Name --desc \"This is a description for $app2Name\" --coll_name $collName" 0
echo -n ">  $app3Name "
assert_eval "$cli $auth app create $app3Name --coll_name $collName" 0
# echo
# echo -n "Try to create an existing application: FAILURE"
# assert_eval "$cli $auth app create $app2Name" 1 #TODO: Find a way to make that work on CircleCI
echo -n "List applications"
assert_eval "$cli $auth app list" 0
echo
echo "------ TEST APPLICATION ... OK ------"
echo

echo "########### RELEASE ###########"
echo
echo -n "Create release $releaseName"
assert_eval "$cli $auth release create $app1Name $releaseName 0001 --desc \"This is a description for $releaseName\"" 0
echo -n "List release from 'App1'"
assert_eval "$cli $auth release list $app1Name" 0
echo
echo "------ TEST RELEASE ... OK ------"
echo

echo "########### EXTENSIONS ###########"
echo
echo 'Content of the extension 1' > ext_file1.txt
echo 'Content of the extension 2' > ext_file2.txt
echo 'Content of the extension 3' > ext_file3.txt
echo 'Content of the extension 4' > ext_file4.txt
echo 'Content of the extension 5' > ext_file5.txt
cat ext_file*.txt > contents.txt

echo "### UPLOAD ###"
echo
echo -n "> $ext1Name"
assert_eval "$cli $auth extension upload $app1Name ./ext_file1.txt --os win --arch i386 --name $ext1Name --app_revision 0000 --desc \"Description for ex1\" > ext_output1.txt" 0
echo -n "> $ext2Name"
assert_eval "$cli $auth extension upload $app1Name ./ext_file2.txt --os linux --arch i386 --name $ext2Name --app_revision 0002 --desc \"Description for ex2\" > ext_output2.txt" 0
echo -n "> $ext3Name"
assert_eval "$cli $auth extension upload $app1Name ./ext_file3.txt --os $os3 --arch $arch3 --name $ext3Name --app_revision $app_rev3 --revision $rev3 > ext_output3.txt" 0
echo -n "> $ext4Name"
assert_eval "$cli $auth extension upload $app1Name ./ext_file4.txt --os linux --arch amd64 --name $ext4Name --app_revision 0000 > ext_output4.txt" 0
echo -n "> $ext5Name"
assert_eval "$cli $auth extension upload $app1Name ./ext_file5.txt --os macosx --arch amd64 --name $ext5Name --app_revision 0000 > ext_output5.txt" 0
echo

echo "### LIST ###"
echo
echo -n "List all the extension in the default release"
assert_eval "$cli $auth extension list $app1Name" 0
echo -n "List all the extension in the $releaseName"
assert_eval "$cli $auth extension list $app1Name --release $releaseName" 0
echo -n "List all the extension in $app1Name"
assert_eval "$cli $auth extension list $app1Name --all >/dev/null 2>&1" 0
echo

echo "### DOWNLOAD ###"
echo
echo "___By ID___"
ext_id1=$(python extractID.py ext_output1.txt)
ext_id2=$(python extractID.py ext_output2.txt)
ext_id4=$(python extractID.py ext_output4.txt)
ext_id5=$(python extractID.py ext_output5.txt)
echo -n "> $ext1Name"
assert_eval "$cli $auth extension download $app1Name \"$ext_id1\" --dir_path ./dwn" 0
echo -n "> $ext2Name"
assert_eval "$cli $auth extension download $app1Name \"$ext_id2\" --dir_path ./dwn" 0
echo -n "> $ext4Name"
assert_eval "$cli $auth extension download $app1Name \"$ext_id4\" --dir_path ./dwn" 0
echo -n "> $ext5Name"
assert_eval "$cli $auth extension download $app1Name \"$ext_id5\" --dir_path ./dwn" 0
echo
echo "___By NAME___"
ext_name3="${app_rev3}_${ext3Name}_${os3}_${arch3}_${rev3}"
echo -n "> $ext3Name"
assert_eval "$cli $auth extension download $app1Name $ext_name3 --dir_path ./dwn" 0
echo

echo "### COMPARE DOWNLOADED EXTENSION FILES ###"
echo
cat dwn/*ext1* >> ext_contents_d.txt
cat dwn/*ext2* >> ext_contents_d.txt
cat dwn/*ext3* >> ext_contents_d.txt
cat dwn/*ext4* >> ext_contents_d.txt
cat dwn/*ext5* >> ext_contents_d.txt

echo -n "Compare content between uploaded files and downloaded files"
diff contents.txt ext_contents_d.txt
assert $? 0
echo
echo "### UPDATE EXTENSION ###"
echo -n "> UPDATE $ext5Name with same revision"
assert_eval "$cli $auth extension upload $app1Name ./ext_file1.txt --os macosx --arch amd64 --name $ext5Name --app_revision 0000" 0
echo -n "> DOWNLOAD $ext5Name"
assert_eval "$cli $auth extension download $app1Name \"$ext_id5\" --dir_path ./dwn2" 0
echo -n "==> The extension shouldn't be updated"
diff dwn/*ext5* dwn2/*ext*
assert $? 0
echo
rm -rf dwn2
echo -n "> UPDATE $ext5Name with different revision"
assert_eval "$cli $auth extension upload $app1Name ./ext_file1.txt --os macosx --arch amd64 --name $ext5Name --app_revision 0000 --revision 1111" 0
echo -n "> DOWNLOAD $ext5Name"
assert_eval "$cli $auth extension download $app1Name \"$ext_id5\" --dir_path ./dwn2" 0
echo -n "==> The file should have change"
diff dwn/*ext1* dwn2/*ext*
assert $? 0
echo
echo "------ TEST EXTENSION ... OK ------"
echo

echo "########### PACKAGE ###########"
echo
echo 'Content of the package 1' > pkg_file1.txt
echo 'Content of the package 2' > pkg_file2.txt
echo 'Content of the package 3' > pkg_file3.txt
cat pkg_file*.txt > contents.txt

echo "### UPLOAD ###"
echo
echo -n "> $pkg1Name"
assert_eval "$cli $auth package upload $app1Name ./pkg_file1.txt --os win --arch i386 --name $pkg1Name --revision 0000 > pkg_output1.txt" 0
echo -n "> $pkg2Name"
assert_eval "$cli $auth package upload $app1Name ./pkg_file2.txt --os linux --arch i386 --name $pkg2Name --revision 0002 > pkg_output2.txt" 0
echo -n "> $pkg3Name"
assert_eval "$cli $auth package upload $app1Name ./pkg_file3.txt --os $os3 --arch $arch3 --name $pkg3Name --revision $app_rev3 > pkg_output3.txt" 0
echo

echo "### LIST ###"
echo
echo -n "List all the package"
assert_eval "$cli $auth package list $app1Name" 0
echo -n "List all the package in the $releaseName"
assert_eval "$cli $auth package list $app1Name --release $releaseName" 0
echo

echo "### DOWNLOAD ###"
echo
echo "___By ID___"
pkg_id1=$(python extractID.py pkg_output1.txt)
pkg_id2=$(python extractID.py pkg_output2.txt)
echo -n "> $ext1Name"
assert_eval "$cli $auth package download $app1Name \"$pkg_id1\" --dir_path ./dwn" 0
echo -n "> $ext2Name"
assert_eval "$cli $auth package download $app1Name \"$pkg_id2\" --dir_path ./dwn" 0
echo
echo "___By NAME___"
pkg_name3="${pkg3Name}_${os3}_${arch3}_${app_rev3}"
echo -n "> $pkg3Name"
assert_eval "$cli $auth package download $app1Name $pkg_name3 --dir_path ./dwn" 0
echo

echo "### COMPARE DOWNLOADED PACKAGE FILES ###"
echo
cat dwn/*pkg1* >> pkg_contents_d.txt
cat dwn/*pkg2* >> pkg_contents_d.txt
cat dwn/*pkg3* >> pkg_contents_d.txt
echo -n "Compare content between uploaded files and downloaded files"
diff contents.txt pkg_contents_d.txt
assert $? 0
echo

echo "### UPDATE PACKAGE ###"
echo
echo -n "> UPDATE $pkg2Name"
assert_eval "$cli $auth package upload $app1Name ./pkg_file1.txt --os linux --arch i386 --name $pkg2Name --revision 0002" 0
rm -rf dwn2
echo -n "> DOWNLOAD $pkg2Name"
assert_eval "$cli $auth package download $app1Name \"$pkg_id2\" --dir_path ./dwn2" 0
echo -n "==> The file should have change"
diff dwn/*pkg1* dwn2/*pkg*
assert $? 0
echo
echo "------ TEST PACKAGE ... OK ------"
echo

echo "########### DRAFT ###########"
echo

echo "### LIST ###"
echo
echo -n "List all the draft release"
assert_eval "$cli $auth draft list $app1Name" 0
echo -n "List the older draft release using an offset"
assert_eval "$cli $auth draft list $app1Name --offset 1" 0
echo -n "List one draft release using its 'revision'"
assert_eval "$cli $auth draft list $app1Name --revision 0002" 0
echo

echo "### DELETE ###"
echo
echo -n "Delete Draft release by revision"
assert_eval "$cli $auth draft delete $app1Name 0002" 0
echo
echo "------ TEST DRAFT ... OK ------"
echo

if ! $DEBUG; then
    echo
    echo "########### DELETE ###########"
    echo
    echo -n "Delete Extension by ID"
    assert_eval "$cli $auth extension delete $app1Name $ext_id1" 0
    echo -n "Delete Extension by name"
    assert_eval "$cli $auth extension delete $app1Name $ext_name3" 0
    echo
    echo -n "Delete Application Package by ID"
    assert_eval "$cli $auth package delete $app1Name $pkg_id1" 0
    echo -n "Delete Application Package by name"
    assert_eval "$cli $auth package delete $app1Name $pkg_name3" 0
    echo
    echo -n "Delete release"
    assert_eval "$cli $auth release delete $app1Name $releaseName" 0
    echo
    echo "Delete application"
    echo -n "> $app1Name"
    assert_eval "$cli $auth app delete $app1Name" 0
#    echo -n "> $app2Name"
#    assert_eval "$cli $auth app delete $app2Name" 0
#    echo -n "> $app3Name"
#    assert_eval "$cli $auth app delete $app3Name" 0
    echo
fi
echo "---------------------- TEST COMPLETE : SUCCESS ----------------------"
echo
rm -rf dwn dwn2
rm *.txt
