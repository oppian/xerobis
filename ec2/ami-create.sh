#!/bin/bash -x

AWS_ID=375004319118
AWS_KEY=1EZPW78HVZMFXZXJXAR2
AWS_SECRET=ZXslmLM93TYrGA33GFyzIozSSN4VH1wrNXzyjXIt
LOCATION=EU

AMI_VER=xerobis-`date +%Y%m%d%H%M`
S3_BUCKET=xerobis-ami

EC2_DIR=.

export EC2_HOME=/usr/local/ec2-ami-tools
export PATH=$EC2_HOME/bin:$PATH
export EC2_KEY=$EC2_DIR/pk-RFVQF2T63ZC3ACJ4W5YHPWSIY2FC2GDY.pem
export EC2_CERT=$EC2_DIR/cert-RFVQF2T63ZC3ACJ4W5YHPWSIY2FC2GDY.pem

ec2-bundle-vol -d /mnt -k $EC2_KEY -c $EC2_CERT -u $AWS_ID -r i386 -p $AMI_VER

ec2-upload-bundle -b $S3_BUCKET -m /mnt/$AMI_VER.manifest.xml -a $AWS_KEY -s $AWS_SECRET --location $LOCATION

