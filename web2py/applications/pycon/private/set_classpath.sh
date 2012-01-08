#/bin/csh
# Please source this file.

export CRYPTO_HOME="./crypto-146"
export AXIS_HOME="./axis-1_4"

export CLASSPATH="."
export CLASSPATH="${CLASSPATH}:${AXIS_HOME}/lib/axis.jar"
export CLASSPATH="${CLASSPATH}:${AXIS_HOME}/lib/jaxrpc.jar"
export CLASSPATH="${CLASSPATH}:${AXIS_HOME}/lib/saaj.jar"
export CLASSPATH="${CLASSPATH}:${AXIS_HOME}/lib/wsdl4j.jar"
export CLASSPATH="${CLASSPATH}:${AXIS_HOME}/lib/commons-logging.jar"
export CLASSPATH="${CLASSPATH}:${AXIS_HOME}/lib/commons-discovery.jar"
export CLASSPATH="${CLASSPATH}:${CRYPTO_HOME}/jars/bcprov-jdk15-146.jar"
export CLASSPATH="${CLASSPATH}:${CRYPTO_HOME}/jars/bcpg-jdk15-146.jar"
export CLASSPATH="${CLASSPATH}:${CRYPTO_HOME}/jars/bctest-jdk15-146.jar"
export CLASSPATH="${CLASSPATH}:${CRYPTO_HOME}/jars/bcmail-jdk15-146.jar"
export CLASSPATH="${CLASSPATH}:./ppapi.jar"
echo $CLASSPATH
