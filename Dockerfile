# A java 8 image; any will probably do
FROM eclipse-temurin:8

# The setup script uses unzip
RUN apt-get update && apt-get install -y unzip

COPY . /src
WORKDIR /src
RUN ./setup-dependencies.bash
