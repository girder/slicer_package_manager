#!/usr/bin/env bash

cmd=slicer_extension_manager_client
auth='--username admin --password adminadmin'

app1Name='App1'
app2Name='App2'
releaseName='Release1'

### Create 2 Applications ###
$cmd $auth app create $app1Name --desc "This is a description for $app1Name"
$cmd $auth app create $app2Name --desc "This is a description for $app2Name"

$cmd $auth app list

### Create 1 release in 'App1' ###
$cmd $auth release create $app1Name --name $releaseName --revision 0001 --desc "This is a description for $releaseName"
# List release from 'App1'
$cmd $auth release list $app1Name

### Upload new extensions ###
echo 'Content of the extension 1' > file1.txt
echo 'Content of the extension 2' > file2.txt
echo 'Content of the extension 3' > file3.txt

cat file*.txt > contents.txt

app_rev3="0001"
os3="macosx"
arch3="amd64"
rev3="0.0.1"

$cmd $auth extension upload $app1Name ./file1.txt --os win --arch i386 --name ext1 --app_revision 0000 --desc "Description for ex1" > _output1.txt
$cmd $auth extension upload $app1Name ./file2.txt --os linux --arch i386 --name ext2 --app_revision 0000 --desc "Description for ex2" > _output2.txt
$cmd $auth extension upload $app1Name ./file3.txt --os $os3 --arch $arch3 --name ext3 --app_revision $app_rev3 --revision $rev3 --desc "Description for ex3" > _output3.txt

# List extensions from 'App1'
$cmd $auth extension list $app1Name
$cmd $auth extension list $app1Name --release $releaseName
$cmd $auth extension list $app1Name --all

### Download extensions ###
# By ID
id1=$(python extractID.py _output1.txt)
id2=$(python extractID.py _output2.txt)

$cmd $auth extension download $app1Name "$id1" --dir_path ./dwn
$cmd $auth extension download $app1Name "$id2" --dir_path ./dwn

# By NAME
name3="${app_rev3}_${os3}_${arch3}_ext3_${rev3}"

$cmd $auth extension download $app1Name $name3 --dir_path ./dwn

# Check downloaded files
cat dwn/*ext1* >> contents_d.txt
cat dwn/*ext2* >> contents_d.txt
cat dwn/*ext3* >> contents_d.txt

diff contents.txt contents_d.txt

if [ $? != 0 ]; then
    echo "DIFFERENT"
    rm -rf dwn
    rm *.txt
    exit 1
fi
echo "TEST OK"
rm -rf dwn
rm *.txt

### Update extension  ### TODO

# Same revision

# Different revision


### Delete extensions ###
# By ID
$cmd $auth extension delete $app1Name $id1

# By full NAME
$cmd $auth extension delete $app1Name $name3

# List extension to make sure the delete is working
$cmd $auth extension list $app1Name --all

### Delete all the applications ###
$cmd $auth app delete $app1Name
$cmd $auth app delete $app2Name

# List all the applications
$cmd $auth app list
