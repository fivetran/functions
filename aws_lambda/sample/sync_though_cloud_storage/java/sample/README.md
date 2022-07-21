## Building the function
- References
    - http://www.java2s.com/Tutorials/Java/Maven_Tutorial/2010__Maven_Create_Project.htm
    - https://docs.aws.amazon.com/lambda/latest/dg/java-package.html
- Install mvn
    ```bash
       brew install mvn
    ```
- Initialise the project (if you want to build the project from scratch)
    ```bash
       mvn archetype:generate -DgroupId=com.fivetran.function -DartifactId=sample -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
    ```
- Build the project and get the executables
    ```bash
    mvn package
    ````
- Deploy the /target/sample-1.0.jar file in aws lambda.