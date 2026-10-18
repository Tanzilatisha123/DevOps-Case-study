pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'tanzila123'      // <-- change this
        IMAGE_NAME     = "${DOCKERHUB_USER}/student-task-manager"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME%:%IMAGE_TAG% -t %IMAGE_NAME%:latest ."
            }
        }

        stage('Test') {
            steps {
                // runs the pytest tests inside the freshly built image
                bat "docker run --rm %IMAGE_NAME%:%IMAGE_TAG% python -m pytest -q"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    bat '''
                        echo %DH_PASS%| docker login -u %DH_USER% --password-stdin
                        docker push %IMAGE_NAME%:%IMAGE_TAG%
                        docker push %IMAGE_NAME%:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    powershell '''
                        (Get-Content k8s/deployment.yaml) -replace 'DOCKERHUB_USER/student-task-manager:IMAGE_TAG', "$env:IMAGE_NAME`:$env:IMAGE_TAG" | Set-Content k8s/deployment.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl rollout status deployment/student-task-manager --timeout=120s
                    '''
                }
            }
        }
    }

    post {
        success { echo "Deployed ${IMAGE_NAME}:${IMAGE_TAG} successfully" }
        failure { echo 'Pipeline failed - check the logs' }
    }
}
