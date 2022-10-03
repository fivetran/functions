## Building the function
- References: https://docs.aws.amazon.com/lambda/latest/dg/golang-package.html#golang-package-prereqs
- Install go
    ```bash
       brew install go
    ```
- Initialise the project (if you don't have go.mod)
    ```bash
       go mod init go
    ```
- Download the lambda library from GitHub.
    ```bash
    go get github.com/aws/aws-lambda-go/lambda
    ````
- Compile your executable.
    ```bash
    GOOS=linux go build main.go
    ```
- Create a deployment package by packaging the executable in a .zip file.
    ```bash
    zip function.zip main
    ```