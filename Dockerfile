FROM eclipse-temurin:17-jre-alpine

WORKDIR /app
COPY target/life-insurance-app-1.0.0.jar app.jar

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
