#!/usr/bin/env bash

cmd=slicer_extension_manager_client
auth='--username admin --password adminadmin'

app1Name='App1'
app2Name='App2'
releaseName='Release1'

# Create 2 Applications
$cmd $auth app create $app1Name --desc "This is a description for $app1Name"
$cmd $auth app create $app2Name --desc "This is a description for $app2Name"

$cmd $auth app list

# Create 1 release in 'App1'
$cmd $auth release create $app1Name --name $releaseName --revision 0001 --desc "This is a description for $releaseName"

$cmd $auth release list $app1Name

# Upload extensions
echo 'Content of the extension 1' > file1.txt
echo 'Content of the extension 2' > file2.txt
echo 'Content of the extension 3' > file3.txt

cat file*.txt > contents.txt

$cmd $auth extension upload $app1Name ./file1.txt --os win --arch i386 --name ext1 --app_revision 0000 --desc "Description for ex1" > _output1.txt
$cmd $auth extension upload $app1Name ./file2.txt --os linux --arch i386 --name ext2 --app_revision 0000 --desc "Description for ex2" > _output2.txt
$cmd $auth extension upload $app1Name ./file3.txt --arch amd64 --name ext3 --app_revision 0001 --desc "Description for ex3" > _output3.txt

$cmd $auth extension list $app1Name
$cmd $auth extension list $app1Name --release $releaseName
$cmd $auth extension list $app1Name --all

# Download extensions
# TODO: Use the new option to get only the ID from the client
id1=$(python extractID.py _output1.txt)
id2=$(python extractID.py _output2.txt)
id3=$(python extractID.py _output3.txt)

$cmd $auth extension download "$id1" --dir_path ./dwn
$cmd $auth extension download "$id2" --dir_path ./dwn
$cmd $auth extension download "$id3" --dir_path ./dwn

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
# Delete all the applications
$cmd $auth app delete $app1Name
$cmd $auth app delete $app2Name

$cmd $auth app list
