# Local Spark image (no external registry required)
FROM eclipse-temurin:17-jre AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates python3 python3-pip python3-venv \
 && rm -rf /var/lib/apt/lists/*

ARG SPARK_VERSION=3.5.1
ARG HADOOP_VERSION=3

# Download prebuilt Spark (Apache archive is stable)
RUN mkdir -p /opt && \
    curl -fsSL https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
WORKDIR /opt

