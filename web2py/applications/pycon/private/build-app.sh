#!/bin/bash

echo
echo "Be sure Java version is at least 1.4"
$JAVA -version
echo ; echo ; #sleep 3


echo "CLASSPATH="
echo $CLASSPATH
echo

echo compiling java files ...
javac -g -classpath "$CLASSPATH" 	                \
	ButtonEncryption.java	\
	com/paypal/crypto/sample/*.java

echo "Done!!!!!"

