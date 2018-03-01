#!/usr/bin/env bash

DEBUG=true

cmd=slicer_package_manager_client
auth='--username admin --password adminadmin'

app1Name="App1"
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

echo
echo "########### CLEAN UP ###########"
echo
### Delete the application ###
$cmd $auth app delete $app1Name
echo

# List application
$cmd $auth app list


### Create Application ###
echo
echo "########### CREATE APPLICATION ###########"
echo
$cmd $auth app create $app1Name --desc "This is a description for $app1Name"
echo
$cmd $auth app list

### Create release in 'App1' ###
echo
echo "########### CREATE RELEASE ###########"
echo
$cmd $auth release create $app1Name --name $releaseName --revision 0001 --desc "This is a description for $releaseName"
echo
# List release from 'App1'
$cmd $auth release list $app1Name

### Upload new extensions ###
echo
echo "########### UPLOAD NEW EXTENSIONS ###########"
echo
echo 'Content of the extension 1' > file1.txt
echo 'Content of the extension 2' > file2.txt
echo 'Content of the extension 3' > file3.txt
echo 'Content of the extension 4' > file4.txt
echo 'Content of the extension 5' > file5.txt


cat file*.txt > contents.txt

echo UPLOAD $ext1Name
$cmd $auth extension upload $app1Name ./file1.txt --ext_os win --arch i386 --name $ext1Name --app_revision 0000 --desc "Description for ex1" > _output1.txt
echo UPLOAD $ext2Name
$cmd $auth extension upload $app1Name ./file2.txt --ext_os linux --arch i386 --name $ext2Name --app_revision 0002 --desc "Description for ex2" > _output2.txt
echo UPLOAD $ext3Name
$cmd $auth extension upload $app1Name ./file3.txt --ext_os $os3 --arch $arch3 --name $ext3Name --app_revision $app_rev3 --revision $rev3 > _output3.txt
echo UPLOAD $ext4Name
$cmd $auth extension upload $app1Name ./file4.txt --ext_os linux --arch amd64 --name $ext4Name --app_revision 0000 > _output4.txt
echo UPLOAD $ext5Name
$cmd $auth extension upload $app1Name ./file5.txt --ext_os macosx --arch amd64 --name $ext5Name --app_revision 0000 > _output5.txt

# List extensions from 'App1'
echo
echo "########### LIST EXTENSIONS ###########"
echo
echo "List all the extension in the default release:"
$cmd $auth extension list $app1Name
echo
echo "List all the extension in the $releaseName:"
$cmd $auth extension list $app1Name --release $releaseName
echo
echo "List all the extension in $app1Name:"
$cmd $auth extension list $app1Name --all

echo
echo "########### DOWNLOAD EXTENSIONS ###########"
echo
# By ID
echo "By ID"
id1=$(python extractID.py _output1.txt)
id2=$(python extractID.py _output2.txt)
id4=$(python extractID.py _output4.txt)
id5=$(python extractID.py _output5.txt)

$cmd $auth extension download $app1Name "$id1" --dir_path ./dwn
$cmd $auth extension download $app1Name "$id2" --dir_path ./dwn
$cmd $auth extension download $app1Name "$id4" --dir_path ./dwn
$cmd $auth extension download $app1Name "$id5" --dir_path ./dwn

echo
echo "By NAME"
name3="${ext3Name}_${os3}_${arch3}_${rev3}"

$cmd $auth extension download $app1Name $name3 --dir_path ./dwn

echo
echo "########### CHECKING DOWNLOADED FILES ###########"
echo
cat dwn/*ext1* >> contents_d.txt
cat dwn/*ext2* >> contents_d.txt
cat dwn/*ext3* >> contents_d.txt
cat dwn/*ext4* >> contents_d.txt
cat dwn/*ext5* >> contents_d.txt

diff contents.txt contents_d.txt

if [ $? != 0 ]; then
    echo "DIFFERENT"
    rm -rf dwn
    rm *.txt
    echo
    echo
    echo "---------------------- TEST COMPLETE : FAILURE ----------------------"
    echo
    exit 1
fi
echo "TEST OK"
rm -rf dwn
rm *.txt

### Update extension  ### TODO

# Same revision

# Different revision

if ! $DEBUG; then
    ### Delete extensions ###
    echo
    echo "########### CLEAN UP ###########"
    echo
    # By ID
    echo "Delete by ID"
    $cmd $auth extension delete $app1Name $id1
    echo
    # By full NAME
    echo "Delete by NAME"
    $cmd $auth extension delete $app1Name $name3
    echo
    # List extension to make sure the delete is working
    $cmd $auth extension list $app1Name --all
    echo
    ### Delete the application ###
    $cmd $auth app delete $app1Name
    echo

    # List the application
    $cmd $auth app list
    echo
fi
echo
echo "---------------------- TEST COMPLETE : SUCCESS ----------------------"
echo
